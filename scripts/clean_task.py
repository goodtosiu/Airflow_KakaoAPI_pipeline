import numpy as np
from scipy.interpolate import PchipInterpolator
from collections import defaultdict
from datetime import datetime, timedelta

def clean_task(**context):
    ti = context["ti"]
    raw_data = ti.xcom_pull(task_ids="fetch_task")

    if not raw_data or len(raw_data) < 2:
        raise ValueError("Insufficient data received from fetch_task")

    # Group by date (YYYY-MM-DD)
    grouped = defaultdict(dict)
    for item in raw_data:
        dt = datetime.strptime(item["departure_time"], "%Y%m%d%H%M")
        date_str = dt.strftime("%Y-%m-%d")
        grouped[date_str][dt.strftime("%H:%M")] = item["duration"]

    interpolated_all = []

    for date, time_duration_dict in grouped.items():
        base_date = datetime.strptime(date, "%Y-%m-%d")
        all_slots = [(base_date + timedelta(minutes=30 * i)).strftime("%H:%M") for i in range(48)]

        x = []
        y = []
        for i, slot in enumerate(all_slots):
            if slot in time_duration_dict:
                x.append(i)
                y.append(time_duration_dict[slot])

        if len(x) < 2:
            raise ValueError(f"Too few data points to interpolate for {date}")

        interpolator = PchipInterpolator(x, y)
        y_new = interpolator(range(48))

        for i, yi in enumerate(y_new):
            departure_time = (base_date + timedelta(minutes=30 * i)).strftime("%Y%m%d%H%M")
            interpolated_all.append({
                "departure_time": departure_time,
                "duration": float(yi),
                "origin_id": item["origin_id"],
                "destination_id": item["destination_id"],
                "origin_name": item["origin_name"],
                "destination_name": item["destination_name"]
            })

    # Sort by departure_time
    interpolated_all.sort(key=lambda x: x["departure_time"])
    print("[CLEAN] Sample of interpolated data:")
    for item in interpolated_all:
        print(item)

    print(f"[CLEAN] Interpolated {len(raw_data)} → {len(interpolated_all)} points")
    return interpolated_all