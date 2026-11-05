from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Site, Alert, RiskEvaluation, User
from app.api.deps import get_current_user, verify_site_access
from app.services.weather_service import get_latest_site_environment

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.get("")
def list_sites(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Returns list of configured Abu Dhabi pilot sites with their current tier and environmental status.
    Applies server-side site scoping if authenticated as HSE Officer.
    """
    query = db.query(Site).filter(Site.is_active == True)

    # Scoping for HSE Officer
    if current_user and current_user.role == "hse_officer" and current_user.permitted_site_id:
        query = query.filter(Site.site_id == current_user.permitted_site_id)

    sites = query.all()
    results = []

    for site in sites:
        latest_eval = db.query(RiskEvaluation).filter(
            RiskEvaluation.site_id == site.site_id
        ).order_by(RiskEvaluation.evaluated_at.desc()).first()

        latest_env = get_latest_site_environment(db, site.site_id)

        active_alert = db.query(Alert).filter(
            Alert.site_id == site.site_id,
            Alert.acknowledged_at == None
        ).order_by(Alert.issued_at.desc()).first()

        results.append({
            "site_id": site.site_id,
            "pseudonym": site.pseudonym,
            "sector": site.sector,
            "region": site.region,
            "latitude": site.latitude,
            "longitude": site.longitude,
            "timezone": site.timezone,
            "current_tier": latest_eval.tier if latest_eval else "Normal",
            "composite_score": latest_eval.score if latest_eval else 0.0,
            "ml_score": latest_eval.ml_score if latest_eval else None,
            "has_open_alert": active_alert is not None,
            "open_alert_id": active_alert.alert_id if active_alert else None,
            "latest_environment": latest_env
        })

    return results


@router.get("/{site_id}")
def get_site_detail(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    verify_site_access(site_id, current_user)
    site = db.query(Site).filter(Site.site_id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found.")

    latest_eval = db.query(RiskEvaluation).filter(
        RiskEvaluation.site_id == site.site_id
    ).order_by(RiskEvaluation.evaluated_at.desc()).first()

    latest_env = get_latest_site_environment(db, site.site_id)

    return {
        "site_id": site.site_id,
        "pseudonym": site.pseudonym,
        "sector": site.sector,
        "region": site.region,
        "latitude": site.latitude,
        "longitude": site.longitude,
        "timezone": site.timezone,
        "current_tier": latest_eval.tier if latest_eval else "Normal",
        "composite_score": latest_eval.score if latest_eval else 0.0,
        "ml_score": latest_eval.ml_score if latest_eval else None,
        "latest_environment": latest_env
    }

