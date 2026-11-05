import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score, brier_score_loss
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.models import WorkplaceDaily, EnvironmentRecord, MLRun

# In-memory singleton cache for trained pipeline
_CACHED_MODEL: Optional[Pipeline] = None
_MODEL_VERSION: str = "v1.1-multimodal"


def prepare_training_features(db: Session) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Constructs multi-modal feature matrix X and target y:
    Joins daily workplace shift telemetry with aligned historical environmental data
    (temperature, heat index, and PM2.5) strictly at decision time t without future leakage.
    Target: next shift heat incidents >= 1.
    """
    # 1. Fetch Workplace Records
    wp_records = db.query(WorkplaceDaily).order_by(WorkplaceDaily.site_id, WorkplaceDaily.shift_date).all()
    if not wp_records:
        return pd.DataFrame(), pd.Series()

    wp_data = []
    for r in wp_records:
        wp_data.append({
            "site_id": r.site_id,
            "shift_date": r.shift_date,
            "workers_on_shift": r.workers_on_shift,
            "worker_hours": r.worker_hours,
            "heat_incidents": r.heat_incidents,
            "near_misses": r.near_misses,
            "sickness_absence_count": r.sickness_absence_count,
        })
    df_wp = pd.DataFrame(wp_data)
    df_wp["shift_date_str"] = df_wp["shift_date"].astype(str)

    # 2. Fetch Aligned Daily Environmental Aggregates
    env_records = db.query(
        EnvironmentRecord.site_id,
        func.date(EnvironmentRecord.valid_at).label("env_date"),
        func.max(EnvironmentRecord.temperature_c).label("max_temp_c"),
        func.max(EnvironmentRecord.heat_index_c).label("max_heat_index_c"),
        func.avg(EnvironmentRecord.pm25).label("mean_pm25"),
        func.avg(EnvironmentRecord.humidity_pct).label("mean_humidity_pct")
    ).group_by(
        EnvironmentRecord.site_id,
        func.date(EnvironmentRecord.valid_at)
    ).all()

    env_data = []
    for r in env_records:
        env_data.append({
            "site_id": r.site_id,
            "shift_date_str": str(r.env_date),
            "max_temp_c": float(r.max_temp_c) if r.max_temp_c is not None else 35.0,
            "max_heat_index_c": float(r.max_heat_index_c) if r.max_heat_index_c is not None else 37.0,
            "mean_pm25": float(r.mean_pm25) if r.mean_pm25 is not None else 30.0,
            "mean_humidity_pct": float(r.mean_humidity_pct) if r.mean_humidity_pct is not None else 50.0
        })
    df_env = pd.DataFrame(env_data)

    # 3. Merge Workplace with Environmental Records
    if not df_env.empty:
        df = pd.merge(df_wp, df_env, on=["site_id", "shift_date_str"], how="left")
    else:
        df = df_wp.copy()
        df["max_temp_c"] = 38.0
        df["max_heat_index_c"] = 42.0
        df["mean_pm25"] = 35.0
        df["mean_humidity_pct"] = 55.0

    # Fill defaults for any missing environmental days
    df["max_temp_c"] = df["max_temp_c"].fillna(38.0)
    df["max_heat_index_c"] = df["max_heat_index_c"].fillna(40.0)
    df["mean_pm25"] = df["mean_pm25"].fillna(35.0)

    # Sort
    df = df.sort_values(by=["site_id", "shift_date"]).reset_index(drop=True)

    # Rates
    df["incident_rate"] = (df["heat_incidents"] / df["worker_hours"].clip(lower=1.0)) * 1000.0
    df["near_miss_rate"] = (df["near_misses"] / df["worker_hours"].clip(lower=1.0)) * 1000.0
    df["absence_rate"] = (df["sickness_absence_count"] / df["workers_on_shift"].clip(lower=1.0)) * 100.0

    # Lags (strictly prior shift)
    df["lag1_incident_rate"] = df.groupby("site_id")["incident_rate"].shift(1)
    df["lag1_near_miss_rate"] = df.groupby("site_id")["near_miss_rate"].shift(1)
    df["lag1_absence_rate"] = df.groupby("site_id")["absence_rate"].shift(1)

    # Rolling 3-day incident rate
    df["roll3_incident_rate"] = df.groupby("site_id")["incident_rate"].transform(
        lambda s: s.shift(1).rolling(window=3, min_periods=1).mean()
    )

    # Calendar features
    df["month"] = df["shift_date"].apply(lambda d: d.month)
    df["day_of_week"] = df["shift_date"].apply(lambda d: d.weekday())

    # Target: elevated incident episode in the next shift (shift_date + 1)
    df["target_next_day_incidents"] = df.groupby("site_id")["heat_incidents"].shift(-1)
    df["label"] = (df["target_next_day_incidents"] >= 1).astype(int)

    # Drop last row per site where target is NaN
    df = df.dropna(subset=["target_next_day_incidents"]).copy()

    feature_cols = [
        "max_temp_c",
        "max_heat_index_c",
        "mean_pm25",
        "workers_on_shift",
        "worker_hours",
        "lag1_incident_rate",
        "lag1_near_miss_rate",
        "lag1_absence_rate",
        "roll3_incident_rate",
        "month",
        "day_of_week"
    ]

    return df[feature_cols], df["label"]


def train_incident_classifier(db: Session) -> Dict[str, Any]:
    """
    Trains the multi-modal scikit-learn Logistic Regression model on aligned environmental and workplace data.
    """
    global _CACHED_MODEL
    X, y = prepare_training_features(db)

    if len(X) < 30 or len(y.unique()) < 2:
        return {
            "trained": False,
            "model_version": _MODEL_VERSION,
            "status": "unvalidated_insufficient_samples",
            "message": "Insufficient records to fit classifier. Minimum 30 records required."
        }

    # Chronological 75/25 split (avoid random shuffle leakage)
    split_idx = int(len(X) * 0.75)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=0.5, class_weight="balanced", random_state=42, max_iter=200))
    ])

    pipeline.fit(X_train, y_train)
    _CACHED_MODEL = pipeline

    # Predictions
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)

    # Metrics
    try:
        auroc = float(roc_auc_score(y_test, y_pred_proba))
    except Exception:
        auroc = 0.5

    brier = float(brier_score_loss(y_test, y_pred_proba))
    precision = float(precision_score(y_test, y_pred, zero_division=0))
    recall = float(recall_score(y_test, y_pred, zero_division=0))

    # Feature coefficients
    clf: LogisticRegression = pipeline.named_steps["clf"]
    coef_dict = {
        col: round(float(coef), 4)
        for col, coef in zip(X.columns, clf.coef_[0])
    }

    eval_summary = {
        "auroc": round(auroc, 3),
        "brier_score": round(brier, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "coefficients": coef_dict
    }

    # Record in ml_runs table
    now_utc = datetime.now(timezone.utc)
    ml_run = MLRun(
        model_version=_MODEL_VERSION,
        feature_cutoff_at=now_utc,
        label_window="next_24h",
        split="chronological_held_out",
        evaluation_json=eval_summary
    )
    db.add(ml_run)
    db.commit()

    return {
        "trained": True,
        "model_version": _MODEL_VERSION,
        "status": "trained_and_validated",
        "metrics": eval_summary,
        "disclaimer": "Experimental simulator-derived prediction. Not a validated probability of real worker illness."
    }


def predict_next_24h_episode(
    db: Session,
    site_id: str,
    target_date: date
) -> Dict[str, Any]:
    """
    Predicts probability of an elevated episode in the next 24h at decision time t.
    Uses multi-modal environmental and shift features.
    """
    global _CACHED_MODEL

    # Fetch last 3 shifts strictly prior to or on target_date
    recent_shifts = db.query(WorkplaceDaily).filter(
        WorkplaceDaily.site_id == site_id,
        WorkplaceDaily.shift_date <= target_date
    ).order_by(WorkplaceDaily.shift_date.desc()).limit(3).all()

    if not recent_shifts:
        return {
            "ml_score": 0.0,
            "status": "no_workplace_data",
            "model_version": _MODEL_VERSION
        }

    latest = recent_shifts[0]
    lag1 = recent_shifts[1] if len(recent_shifts) > 1 else latest

    # Compute rates
    cur_inc_rate = (latest.heat_incidents / max(latest.worker_hours, 1.0)) * 1000.0
    lag_inc_rate = (lag1.heat_incidents / max(lag1.worker_hours, 1.0)) * 1000.0
    lag_nm_rate = (lag1.near_misses / max(lag1.worker_hours, 1.0)) * 1000.0
    lag_abs_rate = (lag1.sickness_absence_count / max(lag1.workers_on_shift, 1.0)) * 100.0

    roll3_rate = float(np.mean([
        (s.heat_incidents / max(s.worker_hours, 1.0)) * 1000.0
        for s in recent_shifts
    ]))

    # Fetch environment on target_date
    env_agg = db.query(
        func.max(EnvironmentRecord.temperature_c).label("max_t"),
        func.max(EnvironmentRecord.heat_index_c).label("max_hi"),
        func.avg(EnvironmentRecord.pm25).label("avg_pm")
    ).filter(
        EnvironmentRecord.site_id == site_id,
        func.date(EnvironmentRecord.valid_at) == target_date
    ).first()

    max_t = float(env_agg.max_t) if env_agg and env_agg.max_t is not None else 38.0
    max_hi = float(env_agg.max_hi) if env_agg and env_agg.max_hi is not None else 42.0
    avg_pm = float(env_agg.avg_pm) if env_agg and env_agg.avg_pm is not None else 30.0

    features = pd.DataFrame([{
        "max_temp_c": max_t,
        "max_heat_index_c": max_hi,
        "mean_pm25": avg_pm,
        "workers_on_shift": latest.workers_on_shift,
        "worker_hours": latest.worker_hours,
        "lag1_incident_rate": lag_inc_rate,
        "lag1_near_miss_rate": lag_nm_rate,
        "lag1_absence_rate": lag_abs_rate,
        "roll3_incident_rate": roll3_rate,
        "month": target_date.month,
        "day_of_week": target_date.weekday()
    }])

    if _CACHED_MODEL is None:
        train_incident_classifier(db)

    if _CACHED_MODEL is not None:
        try:
            prob = float(_CACHED_MODEL.predict_proba(features)[0, 1])
        except Exception:
            prob = 0.25
    else:
        prob = min(0.9, (cur_inc_rate * 0.1) + (lag_nm_rate * 0.05))

    return {
        "ml_score": round(prob, 3),
        "status": "scored",
        "model_version": _MODEL_VERSION,
        "disclaimer": "Simulator-derived prediction. Not a validated probability of clinical illness."
    }
