import asyncio
import httpx
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Site, EnvironmentRecord
from app.analytics.heat_index import calculate_heat_index

START_DATE = "2026-06-01"
END_DATE = "2026-07-30"


async def fetch_archive_for_site(client: httpx.AsyncClient, lat: float, lon: float):
    weather_url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={START_DATE}&end_date={END_DATE}&"
        f"hourly=temperature_2m,relative_humidity_2m&timezone=Asia%2FDubai"
    )
    aq_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}&start_date={START_DATE}&end_date={END_DATE}&"
        f"hourly=pm2_5&timezone=Asia%2FDubai"
    )

    w_res = await client.get(weather_url)
    w_data = w_res.json() if w_res.status_code == 200 else {}

    aq_res = await client.get(aq_url)
    aq_data = aq_res.json() if aq_res.status_code == 200 else {}

    return w_data, aq_data


async def seed_historical_environmental_data():
    db: Session = SessionLocal()
    sites = db.query(Site).all()
    print(f"Fetching historical environmental data ({START_DATE} to {END_DATE}) for {len(sites)} sites...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for site in sites:
            print(f"--> Fetching site {site.site_id} ({site.pseudonym})...")
            w_data, aq_data = await fetch_archive_for_site(client, site.latitude, site.longitude)

            w_hourly = w_data.get("hourly", {})
            times = w_hourly.get("time", [])
            temps = w_hourly.get("temperature_2m", [])
            humidities = w_hourly.get("relative_humidity_2m", [])

            aq_hourly = aq_data.get("hourly", {})
            aq_times = aq_hourly.get("time", [])
            pm25_vals = aq_hourly.get("pm2_5", [])
            pm25_map = {t: v for t, v in zip(aq_times, pm25_vals)}

            # Single bulk query for existing records to avoid 1440 network roundtrips!
            existing_valid_ats = {
                r[0] for r in db.query(EnvironmentRecord.valid_at).filter(
                    EnvironmentRecord.site_id == site.site_id
                ).all()
            }

            records_to_insert = []
            for i, t_str in enumerate(times):
                local_dt = datetime.fromisoformat(t_str)
                # Convert Asia/Dubai (UTC+4) to UTC
                valid_at_utc = local_dt.replace(tzinfo=timezone.utc) - timedelta(hours=4)
                received_dt = valid_at_utc + timedelta(hours=1)

                if valid_at_utc in existing_valid_ats:
                    continue

                temp = temps[i] if i < len(temps) else None
                hum = humidities[i] if i < len(humidities) else None
                pm25 = pm25_map.get(t_str)
                hi = calculate_heat_index(temp, hum) if (temp is not None and hum is not None) else None

                records_to_insert.append(EnvironmentRecord(
                    site_id=site.site_id,
                    valid_at=valid_at_utc,
                    issued_at=valid_at_utc,
                    received_at=received_dt,
                    temperature_c=temp,
                    humidity_pct=hum,
                    pm25=pm25,
                    heat_index_c=hi,
                    source="Open-Meteo Archive",
                    is_forecast=False
                ))

            if records_to_insert:
                db.bulk_save_objects(records_to_insert)
                db.commit()
                print(f"    Saved {len(records_to_insert)} historical environmental records for {site.site_id}.")
            else:
                print(f"    Records already exist for {site.site_id}.")

    db.close()
    print("Historical environmental seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed_historical_environmental_data())
