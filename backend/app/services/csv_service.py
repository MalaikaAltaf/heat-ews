import csv
import io
from datetime import datetime, date, time, timezone
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.db.models import Site, WorkplaceDaily

REQUIRED_COLUMNS = [
    "site_id",
    "shift_date",
    "workers_on_shift",
    "worker_hours",
    "heat_incidents",
    "near_misses",
    "sickness_absence_count"
]

FORBIDDEN_IDENTIFIERS = [
    "worker_id",
    "employee_id",
    "name",
    "first_name",
    "last_name",
    "national_id",
    "ssn",
    "emirates_id",
    "patient_id",
    "badge_number"
]


def validate_and_parse_csv(content_str: str, db: Session) -> Dict[str, Any]:
    """
    Validates uploaded CSV file contents against SRS ING-02 & PRV-01.
    Rejects any individual identifiers, negative values, impossible ratios, and returns detailed row errors.
    """
    f = io.StringIO(content_str.strip())
    reader = csv.reader(f)

    try:
        header = next(reader)
    except StopIteration:
        return {"success": False, "errors": ["Uploaded file is completely empty."], "rows_imported": 0}

    header_lower = [c.strip().lower() for c in header]

    # 1. Privacy Check: Prohibit individual worker/patient identifiers
    for col in header_lower:
        for forbidden in FORBIDDEN_IDENTIFIERS:
            if forbidden in col:
                return {
                    "success": False,
                    "errors": [
                        f"Privacy Violation (PRV-01): Upload contains individual identifier column '{col}'. "
                        "HEAT-EWS strictly prohibits individual-level workforce tracking."
                    ],
                    "rows_imported": 0
                }

    # 2. Check for required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in header_lower]
    if missing:
        return {
            "success": False,
            "errors": [f"Missing required columns in CSV header: {', '.join(missing)}"],
            "rows_imported": 0
        }

    col_idx = {col: header_lower.index(col) for col in REQUIRED_COLUMNS}

    valid_sites = {s.site_id for s in db.query(Site.site_id).all()}
    errors: List[str] = []
    records_to_insert: List[Dict[str, Any]] = []
    seen_site_dates = set()

    row_num = 1
    for row in reader:
        row_num += 1
        if not row or not any(row):
            continue

        try:
            site_id = row[col_idx["site_id"]].strip()
            shift_date_str = row[col_idx["shift_date"]].strip()
            workers_str = row[col_idx["workers_on_shift"]].strip()
            hours_str = row[col_idx["worker_hours"]].strip()
            incidents_str = row[col_idx["heat_incidents"]].strip()
            near_miss_str = row[col_idx["near_misses"]].strip()
            absence_str = row[col_idx["sickness_absence_count"]].strip()

            # Site validation
            if site_id not in valid_sites:
                errors.append(f"Row {row_num}: Unknown site_id '{site_id}'. Must be registered in pilot sites.")
                continue

            # Date validation
            try:
                shift_date = date.fromisoformat(shift_date_str)
            except ValueError:
                errors.append(f"Row {row_num}: Invalid date format '{shift_date_str}'. Expected YYYY-MM-DD.")
                continue

            # Duplicate check within file
            key = (site_id, shift_date)
            if key in seen_site_dates:
                errors.append(f"Row {row_num}: Duplicate entry for site '{site_id}' on shift_date '{shift_date}'.")
                continue
            seen_site_dates.add(key)

            # Integer and float conversions
            workers = int(workers_str)
            hours = float(hours_str)
            incidents = int(incidents_str)
            near_misses = int(near_miss_str)
            absence = int(absence_str)

            # Value and ratio validation
            if workers <= 0:
                errors.append(f"Row {row_num}: workers_on_shift must be greater than 0.")
                continue
            if hours <= 0:
                errors.append(f"Row {row_num}: worker_hours must be greater than 0.")
                continue
            if incidents < 0 or near_misses < 0 or absence < 0:
                errors.append(f"Row {row_num}: Incident, near miss, and absence counts cannot be negative.")
                continue
            if hours > workers * 24:
                errors.append(f"Row {row_num}: Impossible worker_hours ({hours}) exceeds 24h per worker ({workers} workers).")
                continue

            records_to_insert.append({
                "site_id": site_id,
                "shift_date": shift_date,
                "workers_on_shift": workers,
                "worker_hours": hours,
                "heat_incidents": incidents,
                "near_misses": near_misses,
                "sickness_absence_count": absence,
            })

        except (IndexError, ValueError) as ex:
            errors.append(f"Row {row_num}: Format parsing error - {str(ex)}")

    # If critical validation errors exist, reject whole file to maintain data integrity
    if errors:
        return {
            "success": False,
            "errors": errors[:25],  # Cap return errors to first 25 for readability
            "total_errors": len(errors),
            "rows_imported": 0
        }

    # Commit records
    now_utc = datetime.now(timezone.utc)
    for rec_data in records_to_insert:
        existing = db.query(WorkplaceDaily).filter(
            WorkplaceDaily.site_id == rec_data["site_id"],
            WorkplaceDaily.shift_date == rec_data["shift_date"]
        ).first()

        received_dt = datetime.combine(rec_data["shift_date"], time(13, 0), tzinfo=timezone.utc)

        if existing:
            existing.workers_on_shift = rec_data["workers_on_shift"]
            existing.worker_hours = rec_data["worker_hours"]
            existing.heat_incidents = rec_data["heat_incidents"]
            existing.near_misses = rec_data["near_misses"]
            existing.sickness_absence_count = rec_data["sickness_absence_count"]
            existing.received_at = now_utc
            existing.synthetic_flag = True
        else:
            new_rec = WorkplaceDaily(
                site_id=rec_data["site_id"],
                shift_date=rec_data["shift_date"],
                workers_on_shift=rec_data["workers_on_shift"],
                worker_hours=rec_data["worker_hours"],
                heat_incidents=rec_data["heat_incidents"],
                near_misses=rec_data["near_misses"],
                sickness_absence_count=rec_data["sickness_absence_count"],
                received_at=received_dt,
                synthetic_flag=True
            )
            db.add(new_rec)

    db.commit()

    return {
        "success": True,
        "errors": [],
        "rows_imported": len(records_to_insert)
    }

