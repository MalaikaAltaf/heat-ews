import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import WorkplaceDaily
from app.core.config import settings


def compute_site_workplace_anomaly(
    db: Session,
    site_id: str,
    target_date: date,
    k_slack: float = 0.5,
    h_threshold: float = 3.0,
    baseline_days: int = 14
) -> Dict[str, Any]:
    """
    Computes statistical anomaly detection on workplace shift event rates (SRS DET-01, DET-02, DET-03).
    Uses strictly past 7-14 shift days prior to target_date to avoid any temporal look-ahead leakage.
    Applies rate standardization and one-sided CUSUM: S[t] = max(0, S[t-1] + z[t] - k).
    """
    # 1. Fetch historical baseline shifts strictly before target_date
    start_date = target_date - timedelta(days=baseline_days + 14)  # Fetch extra to ensure at least baseline_days
    history = db.query(WorkplaceDaily).filter(
        WorkplaceDaily.site_id == site_id,
        WorkplaceDaily.shift_date < target_date,
        WorkplaceDaily.shift_date >= start_date
    ).order_by(WorkplaceDaily.shift_date.asc()).all()

    # 2. Fetch current observation
    current = db.query(WorkplaceDaily).filter(
        WorkplaceDaily.site_id == site_id,
        WorkplaceDaily.shift_date == target_date
    ).first()

    if not current:
        return {
            "has_data": False,
            "is_anomaly": False,
            "anomaly_score": 0.0,
            "message": "No workplace shift record for target date.",
            "quality_flag": "missing_workplace_record"
        }

    # Rates: per 1,000 worker hours
    current_incident_rate = (current.heat_incidents / max(current.worker_hours, 1.0)) * 1000.0
    current_near_miss_rate = (current.near_misses / max(current.worker_hours, 1.0)) * 1000.0
    current_absence_rate = (current.sickness_absence_count / max(current.workers_on_shift, 1.0)) * 100.0

    if len(history) < 5:
        # Short history: provisional baseline with reduced confidence
        return {
            "has_data": True,
            "is_anomaly": current.heat_incidents > 1,
            "anomaly_score": 0.3 if current.heat_incidents > 0 else 0.0,
            "z_score": 0.0,
            "cusum_s": 0.0,
            "current_incident_rate": round(current_incident_rate, 2),
            "baseline_mean_rate": round(current_incident_rate, 2),
            "baseline_period_days": len(history),
            "confidence": "provisional_low_history",
            "k_slack": k_slack,
            "h_threshold": h_threshold,
            "contributing_signals": {
                "incident_rate": round(current_incident_rate, 2),
                "near_miss_rate": round(current_near_miss_rate, 2),
                "absence_rate": round(current_absence_rate, 2)
            }
        }

    # Extract historical rates
    hist_incident_rates = [
        (h.heat_incidents / max(h.worker_hours, 1.0)) * 1000.0
        for h in history
    ]

    mean_rate = float(np.mean(hist_incident_rates))
    std_rate = float(np.std(hist_incident_rates))
    if std_rate < 0.05:
        std_rate = 0.5  # Prevent division by zero on zero-variance baseline

    # Compute rolling CUSUM sequence across history up to current
    s_cusum = 0.0
    all_rates = hist_incident_rates + [current_incident_rate]
    for rate in all_rates:
        z = (rate - mean_rate) / std_rate
        s_cusum = max(0.0, s_cusum + z - k_slack)

    current_z = (current_incident_rate - mean_rate) / std_rate
    is_anomaly = s_cusum >= h_threshold or current_z >= 2.5

    # Normalized workplace anomaly score in [0.0, 1.0]
    workplace_score = min(1.0, max(0.0, (s_cusum / (h_threshold * 1.5))))

    return {
        "has_data": True,
        "is_anomaly": is_anomaly,
        "anomaly_score": round(workplace_score, 3),
        "z_score": round(current_z, 2),
        "cusum_s": round(s_cusum, 2),
        "current_incident_rate": round(current_incident_rate, 2),
        "baseline_mean_rate": round(mean_rate, 2),
        "baseline_std_rate": round(std_rate, 2),
        "baseline_period_days": len(history),
        "confidence": "high" if len(history) >= 14 else "moderate",
        "k_slack": k_slack,
        "h_threshold": h_threshold,
        "contributing_signals": {
            "incident_rate": round(current_incident_rate, 2),
            "near_miss_rate": round(current_near_miss_rate, 2),
            "absence_rate": round(current_absence_rate, 2)
        }
    }

