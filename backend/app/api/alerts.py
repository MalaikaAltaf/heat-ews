from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Alert, User
from app.api.deps import get_current_user, require_user
from app.services.alert_service import get_playbook_for_tier, acknowledge_alert, log_preventive_action

router = APIRouter(prefix="/alerts", tags=["Alerts & Decisions"])


class ActionLogRequest(BaseModel):
    action_code: str
    feedback: Optional[str] = None


@router.get("")
def list_alerts(
    site_id: Optional[str] = None,
    tier: Optional[str] = None,
    unacknowledged_only: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    query = db.query(Alert)

    # Scoping for HSE Officer
    if current_user and current_user.role == "hse_officer" and current_user.permitted_site_id:
        query = query.filter(Alert.site_id == current_user.permitted_site_id)
    elif site_id:
        query = query.filter(Alert.site_id == site_id)

    if tier:
        query = query.filter(Alert.tier == tier)

    if unacknowledged_only:
        query = query.filter(Alert.acknowledged_at == None)

    alerts = query.order_by(Alert.issued_at.desc()).limit(50).all()

    return [
        {
            "alert_id": a.alert_id,
            "site_id": a.site_id,
            "tier": a.tier,
            "issued_at": a.issued_at.isoformat(),
            "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
            "acknowledged_by": a.acknowledged_by,
            "action_code": a.action_code,
            "action_time": a.action_time.isoformat() if a.action_time else None,
            "feedback": a.feedback,
            "evidence": a.evidence_json,
            "playbook": get_playbook_for_tier(a.tier)
        }
        for a in alerts
    ]


@router.get("/{alert_id}")
def get_alert_detail(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")

    return {
        "alert_id": alert.alert_id,
        "site_id": alert.site_id,
        "tier": alert.tier,
        "issued_at": alert.issued_at.isoformat(),
        "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        "acknowledged_by": alert.acknowledged_by,
        "action_code": alert.action_code,
        "action_time": alert.action_time.isoformat() if alert.action_time else None,
        "feedback": alert.feedback,
        "evidence": alert.evidence_json,
        "playbook": get_playbook_for_tier(alert.tier)
    }


@router.post("/{alert_id}/acknowledge")
def acknowledge(
    alert_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    alert = acknowledge_alert(db, alert_id, user.username, user.role)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return {
        "success": True,
        "alert_id": alert.alert_id,
        "acknowledged_at": alert.acknowledged_at.isoformat(),
        "acknowledged_by": alert.acknowledged_by
    }


@router.post("/{alert_id}/action")
def log_action(
    alert_id: str,
    action_data: ActionLogRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    alert = log_preventive_action(
        db,
        alert_id,
        action_data.action_code,
        action_data.feedback,
        user.username,
        user.role
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return {
        "success": True,
        "alert_id": alert.alert_id,
        "action_code": alert.action_code,
        "action_time": alert.action_time.isoformat(),
        "feedback": alert.feedback
    }

