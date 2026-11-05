from datetime import datetime, date, time, timedelta, timezone
from typing import Dict, Any, List, Optional

SCENARIO_DEFINITIONS = [
    {
        "id": "S1",
        "name": "Heat Rise + Incident Spike",
        "site_id": "AD_SITE_01",
        "description": "Rapid ambient temperature and heat index escalation coupled with surging workplace heat exhaustion incidents.",
        "expected_demonstration": "Early multi-signal alert, evidence card generation, and Action tier recommendation.",
        "simulated_onset_offset_hours": 6,
        "env_profile": {"temp_c": 46.5, "humidity_pct": 55.0, "pm25": 42.0},
        "workplace_profile": {"workers": 75, "hours": 600.0, "incidents": 4, "near_misses": 6, "absences": 5},
        "ground_truth_label": 1
    },
    {
        "id": "S2",
        "name": "PM2.5 Dust Surge + Near Misses",
        "site_id": "AD_SITE_02",
        "description": "High particulate dust storm (PM2.5 > 160 ug/m3) in Mussafah combined with elevated near-misses and respiratory sickness absence.",
        "expected_demonstration": "Combined environmental and workplace Advisory warning before severe incident occurs.",
        "simulated_onset_offset_hours": 12,
        "env_profile": {"temp_c": 38.0, "humidity_pct": 40.0, "pm25": 175.0},
        "workplace_profile": {"workers": 50, "hours": 400.0, "incidents": 1, "near_misses": 7, "absences": 8},
        "ground_truth_label": 1
    },
    {
        "id": "S3",
        "name": "Hot Weather, Stable Workplace",
        "site_id": "AD_SITE_03",
        "description": "High summer heat index, but effective hydration controls prevent workplace incidents (zero incidents/near misses).",
        "expected_demonstration": "Avoids automatic Action tier; issues Watch/Advisory only. Controls false positive alarm rate.",
        "simulated_onset_offset_hours": None,
        "env_profile": {"temp_c": 44.0, "humidity_pct": 48.0, "pm25": 30.0},
        "workplace_profile": {"workers": 90, "hours": 720.0, "incidents": 0, "near_misses": 1, "absences": 1},
        "ground_truth_label": 0
    },
    {
        "id": "S4",
        "name": "Workplace Incident Rise, Mild Weather",
        "site_id": "AD_SITE_01",
        "description": "Moderate spring weather, but sudden spike in site heat/exertion incidents due to heavy PPE or inadequate ventilation.",
        "expected_demonstration": "Statistical CUSUM engine detects independent workplace anomaly and prompts HSE investigation.",
        "simulated_onset_offset_hours": 4,
        "env_profile": {"temp_c": 29.0, "humidity_pct": 35.0, "pm25": 18.0},
        "workplace_profile": {"workers": 70, "hours": 560.0, "incidents": 3, "near_misses": 5, "absences": 2},
        "ground_truth_label": 1
    },
    {
        "id": "S5",
        "name": "Missing Workplace CSV Feed",
        "site_id": "AD_SITE_02",
        "description": "Severe heat index observed, but workplace CSV shift report was not submitted or network transmission failed.",
        "expected_demonstration": "Tier capped at Advisory maximum; explicit 'missing_workplace_feed' quality banner displayed.",
        "simulated_onset_offset_hours": 8,
        "env_profile": {"temp_c": 47.0, "humidity_pct": 60.0, "pm25": 50.0},
        "workplace_profile": None,  # Simulated missing feed
        "ground_truth_label": 1
    },
    {
        "id": "S6",
        "name": "Stale Environmental Provider",
        "site_id": "AD_SITE_03",
        "description": "External Open-Meteo weather provider is unreachable. Cached last-known observations are older than 4 hours.",
        "expected_demonstration": "Cached data labeled stale; system blocks unsupported new Action tier; preserves separate confidence indicator.",
        "simulated_onset_offset_hours": None,
        "env_profile": {"temp_c": 42.0, "humidity_pct": 50.0, "pm25": 35.0, "age_hours": 5.5, "is_stale": True},
        "workplace_profile": {"workers": 90, "hours": 720.0, "incidents": 1, "near_misses": 2, "absences": 2},
        "ground_truth_label": 0
    },
    {
        "id": "S7",
        "name": "Small Cohort Privacy Test (N < 11)",
        "site_id": "AD_SITE_01",
        "description": "Night shift or specialized crew with small counts (e.g. 3 incidents, 2 near-misses, 4 absences).",
        "expected_demonstration": "Small-cell privacy suppression strictly masks numbers 1-10 as '<11' in all outward views and exports.",
        "simulated_onset_offset_hours": 8,
        "env_profile": {"temp_c": 36.0, "humidity_pct": 65.0, "pm25": 40.0},
        "workplace_profile": {"workers": 15, "hours": 120.0, "incidents": 3, "near_misses": 2, "absences": 4},
        "ground_truth_label": 1
    },
    {
        "id": "S8",
        "name": "Late-Arriving Incident Report",
        "site_id": "AD_SITE_02",
        "description": "Workplace shift incidents occurred on day t but incident report was entered into the database 48 hours late.",
        "expected_demonstration": "Chronological replay at time t strictly excludes records where received_at > t, proving zero future data leakage.",
        "simulated_onset_offset_hours": 6,
        "env_profile": {"temp_c": 41.0, "humidity_pct": 52.0, "pm25": 45.0},
        "workplace_profile": {
            "workers": 50,
            "hours": 400.0,
            "incidents": 3,
            "near_misses": 4,
            "absences": 3,
            "received_late": True
        },
        "ground_truth_label": 1
    }
]


def get_all_scenarios() -> List[Dict[str, Any]]:
    return SCENARIO_DEFINITIONS


def get_scenario_by_id(scenario_id: str) -> Optional[Dict[str, Any]]:
    for s in SCENARIO_DEFINITIONS:
        if s["id"].upper() == scenario_id.upper():
            return s
    return None
