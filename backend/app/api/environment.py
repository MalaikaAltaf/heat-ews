from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Site, EnvironmentRecord, User
from app.api.deps import get_current_user, verify_site_access
from app.services.weather_service import fetch_open_meteo_data, sync_site_environmental_data, get_latest_site_environment
from app.analytics.heat_index import check_mohre_midday_break
from app.analytics.fusion import evaluate_site_risk

router = APIRouter(prefix="/environment", tags=["Environment"])


@router.get("/{site_id}/current")
def get_current_environment(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    verify_site_access(site_id, current_user)
    latest = get_latest_site_environment(db, site_id)
    mohre = check_mohre_midday_break()

    return {
        "site_id": site_id,
        "environment": latest,
        "mohre_break": mohre
    }


@router.get("/{site_id}/forecast")
def get_forecast(
    site_id: str,
    hours: int = 72,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    verify_site_access(site_id, current_user)
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc + timedelta(hours=hours)

    records = db.query(EnvironmentRecord).filter(
        EnvironmentRecord.site_id == site_id,
        EnvironmentRecord.valid_at >= now_utc,
        EnvironmentRecord.valid_at <= cutoff
    ).order_by(EnvironmentRecord.valid_at.asc()).all()

    return [
        {
            "valid_at": r.valid_at.isoformat(),
            "temperature_c": r.temperature_c,
            "humidity_pct": r.humidity_pct,
            "pm25": r.pm25,
            "heat_index_c": r.heat_index_c,
            "is_forecast": r.is_forecast
        }
        for r in records
    ]


@router.post("/{site_id}/sync")
async def sync_environment(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Fetches real-time environmental data from Open-Meteo, saves hourly records to DB,
    and runs the risk fusion engine to update site tier.
    """
    site = db.query(Site).filter(Site.site_id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found.")

    verify_site_access(site_id, current_user)

    data = await fetch_open_meteo_data(site.latitude, site.longitude)
    if not data:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve weather from Open-Meteo provider. Using cached observations."
        )

    records_saved = sync_site_environmental_data(db, site, data)
    eval_result = evaluate_site_risk(db, site_id)

    return {
        "success": True,
        "records_synced": records_saved,
        "risk_evaluation": eval_result
    }

