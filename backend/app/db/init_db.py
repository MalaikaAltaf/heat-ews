import csv
from datetime import datetime, time, timezone, date
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal, Base
from app.db.models import Site, User, WorkplaceDaily, EnvironmentRecord
from app.core.security import get_password_hash


PILOT_SITES = [
    {
        "site_id": "AD_SITE_01",
        "pseudonym": "Al Reem Coastal Construction Sector A",
        "sector": "Commercial High-Rise",
        "region": "Al Reem Island, Abu Dhabi",
        "latitude": 24.498,
        "longitude": 54.405,
        "timezone": "Asia/Dubai",
    },
    {
        "site_id": "AD_SITE_02",
        "pseudonym": "Mussafah Industrial Development Sector C",
        "sector": "Industrial Infrastructure",
        "region": "Mussafah, Abu Dhabi",
        "latitude": 24.341,
        "longitude": 54.512,
        "timezone": "Asia/Dubai",
    },
    {
        "site_id": "AD_SITE_03",
        "pseudonym": "Khalifa City Transport Hub Expansion",
        "sector": "Civil & Highway Works",
        "region": "Khalifa City, Abu Dhabi",
        "latitude": 24.428,
        "longitude": 54.577,
        "timezone": "Asia/Dubai",
    },
]

DEMO_USERS = [
    {
        "username": "hse_reem",
        "role": "hse_officer",
        "permitted_site_id": "AD_SITE_01",
        "password": "password123",
    },
    {
        "username": "hse_mussafah",
        "role": "hse_officer",
        "permitted_site_id": "AD_SITE_02",
        "password": "password123",
    },
    {
        "username": "hse_khalifa",
        "role": "hse_officer",
        "permitted_site_id": "AD_SITE_03",
        "password": "password123",
    },
    {
        "username": "public_health_viewer",
        "role": "public_health_viewer",
        "permitted_site_id": None,
        "password": "password123",
    },
    {
        "username": "admin_steward",
        "role": "data_steward",
        "permitted_site_id": None,
        "password": "password123",
    },
]


def init_db(db: Session = None):
    # Create all tables in PostgreSQL
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")

    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        # 1. Seed Pilot Sites
        for site_info in PILOT_SITES:
            existing = db.query(Site).filter(Site.site_id == site_info["site_id"]).first()
            if not existing:
                site = Site(**site_info)
                db.add(site)
                print(f"Created site: {site_info['site_id']} ({site_info['pseudonym']})")
            else:
                for k, v in site_info.items():
                    setattr(existing, k, v)
        db.commit()

        # 2. Seed Demo Users
        for user_info in DEMO_USERS:
            existing_user = db.query(User).filter(User.username == user_info["username"]).first()
            if not existing_user:
                new_user = User(
                    username=user_info["username"],
                    role=user_info["role"],
                    permitted_site_id=user_info["permitted_site_id"],
                    hashed_password=get_password_hash(user_info["password"])
                )
                db.add(new_user)
                print(f"Created demo user: {user_info['username']} ({user_info['role']})")
        db.commit()

        # 3. Seed Workplace Daily from CSV
        csv_path = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "workplace_daily.csv"
        if csv_path.exists():
            with csv_path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                added_count = 0
                for row in reader:
                    site_id = row["site_id"]
                    shift_date = date.fromisoformat(row["shift_date"])
                    existing_record = db.query(WorkplaceDaily).filter(
                        WorkplaceDaily.site_id == site_id,
                        WorkplaceDaily.shift_date == shift_date
                    ).first()

                    if not existing_record:
                        # Shift ends at 17:00 UTC+4 (13:00 UTC)
                        received_dt = datetime.combine(shift_date, time(13, 0), tzinfo=timezone.utc)
                        record = WorkplaceDaily(
                            site_id=site_id,
                            shift_date=shift_date,
                            workers_on_shift=int(row["workers_on_shift"]),
                            worker_hours=float(row["worker_hours"]),
                            heat_incidents=int(row["heat_incidents"]),
                            near_misses=int(row["near_misses"]),
                            sickness_absence_count=int(row["sickness_absence_count"]),
                            received_at=received_dt,
                            synthetic_flag=True
                        )
                        db.add(record)
                        added_count += 1
                db.commit()
                print(f"Seeded {added_count} workplace daily records from CSV.")

    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    init_db()

