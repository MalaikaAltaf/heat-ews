import pytest
from app.core.privacy import (
    suppress_small_cell_count,
    apply_privacy_to_workplace_dict,
    sanitize_workplace_records
)
from app.services.csv_service import validate_and_parse_csv


def test_small_cell_count_suppression():
    """
    SRS PRV-02:
    Counts between 1 and 10 must be displayed as '<11'.
    Counts of 0 must remain 0 (indicates zero events).
    Counts >= 11 must remain exact.
    """
    assert suppress_small_cell_count(0) == 0
    assert suppress_small_cell_count(1) == "<11"
    assert suppress_small_cell_count(5) == "<11"
    assert suppress_small_cell_count(10) == "<11"
    assert suppress_small_cell_count(11) == 11
    assert suppress_small_cell_count(25) == 25
    assert suppress_small_cell_count(None) is None


def test_reconstruction_prevention_on_rates():
    """
    SRS PRV-02:
    Suppress derived percentages and complementary totals when small cells are suppressed
    to prevent reverse-engineering of incident counts.
    """
    sample_record = {
        "site_id": "AD_SITE_01",
        "shift_date": "2026-06-15",
        "workers_on_shift": 50,
        "worker_hours": 400.0,
        "heat_incidents": 3,  # Between 1-10 -> Must be masked as "<11"
        "near_misses": 8,     # Between 1-10 -> Must be masked as "<11"
        "sickness_absence_count": 0  # 0 -> Kept as 0
    }

    sanitized = apply_privacy_to_workplace_dict(sample_record, is_public_or_export=True)

    assert sanitized["heat_incidents"] == "<11"
    assert sanitized["near_misses"] == "<11"
    assert sanitized["sickness_absence_count"] == 0
    # Complementary rates must be masked to prevent calculation: (rate * hours) = count
    assert sanitized["incident_rate_per_1k_hours"] == "Suppressed (<11 events)"
    assert sanitized["near_miss_rate_per_1k_hours"] == "Suppressed (<11 events)"


def test_individual_identifiers_strictly_rejected_at_upload(db):
    """
    SRS PRV-01:
    Reject worker/patient identifiers at upload; no individual-level tables or drilldowns.
    """
    csv_with_worker_ids = """site_id,shift_date,worker_id,workers_on_shift,worker_hours,heat_incidents,near_misses,sickness_absence_count
AD_SITE_01,2026-06-20,WRK-9901,50,400,1,2,0
"""
    result = validate_and_parse_csv(csv_with_worker_ids, db)
    assert result["success"] is False
    assert result["rows_imported"] == 0
    assert any("Privacy Violation" in err for err in result["errors"])
    assert any("worker_id" in err for err in result["errors"])


def test_internal_hse_unmasked_view():
    """
    Internal authorized HSE Officers can view actual shift counts,
    while outward public views receive the masked version.
    """
    raw = {
        "site_id": "AD_SITE_01",
        "heat_incidents": 4,
        "near_misses": 2,
        "sickness_absence_count": 1
    }

    # Internal authorized view (is_public_or_export=False)
    internal = apply_privacy_to_workplace_dict(raw, is_public_or_export=False)
    assert internal["heat_incidents"] == 4
    assert internal["near_misses"] == 2

    # Public/District view (is_public_or_export=True)
    public = apply_privacy_to_workplace_dict(raw, is_public_or_export=True)
    assert public["heat_incidents"] == "<11"
    assert public["near_misses"] == "<11"

