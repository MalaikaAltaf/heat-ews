from typing import Any, Dict, List, Union
from app.core.config import settings


def suppress_small_cell_count(value: Union[int, float, None]) -> Union[str, int, float, None]:
    """
    SRS Requirement PRV-02:
    Counts 1-10 must be displayed as "<11".
    0 is not suppressed as it indicates no incidents/absences.
    Counts > 10 remain unchanged.
    """
    if value is None:
        return None
    try:
        val = int(value)
        if 1 <= val <= settings.SMALL_CELL_SUPPRESSION_THRESHOLD:
            return f"<{settings.SMALL_CELL_SUPPRESSION_THRESHOLD + 1}"
        return val
    except (ValueError, TypeError):
        return value


def apply_privacy_to_workplace_dict(record: Dict[str, Any], is_public_or_export: bool = True) -> Dict[str, Any]:
    """
    Applies small-cell suppression to sensitive workplace counts.
    Suppresses heat_incidents, near_misses, sickness_absence_count if between 1-10.
    Also suppresses reconstructable rate percentages if cell count is suppressed.
    """
    sanitized = dict(record)

    # Strictly strip any prohibited individual-level identifiers if accidentally present
    prohibited_keys = ["worker_id", "employee_id", "name", "national_id", "email", "phone", "patient_id"]
    for key in prohibited_keys:
        sanitized.pop(key, None)

    if not is_public_or_export:
        return sanitized

    for field in ["heat_incidents", "near_misses", "sickness_absence_count"]:
        if field in sanitized:
            sanitized[field] = suppress_small_cell_count(sanitized[field])

    # If incidents were suppressed, mask exact raw incident rates to prevent reverse-engineering
    if isinstance(sanitized.get("heat_incidents"), str):
        sanitized["incident_rate_per_1k_hours"] = "Suppressed (<11 events)"
    if isinstance(sanitized.get("near_misses"), str):
        sanitized["near_miss_rate_per_1k_hours"] = "Suppressed (<11 events)"
    if isinstance(sanitized.get("sickness_absence_count"), str):
        sanitized["absence_rate_pct"] = "Suppressed (<11 events)"

    return sanitized


def sanitize_workplace_records(records: List[Dict[str, Any]], is_public_or_export: bool = True) -> List[Dict[str, Any]]:
    return [apply_privacy_to_workplace_dict(r, is_public_or_export) for r in records]

