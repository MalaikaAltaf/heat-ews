import pytest
from datetime import datetime, date, timedelta, timezone
from app.analytics.fusion import evaluate_site_risk
from app.db.models import Site, EnvironmentRecord, WorkplaceDaily, Alert


def test_ml_score_alone_cannot_trigger_action_tier(db):
    """
    SRS FUS-02 & Section 7.4:
    'The model score alone must never issue an Action. Safety rules may prompt heat precautions regardless of ML score.'
    """
    # Evaluate a site on a date where environmental heat is mild (<35C)
    # Even if ML model predicts high likelihood, Action tier must NOT be issued.
    mild_dt = datetime(2026, 6, 2, 8, 0, tzinfo=timezone.utc)
    res = evaluate_site_risk(db, "AD_SITE_01", target_dt=mild_dt)

    assert res["tier"] != "Action", (
        f"Safety Invariant Violated! ML score or mild conditions triggered Action tier: {res['tier']}"
    )


def test_missing_workplace_feed_caps_tier_at_advisory():
    """
    SRS FUS-02 & Scenario S5:
    'Missing workplace feed: maximum Advisory; missing environmental feed: no new Action; all feeds stale: Degraded/Unavailable'
    """
    # From S5 evaluation in evaluator:
    from app.validation.evaluator import evaluate_all_scenarios
    eval_report = evaluate_all_scenarios()
    s5_result = next((s for s in eval_report["scenarios"] if s["scenario_id"] == "S5"), None)

    assert s5_result is not None
    # S5 has severe heat (temp=47C) but workplace feed is MISSING.
    # Tier must be capped at Advisory maximum!
    assert s5_result["multi_signal"]["tier"] == "Advisory"
    assert "workplace feed missing" in s5_result["multi_signal"]["tier_cap"].lower()


def test_stale_environmental_feed_blocks_unsupported_action():
    """
    SRS Scenario S6:
    'S6: Stale environmental provider - Cached last-known data labeled stale; no unsupported new Action'
    """
    from app.validation.evaluator import evaluate_all_scenarios
    eval_report = evaluate_all_scenarios()
    s6_result = next((s for s in eval_report["scenarios"] if s["scenario_id"] == "S6"), None)

    assert s6_result is not None
    assert s6_result["multi_signal"]["tier"] != "Action"
    assert "stale" in s6_result["multi_signal"]["tier_cap"].lower()


def test_all_feeds_missing_displays_degraded_not_safe(db):
    """
    SRS Section 7.4 & 7.5:
    'Missing workplace feed: maximum Advisory; missing environmental feed: no new Action;
     all feeds stale: show Degraded/Unavailable, not a reassuring green Safe state.'
    """
    # Test a site timestamp in the far future where no feeds exist
    future_dt = datetime(2099, 1, 1, 12, 0, tzinfo=timezone.utc)
    res = evaluate_site_risk(db, "AD_SITE_01", target_dt=future_dt)

    assert res["tier"] == "Degraded"
    assert len(res["evidence"]["quality_flags"]) > 0
    assert any("missing" in flag or "stale" in flag for flag in res["evidence"]["quality_flags"])
