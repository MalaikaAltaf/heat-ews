import httpx
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import Site, EnvironmentRecord
from app.analytics.heat_index import calculate_heat_index


async def fetch_open_meteo_data(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """
    Fetches real-time and 72-hour forecast weather and air quality from Open-Meteo APIs.
    """
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m",
        "timezone": "Asia/Dubai",
        "forecast_days": 3
    }
    air_quality_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "pm2_5",
        "timezone": "Asia/Dubai",
        "forecast_days": 3
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            weather_res = await client.get(settings.OPEN_METEO_WEATHER_URL, params=weather_params)
            weather_res.raise_for_status()
            weather_data = weather_res.json()
        except Exception as e:
            print(f"Warning: Failed to fetch Open-Meteo weather: {e}")
            weather_data = None

        try:
            aq_res = await client.get(settings.OPEN_METEO_AIR_QUALITY_URL, params=air_quality_params)
            aq_res.raise_for_status()
            aq_data = aq_res.json()
        except Exception as e:
            print(f"Warning: Failed to fetch Open-Meteo air quality: {e}")
            aq_data = None

    if not weather_data and not aq_data:
        return None

    return {
        "weather": weather_data,
        "air_quality": aq_data
    }


def sync_site_environmental_data(db: Session, site: Site, payload: Dict[str, Any]) -> int:
    """
    Parses Open-Meteo payload and saves/updates hourly environmental records.
    """
    weather = payload.get("weather") or {}
    air_quality = payload.get("air_quality") or {}

    w_hourly = weather.get("hourly", {})
    w_times = w_hourly.get("time", [])
    temps = w_hourly.get("temperature_2m", [])
    humidities = w_hourly.get("relative_humidity_2m", [])

    aq_hourly = air_quality.get("hourly", {})
    aq_times = aq_hourly.get("time", [])
    pm25s = aq_hourly.get("pm2_5", [])

    # Map air quality timestamps for quick lookup
    pm25_map = {t: v for t, v in zip(aq_times, pm25s)}

    now_utc = datetime.now(timezone.utc)
    records_saved = 0

    for i, t_str in enumerate(w_times):
        # Open-Meteo returns ISO local timestamp string in Asia/Dubai: e.g. "2026-11-04T14:00"
        # Convert to UTC
        local_dt = datetime.fromisoformat(t_str)
        # Shift 4 hours back from UTC+4
        valid_at_utc = local_dt.replace(tzinfo=timezone.utc) - timedelta(hours=4)

        temp = temps[i] if i < len(temps) else None
        hum = humidities[i] if i < len(humidities) else None
        pm25 = pm25_map.get(t_str)
        heat_idx = calculate_heat_index(temp, hum) if (temp is not None and hum is not None) else None
        is_forecast = valid_at_utc > now_utc

        # Check existing
        existing = db.query(EnvironmentRecord).filter(
            EnvironmentRecord.site_id == site.site_id,
            EnvironmentRecord.valid_at == valid_at_utc
        ).first()

        if existing:
            existing.temperature_c = temp
            existing.humidity_pct = hum
            existing.pm25 = pm25
            existing.heat_index_c = heat_idx
            existing.received_at = now_utc
            existing.is_forecast = is_forecast
        else:
            rec = EnvironmentRecord(
                site_id=site.site_id,
                valid_at=valid_at_utc,
                issued_at=now_utc,
                received_at=now_utc,
                temperature_c=temp,
                humidity_pct=hum,
                pm25=pm25,
                heat_index_c=heat_idx,
                source="Open-Meteo",
                is_forecast=is_forecast
            )
            db.add(rec)
            records_saved += 1

    db.commit()
    return records_saved


def get_latest_site_environment(db: Session, site_id: str) -> Dict[str, Any]:
    """
    Retrieves the most recent observation and checks freshness/stale status.
    """
    now_utc = datetime.now(timezone.utc)
    latest = db.query(EnvironmentRecord).filter(
        EnvironmentRecord.site_id == site_id,
        EnvironmentRecord.valid_at <= now_utc
    ).order_by(EnvironmentRecord.valid_at.desc()).first()

    if not latest:
        # Fallback to any latest record
        latest = db.query(EnvironmentRecord).filter(
            EnvironmentRecord.site_id == site_id
        ).order_by(EnvironmentRecord.valid_at.desc()).first()

    if not latest:
        return {
            "status": "unavailable",
            "is_stale": True,
            "message": "No environmental data records available for this site."
        }

    # Data age in hours
    age_hours = (now_utc - latest.received_at).total_seconds() / 3600.0
    is_stale = age_hours > 3.0

    return {
        "status": "stale" if is_stale else "fresh",
        "is_stale": is_stale,
        "age_hours": round(age_hours, 1),
        "valid_at": latest.valid_at.isoformat(),
        "received_at": latest.received_at.isoformat(),
        "temperature_c": latest.temperature_c,
        "humidity_pct": latest.humidity_pct,
        "pm25": latest.pm25,
        "heat_index_c": latest.heat_index_c,
        "source": latest.source,
        "is_forecast": latest.is_forecast
    }

