from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.db.models import Alert, AuditLog, Site

PLAYBOOK_TIERS = {
    "Watch": {
        "title": "Level 1: Watch (Precautionary Surveillance)",
        "owner": "HSE Officer",
        "recommended_response": "Check water stations, inspect shaded areas, review forecast, and increase site monitoring.",
        "actions": [
            {"code": "ACT_INSPECT_SHADE", "label": "Inspect and verify shaded resting zones"},
            {"code": "ACT_RESTOCK_HYDRATION", "label": "Verify cool water and electrolyte supply"},
            {"code": "ACT_SUPERVISOR_ALERT", "label": "Alert site supervisors to watch for heat fatigue"}
        ],
        "urgency": "Review within 2 hours"
    },
    "Advisory": {
        "title": "Level 2: Advisory (Targeted Mitigation)",
        "owner": "HSE Officer + Operations Lead",
        "recommended_response": "Plan extra shaded rest breaks, enforce hydration schedules, re-time non-urgent heavy tasks, and conduct supervisor briefings.",
        "actions": [
            {"code": "ACT_MANDATORY_BREAKS", "label": "Mandate additional 15-minute shaded breaks every hour"},
            {"code": "ACT_ENFORCE_HYDRATION", "label": "Broadcast mandatory hydration reminders"},
            {"code": "ACT_RETIME_TASKS", "label": "Reschedule high-exertion manual labor away from peak heat"},
            {"code": "ACT_MOHRE_COMPLIANCE", "label": "Enforce MOHRE midday break (12:30-15:00) readiness"}
        ],
        "urgency": "Action required within 45 minutes"
    },
    "Action": {
        "title": "Level 3: Action (Urgent Intervention)",
        "owner": "Operations Lead / HSE Officer",
        "recommended_response": "Urgent review of heavy-work timing, cooling access, and work-rest cycles; consider pausing high-exposure outdoor tasks subject to qualified local safety policy.",
        "actions": [
            {"code": "ACT_PAUSE_HIGH_EXPOSURE", "label": "Pause high-exposure outdoor tasks under direct sun"},
            {"code": "ACT_ROTATE_CREWS", "label": "Immediate crew rotation to air-conditioned rest areas"},
            {"code": "ACT_HEAT_FATIGUE_SCREEN", "label": "Conduct immediate physical heat fatigue triage on shift"},
            {"code": "ACT_EMERGENCY_COOLING", "label": "Deploy misting stations and emergency cold-water immersion packs"}
        ],
        "urgency": "Immediate action required (under 15 minutes)"
    }
}


def get_playbook_for_tier(tier: str) -> Dict[str, Any]:
    return PLAYBOOK_TIERS.get(tier, {
        "title": f"Tier: {tier}",
        "owner": "HSE Officer",
        "recommended_response": "Standard site safety protocols apply.",
        "actions": [],
        "urgency": "Standard monitoring"
    })


def acknowledge_alert(db: Session, alert_id: str, user_id: str, role: str) -> Optional[Alert]:
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        return None

    now_utc = datetime.now(timezone.utc)
    alert.acknowledged_at = now_utc
    alert.acknowledged_by = user_id

    # Log to audit trail
    audit = AuditLog(
        user_id=user_id,
        role=role,
        action="acknowledge_alert",
        object_id=alert_id,
        details={"tier": alert.tier, "site_id": alert.site_id},
        timestamp=now_utc
    )
    db.add(audit)
    db.commit()
    db.refresh(alert)
    return alert


def log_preventive_action(
    db: Session,
    alert_id: str,
    action_code: str,
    feedback: Optional[str],
    user_id: str,
    role: str
) -> Optional[Alert]:
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        return None

    now_utc = datetime.now(timezone.utc)
    alert.action_code = action_code
    alert.action_time = now_utc
    alert.feedback = feedback

    # Log to audit trail
    audit = AuditLog(
        user_id=user_id,
        role=role,
        action="log_preventive_action",
        object_id=alert_id,
        details={
            "action_code": action_code,
            "feedback": feedback,
            "site_id": alert.site_id,
            "tier": alert.tier
        },
        timestamp=now_utc
    )
    db.add(audit)
    db.commit()
    db.refresh(alert)
    return alert

