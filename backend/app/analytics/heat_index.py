from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional, Tuple, Dict, Any
from app.core.config import settings


def calculate_heat_index(temp_c: float, humidity_pct: float) -> Optional[float]:
    """
    Computes the NOAA Heat Index in Celsius using the standard Rothfusz regression.
    Strictly marked as an environmental screening indicator, NOT as WBGT or clinical heat strain.
    """
    if temp_c is None or humidity_pct is None:
        return None

    # Range validation
    if temp_c < -20 or temp_c > 65 or humidity_pct < 0 or humidity_pct > 100:
        return None

    # Convert to Fahrenheit for NOAA formula
    t_f = (temp_c * 9.0 / 5.0) + 32.0
    rh = float(humidity_pct)

    # Simple Steadman equation for cooler conditions
    hi_simple = 0.5 * (t_f + 61.0 + ((t_f - 68.0) * 1.2) + (rh * 0.094))

    if hi_simple < 80.0:
        hi_f = hi_simple
    else:
        # Full Rothfusz polynomial regression
        hi_f = (
            -42.379
            + (2.04901523 * t_f)
            + (10.14333127 * rh)
            - (0.22475541 * t_f * rh)
            - (0.00683783 * (t_f**2))
            - (0.05481717 * (rh**2))
            + (0.00122874 * (t_f**2) * rh)
            + (0.00085282 * t_f * (rh**2))
            - (0.00000199 * (t_f**2) * (rh**2))
        )

        # Adjustment for low humidity
        if rh < 13.0 and (80.0 <= t_f <= 112.0):
            adj = ((13.0 - rh) / 4.0) * ((17.0 - abs(t_f - 95.0)) / 17.0) ** 0.5
            hi_f -= adj
        # Adjustment for high humidity
        elif rh > 85.0 and (80.0 <= t_f <= 87.0):
            adj = ((rh - 85.0) / 10.0) * ((87.0 - t_f) / 5.0)
            hi_f += adj

    # Convert back to Celsius
    hi_c = (hi_f - 32.0) * 5.0 / 9.0
    return round(hi_c, 1)


def check_mohre_midday_break(dt: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Evaluates UAE Ministry of Human Resources and Emiratisation (MOHRE) Midday Break rule:
    Applies from 15 June to 15 September between 12:30 and 15:00 Asia/Dubai time.
    Provides informational compliance reminders, NOT automated legal determinations.
    """
    dubai_tz = ZoneInfo(settings.TIMEZONE)
    if dt is None:
        local_dt = datetime.now(dubai_tz)
    else:
        if dt.tzinfo is None:
            local_dt = dt.replace(tzinfo=timezone.utc).astimezone(dubai_tz)
        else:
            local_dt = dt.astimezone(dubai_tz)

    month = local_dt.month
    day = local_dt.day
    hour_float = local_dt.hour + (local_dt.minute / 60.0)

    # Check if within date window: June 15 to Sept 15
    is_in_date_window = False
    if month == 6 and day >= settings.MOHRE_BREAK_START_DAY:
        is_in_date_window = True
    elif month in [7, 8]:
        is_in_date_window = True
    elif month == 9 and day <= settings.MOHRE_BREAK_END_DAY:
        is_in_date_window = True

    # Check if within time window: 12:30 to 15:00
    is_in_time_window = settings.MOHRE_BREAK_START_HOUR <= hour_float < settings.MOHRE_BREAK_END_HOUR

    is_active = is_in_date_window and is_in_time_window

    return {
        "is_active": is_active,
        "is_in_seasonal_period": is_in_date_window,
        "local_time_dubai": local_dt.strftime("%Y-%m-%d %H:%M:%S UTC+04:00"),
        "rule_summary": "UAE MOHRE Midday Break: Outdoor work in open areas prohibited 12:30-15:00 (15 June - 15 September).",
        "notice": (
            "MOHRE Midday Break in effect. High solar exposure tasks should be suspended."
            if is_active
            else "Standard shift safety precautions apply."
        ),
        "disclaimer": "Informational safeguard only; verify site-specific regulatory exemptions with official authorities."
    }

