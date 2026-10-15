"""Build the deterministic, synthetic payload used by the public demo.

This module deliberately has no Garmin authentication, environment-secret, or
network dependency.  It reuses the production pipeline with a small fixed fake
client so the demo stays close to the live payload contract without copying any
real account data.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sync
from provenance import DataQuality


DEMO_UPDATED_AT = "2025-01-31T08:00:00+00:00"
DEMO_DATE = "2025-01-31"


def _sleep(date_str, hours=7.5, score=82, bedtime=1380):
    total = int(hours * 3600)
    return {
        "date": date_str,
        "score": score,
        "total_seconds": total,
        "deep_seconds": int(total * 0.22),
        "rem_seconds": int(total * 0.18),
        "light_seconds": int(total * 0.60),
        "awake_seconds": 0,
        "avg_stress": 18.0,
        "avg_respiration": 13.0,
        "lowest_respiration": 9.0,
        "bedtime_minutes": bedtime,
    }


def _history():
    start = datetime.fromisoformat("2024-10-01")
    sleep = []
    rhr = []
    hrv = []
    steps = []
    for index in range(123):
        current = (start + timedelta(days=index)).date().isoformat()
        sleep.append(_sleep(current, hours=7.0 + (index % 4) * 0.25, score=76 + index % 12))
        rhr.append({"calendarDate": current, "value": 57.0 + (index % 4) * 0.5})
        hrv.append({
            "calendarDate": current,
            "lastNightAvg": 52 + index % 8,
            "weeklyAvg": 55,
            "status": "BALANCED",
        })
        steps.append({"calendarDate": current, "totalSteps": 6200 + (index % 5) * 500, "stepGoal": 8000})
    return sleep, rhr, hrv, steps


class _DemoClient:
    full_name = "Demo Athlete"
    display_name = "demo-athlete"

    def get_stress_data(self, _date):
        return {"stressValuesArray": [[index, 18 + index % 9] for index in range(80)]}

    def get_body_battery(self, _date):
        return [{"charged": 44, "drained": 21}]

    def get_user_summary(self, _date):
        return {"totalSteps": 7800, "averageStressLevel": 24}


def _fetched():
    sleep, rhr, hrv, steps = _history()
    profile = {
        "gender": "OTHER",
        "birth_date": "1990-01-01",
        "age_years": 35,
        "height_cm": 175.0,
        "weight_kg": 72.0,
        "vo2max": 42.0,
        "lactate_threshold_hr": 158,
        "activity_level": None,
        "devices": [{"name": "Demo Watch", "primary": True}],
        "heat_acclimation_pct": 35,
        "altitude_acclimation_pct": None,
    }
    activities = [{
        "activityId": 1001,
        "activityName": "Demo Run",
        "activityType": "running",
        "category": "Running",
        "startTimeLocal": "2025-01-30 07:15:00",
        "locationName": "Example Park",
        "startLatitude": None,
        "startLongitude": None,
        "elevationGain": 48.0,
        "steps": 5200,
        "distance_km": 5.2,
        "duration_min": 32.0,
        "calories": 360,
        "averageHR": 142,
        "maxHR": 165,
        "aerobicTrainingEffect": 2.4,
        "anaerobicTrainingEffect": 0.2,
        "exercise_sets": None,
    }]
    return {
        "today_str": DEMO_DATE,
        "profile": profile,
        "rhr": rhr,
        "hrv": hrv,
        "sleep": sleep,
        "fitness": {
            "fitness_age": 33.0,
            "chronological_age": 35,
            "achievable_fitness_age": 31.0,
            "device_name": "Demo Watch",
            "training_status": "Maintaining",
            "acute_load": 48,
            "chronic_load": 180,
            "acwr": 0.27,
            "acwr_status": "LOW",
        },
        "activities": activities,
        "location": {
            "location_days": [{
                "date": "2025-01-30",
                "location": "Example Park",
                "latitude": None,
                "longitude": None,
            }],
            "weather": {
                "temp_c": 22.0,
                "feels_like_c": 22.0,
                "humidity_pct": 55,
                "dew_point_c": 12.0,
                "station": "Demo Station",
            },
            "weather_live": False,
        },
        "spo2": [{"date": "2025-01-29", "latest": 97, "sleep_average": 96, "lowest": 94}],
        "steps": steps,
        "hydration": {"goal_ml": 2200, "intake_ml": 1800, "sweat_loss_ml": 420},
        "daily_activity": {
            "steps": 7800,
            "step_goal": 8000,
            "floors": 6,
            "active_kcal": 410,
            "total_kcal": 1900,
            "intensity_goal": 150,
        },
        "intensity": {"weekly_total": 96, "moderate": 76, "vigorous": 10, "goal": 150},
        "races": {"date": DEMO_DATE, "time5k": 1800, "time10k": 3800, "time_half": 8400, "time_marathon": 18000},
    }


def _mark_synthetic(payload):
    quality = payload.get("data_quality", {})
    metrics = quality.get("metrics", {})
    for metric in metrics.values():
        metric["source"] = "demo"
        metric["note"] = "synthetic demonstration value"
    total = len(metrics)
    quality.update({
        "demo": True,
        "degraded": [],
        "live_count": 0,
        "total_count": total,
        "live_pct": 0,
        "core_degraded": [],
    })
    payload["data_quality"] = quality
    payload["demo"] = {
        "synthetic": True,
        "label": "Synthetic demo data — not connected to Garmin",
    }
    payload["updated_at"] = DEMO_UPDATED_AT
    payload["athlete"]["name"] = "Demo Athlete"
    payload["athlete"]["display_name"] = "demo-athlete"
    return payload


def build_demo_payload():
    """Return a deterministic payload with the production dashboard shape."""
    original_now = sync.utc_now_iso
    sync.utc_now_iso = lambda: DEMO_UPDATED_AT
    try:
        dq = DataQuality()
        dq.record("sleep", True, "synthetic demonstration nights")
        dq.record("rhr", True, "synthetic demonstration readings")
        dq.record("hrv", True, "synthetic demonstration summaries")
        payload = sync.build_payload(_DemoClient(), _fetched(), dq)
    finally:
        sync.utc_now_iso = original_now
    return _mark_synthetic(payload)


def write_demo_payload(path="data/demo.json"):
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(build_demo_payload(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


if __name__ == "__main__":
    write_demo_payload()
