
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

sites = {
    "AD_SITE_01": 70,
    "AD_SITE_02": 50,
    "AD_SITE_03": 90,
}

output = Path(__file__).parent / "workplace_daily.csv"

with output.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "site_id",
        "shift_date",
        "workers_on_shift",
        "worker_hours",
        "heat_incidents",
        "near_misses",
        "sickness_absence_count"
    ])

    start = date(2026, 6, 1)

    for day in range(60):
        current_date = start + timedelta(days=day)

        for site_id, workforce in sites.items():
            workers = max(20, workforce + random.randint(-5, 5))
            worker_hours = workers * 8

            heat_incidents = random.choices(
                [0, 1, 2, 3],
                weights=[75, 18, 6, 1]
            )[0]

            near_misses = random.randint(0, 4)
            absence = random.randint(0, 5)

            writer.writerow([
                site_id,
                current_date.isoformat(),
                workers,
                worker_hours,
                heat_incidents,
                near_misses,
                absence
            ])

print(f"Generated: {output}")
