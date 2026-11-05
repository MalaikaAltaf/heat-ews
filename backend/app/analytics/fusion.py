from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import Site, EnvironmentRecord, WorkplaceDaily, RiskEvaluation, Alert
from app.analytics.anomaly import compute_site_workplace_anomaly
from app.analytics.ml_model import predict_next_24h_episode
from app.analytics.heat_index import check_mohre_midday_break
from app.core.config import settings


def evaluate_site_risk(
    db: Session,
    site_id: str,
    target_dt: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Fuses environmental exposure, statistical workplace anomaly, and ML signals into tiered alerts.
    Enforces strict safety invariants (SRS 7.4):
    1. ML score alone must NEVER issue an Action.
    2. Missing workplace feed caps tier at Advisory maximum.
    3. Missing environmental feed blocks any new Action tier.
    4. All stale/missing feeds output 'Degraded/Unavailable' (never a false 'Normal/Safe').
    5. Cooldown window deduplication prevents repetitive alert spam.
    """
    if target_dt is None:
        target_dt = datetime.now(timezone.utc)
    target_date = target_dt.date()

    # 1. Fetch Latest Environmental Record at or before target_dt
    latest_env = db.query(EnvironmentRecord).filter(
        EnvironmentRecord.site_id == site_id,
        EnvironmentRecord.valid_at <= target_dt
    ).order_by(EnvironmentRecord.valid_at.desc()).first()

    # 2. Check Environmental Freshness & Quality
    env_present = latest_env is not None
    env_stale = False
    env_age_hours = 0.0

    if env_present:
        env_age_hours = (target_dt - latest_env.received_at).total_seconds() / 3600.0
        env_stale = env_age_hours > 3.0

    temp_c = latest_env.temperature_c if env_present else None
    hum_pct = latest_env.humidity_pct if env_present else None
    pm25 = latest_env.pm25 if env_present else None
    heat_index = latest_env.heat_index_c if env_present else None

    # Environmental Signal (0.0 to 1.0)
    # NOAA Heat Index: >40C is severe, >35C is elevated
    heat_signal = 0.0
    if heat_index is not None:
        if heat_index >= 45.0:
            heat_signal = 1.0
        elif heat_index >= 40.0:
            heat_signal = 0.8
        elif heat_index >= 35.0:
            heat_signal = 0.5
        elif heat_index >= 30.0:
            heat_signal = 0.2
    elif temp_c is not None:
        if temp_c >= 45.0:
            heat_signal = 0.9
        elif temp_c >= 40.0:
            heat_signal = 0.6
        elif temp_c >= 35.0:
            heat_signal = 0.3

    # PM2.5 Signal (0.0 to 1.0): WHO 24h guideline is 15 ug/m3, >50 elevated, >150 severe dust
    pm25_signal = 0.0
    if pm25 is not None:
        if pm25 >= 150.0:
            pm25_signal = 1.0
        elif pm25 >= 75.0:
            pm25_signal = 0.7
        elif pm25 >= 35.0:
            pm25_signal = 0.4
        elif pm25 >= 15.0:
            pm25_signal = 0.2

    # 3. Compute Workplace Statistical Anomaly
    workplace_res = compute_site_workplace_anomaly(db, site_id, target_date)
    workplace_present = workplace_res["has_data"]
    workplace_signal = workplace_res.get("anomaly_score", 0.0)
    workplace_anomaly = workplace_res.get("is_anomaly", False)

    # 4. Supervised ML Score
    ml_res = predict_next_24h_episode(db, site_id, target_date)
    ml_score = ml_res.get("ml_score", 0.0)

    # 5. Composite Heuristic (for comparative ranking, unvalidated until tested)
    composite_score = round(
        (0.40 * heat_signal) + (0.20 * pm25_signal) + (0.40 * workplace_signal),
        3
    )

    # 6. Safety Gating & Tier Assignment
    quality_flags = []
    tier_cap_reason = None

    if not env_present and not workplace_present:
        tier = "Degraded"
        quality_flags.append("all_feeds_missing")
        tier_cap_reason = "No data feeds available for site. Reporting Degraded state."
    elif env_stale and not workplace_present:
        tier = "Degraded"
        quality_flags.append("environmental_stale_workplace_missing")
        tier_cap_reason = "Environmental feed is stale and workplace feed is missing."
    else:
        # Determine raw suggested tier
        # Action: Requires high corroboration (high environmental exposure + workplace anomaly or elevated near misses)
        if (heat_signal >= 0.7 or pm25_signal >= 0.7) and (workplace_anomaly or workplace_signal >= 0.5):
            raw_tier = "Action"
        elif (heat_signal >= 0.5 or pm25_signal >= 0.5) and (workplace_signal >= 0.3 or ml_score >= 0.6):
            raw_tier = "Advisory"
        elif heat_signal >= 0.5 or pm25_signal >= 0.5 or workplace_anomaly or ml_score >= 0.5:
            raw_tier = "Watch"
        else:
            raw_tier = "Normal"

        tier = raw_tier

        # Invariant 1: ML alone cannot trigger Action
        if raw_tier == "Action" and not workplace_anomaly and heat_signal < 0.7:
            tier = "Advisory"
            tier_cap_reason = "Action tier downgraded to Advisory: ML score alone cannot issue Action."
            quality_flags.append("action_downgraded_ml_only")

        # Invariant 2: Missing workplace feed caps at Advisory
        if not workplace_present:
            quality_flags.append("missing_workplace_feed")
            if tier == "Action":
                tier = "Advisory"
                tier_cap_reason = "Action tier capped at Advisory: workplace feed missing."

        # Invariant 3: Missing/stale environmental feed blocks new Action
        if not env_present or env_stale:
            quality_flags.append("environmental_feed_stale_or_missing")
            if tier == "Action":
                tier = "Advisory"
                tier_cap_reason = "Action tier capped at Advisory: environmental data is stale or missing."

    # 7. Check UAE MOHRE Midday Break Context
    mohre_info = check_mohre_midday_break(target_dt)

    # 8. Check Cooldown Deduplication
    cooldown_cutoff = target_dt - timedelta(hours=settings.ALERT_COOLDOWN_HOURS)
    recent_alert = db.query(Alert).filter(
        Alert.site_id == site_id,
        Alert.tier == tier,
        Alert.issued_at >= cooldown_cutoff
    ).first()

    should_issue_alert = (tier in ["Watch", "Advisory", "Action"]) and (recent_alert is None)

    # 9. Build Evidence Card Payload
    site_obj = db.query(Site).filter(Site.site_id == site_id).first()
    evidence_payload = {
        "site_id": site_id,
        "site_name": site_obj.pseudonym if site_obj else site_id,
        "region": site_obj.region if site_obj else "Abu Dhabi",
        "timestamp": target_dt.isoformat(),
        "tier": tier,
        "tier_cap_reason": tier_cap_reason,
        "quality_flags": quality_flags,
        "measurements": {
            "temperature_c": temp_c,
            "humidity_pct": hum_pct,
            "heat_index_c": heat_index,
            "pm25": pm25,
            "data_age_hours": round(env_age_hours, 1) if env_present else None,
            "is_stale": env_stale
        },
        "workplace_signals": workplace_res.get("contributing_signals", {}),
        "statistical_baseline": {
            "cusum_s": workplace_res.get("cusum_s"),
            "z_score": workplace_res.get("z_score"),
            "mean_rate": workplace_res.get("baseline_mean_rate"),
            "baseline_days": workplace_res.get("baseline_period_days")
        },
        "ml_classifier": {
            "ml_score": ml_score,
            "model_version": ml_res.get("model_version"),
            "disclaimer": "Experimental simulator prediction, not a certified clinical probability."
        },
        "mohre_break": mohre_info,
        "assumptions": [
            "Data reflects synthetic workplace shifts and Open-Meteo environmental models.",
            "Alerts are decision-support recommendations, not automated medical determinations.",
            "UAE MOHRE midday-break notices are informational safeguards."
        ]
    }

    # Save Risk Evaluation to DB
    risk_record = RiskEvaluation(
        site_id=site_id,
        evaluated_at=target_dt,
        heat_signal=heat_signal,
        pm25_signal=pm25_signal,
        workplace_signal=workplace_signal,
        score=composite_score,
        ml_score=ml_score,
        model_version=ml_res.get("model_version"),
        tier=tier,
        quality_flags={"flags": quality_flags, "tier_cap_reason": tier_cap_reason},
        config_version="1.0.0"
    )
    db.add(risk_record)

    # Create Alert if applicable and not in cooldown
    new_alert_id = None
    if should_issue_alert:
        alert = Alert(
            site_id=site_id,
            tier=tier,
            issued_at=target_dt,
            evidence_json=evidence_payload
        )
        db.add(alert)
        db.flush()
        new_alert_id = alert.alert_id

    db.commit()

    return {
        "site_id": site_id,
        "tier": tier,
        "score": composite_score,
        "ml_score": ml_score,
        "heat_signal": heat_signal,
        "pm25_signal": pm25_signal,
        "workplace_signal": workplace_signal,
        "alert_issued": should_issue_alert,
        "alert_id": new_alert_id,
        "cooldown_active": recent_alert is not None,
        "evidence": evidence_payload
    }

