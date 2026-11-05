from typing import Optional, List
from datetime import datetime, date, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import numpy as np
from app.db.session import get_db
from app.db.models import Site, WorkplaceDaily, User
from app.api.deps import get_current_user, verify_site_access
from app.services.csv_service import validate_and_parse_csv
from app.core.privacy import apply_privacy_to_workplace_dict
from app.analytics.fusion import evaluate_site_risk

router = APIRouter(prefix="/workplace", tags=["Workplace Shifts"])


@router.post("/upload")
async def upload_workplace_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Uploads aggregated workplace CSV feed.
    Strictly validates against prohibited individual identifiers (PRV-01) and impossible ratios (ING-02).
    Automatically triggers risk re-evaluation across affected sites.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    try:
        content_str = contents.decode("utf-8")
    except UnicodeDecodeError:
        content_str = contents.decode("latin-1")

    res = validate_and_parse_csv(content_str, db)
    if not res["success"]:
        return {
            "success": False,
            "errors": res["errors"],
            "rows_imported": 0
        }

    # Re-evaluate all pilot sites after new data upload
    sites = db.query(Site).all()
    eval_summaries = {}
    for s in sites:
        eval_summaries[s.site_id] = evaluate_site_risk(db, s.site_id)

    return {
        "success": True,
        "rows_imported": res["rows_imported"],
        "evaluations_updated": eval_summaries
    }


@router.get("/{site_id}/history")
def get_workplace_history(
    site_id: str,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    verify_site_access(site_id, current_user)

    records = db.query(WorkplaceDaily).filter(
        WorkplaceDaily.site_id == site_id
    ).order_by(WorkplaceDaily.shift_date.desc()).limit(days).all()

    # Determine if outward privacy suppression should be applied
    is_public = (current_user is None) or (current_user.role == "public_health_viewer")

    sanitized_records = []
    for r in records:
        raw_dict = {
            "shift_date": r.shift_date.isoformat(),
            "workers_on_shift": r.workers_on_shift,
            "worker_hours": r.worker_hours,
            "heat_incidents": r.heat_incidents,
            "near_misses": r.near_misses,
            "sickness_absence_count": r.sickness_absence_count,
            "synthetic_flag": r.synthetic_flag,
            "received_at": r.received_at.isoformat()
        }
        sanitized_records.append(apply_privacy_to_workplace_dict(raw_dict, is_public_or_export=is_public))

    return {
        "site_id": site_id,
        "privacy_suppression_active": is_public,
        "records": sanitized_records
    }


@router.get("/{site_id}/analytics")
def get_workplace_analytics(
    site_id: str,
    days: int = 30,
    k_slack: float = 0.5,
    h_threshold: float = 3.0,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Returns chronological shift telemetry joined with rolling 14-day baselines and CUSUM excursion scores.
    Powers the dynamic Analytics and Overview telemetry charts directly from PostgreSQL.
    """
    verify_site_access(site_id, current_user)

    records = db.query(WorkplaceDaily).filter(
        WorkplaceDaily.site_id == site_id
    ).order_by(WorkplaceDaily.shift_date.asc()).all()

    if not records:
        return {"site_id": site_id, "series": []}

    series = []
    raw_rates = [
        (r.heat_incidents / max(r.worker_hours, 1.0)) * 1000.0
        for r in records
    ]

    mean_base = float(np.mean(raw_rates[:14])) if len(raw_rates) >= 14 else 1.0
    std_base = float(np.std(raw_rates[:14])) if len(raw_rates) >= 14 and np.std(raw_rates[:14]) > 0.05 else 0.5

    s_cusum = 0.0

    for i, r in enumerate(records):
        inc_rate = raw_rates[i]
        nm_rate = (r.near_misses / max(r.worker_hours, 1.0)) * 1000.0

        # Rolling 14-day baseline prior to this shift (strictly past observations)
        if i >= 14:
            window = raw_rates[i - 14:i]
            cur_base = float(np.mean(window))
            cur_std = float(np.std(window)) if np.std(window) > 0.05 else 0.5
        else:
            cur_base = mean_base
            cur_std = std_base

        z = (inc_rate - cur_base) / cur_std
        s_cusum = max(0.0, s_cusum + z - k_slack)

        series.append({
            "shift_date": r.shift_date.isoformat(),
            "day": r.shift_date.strftime("%d %b"),
            "incidentRate": round(inc_rate, 2),
            "baseline": round(cur_base, 2),
            "cusum": round(s_cusum, 2),
            "nearMisses": r.near_misses,
            "workers": r.workers_on_shift,
            "is_anomaly": s_cusum >= h_threshold
        })

    # Return last N days
    return {
        "site_id": site_id,
        "k_slack": k_slack,
        "h_threshold": h_threshold,
        "series": series[-days:]
    }
