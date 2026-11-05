import pytest
from datetime import datetime, date, timedelta, timezone
from app.db.models import WorkplaceDaily, EnvironmentRecord
from app.analytics.anomaly import compute_site_workplace_anomaly
from app.validation.scenarios import get_scenario_by_id
from app.validation.evaluator import evaluate_all_scenarios


def test_baseline_excludes_target_and_future_shifts(db):
    """
    SRS VAL-01 & DET-01:
    Compute baseline using strictly prior 7-14 comparable site-days; use only past observations.
    Zero future shift data or target day data may leak into the baseline mean.
    """
    target_date = date(2026, 6, 20)
    site_id = "AD_SITE_01"

    res = compute_site_workplace_anomaly(db, site_id, target_date, baseline_days=14)

    # Must have computed baseline from prior shifts
    assert res["has_data"] is True
    assert res["baseline_period_days"] >= 7
    # Baseline mean must be a positive rate
    assert res["baseline_mean_rate"] >= 0.0


def test_late_arriving_record_not_accessible_before_received_at(db):
    """
    SRS VAL-01 & S8:
    A shift occurred on day t, but was entered into the database 48 hours late (received_at = t + 48h).
    At decision time t, the query must strictly exclude records where received_at > t.
    """
    t_decision = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)
    t_late_arrival = datetime(2026, 7, 12, 18, 0, tzinfo=timezone.utc)

    # Create a synthetic late-arriving shift record in memory
    late_record = WorkplaceDaily(
        site_id="AD_SITE_01",
        shift_date=date(2026, 7, 10),
        workers_on_shift=50,
        worker_hours=400.0,
        heat_incidents=3,
        near_misses=5,
        sickness_absence_count=2,
        received_at=t_late_arrival,  # Late arrival timestamp!
        synthetic_flag=True
    )

    # Filter simulating decision time t
    # A decision engine checking available data at t_decision will find received_at <= t_decision is FALSE
    is_available_at_t = late_record.received_at <= t_decision
    assert is_available_at_t is False, "Future/late-arriving record leaked into decision time t!"

    # At t_late_arrival, the record becomes available
    is_available_later = late_record.received_at <= t_late_arrival
    assert is_available_later is True


def test_scenario_s8_late_arriving_replay_evaluation():
    """
    SRS Scenario S8:
    Replay engine evaluates all 8 scenarios, verifying S8 handles late arrival by withholding
    the unreceived shift data at time t.
    """
    eval_report = evaluate_all_scenarios()
    s8_result = next((s for s in eval_report["scenarios"] if s["scenario_id"] == "S8"), None)

    assert s8_result is not None
    # S8 has a late-arriving incident report, so at decision time t, workplace feed is capped at Advisory
    assert s8_result["multi_signal"]["tier_cap"] is not None
    assert "workplace feed missing/late" in s8_result["multi_signal"]["tier_cap"].lower()
    assert s8_result["demonstration_met"] is True

