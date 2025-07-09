# scripts/fetch_api.py

import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

KAKAO_KEYS = os.environ.get("KAKAO_KEYS", "").split(",")  # 쉼표 구분으로 최대 10개
BASE_URL = "https://apis-navi.kakaomobility.com/v1/future/directions"

def _build_departure_times(days=5):
    base = datetime(2025, 12, 21)  # ✅ 고정된 기준일
    # Only yield 8 specific time slots per day (1st, 10th, 16th, 17th, 25th, 32nd, 37th, 40th)
    slots = [0, 9, 15, 16, 24, 31, 36, 39]  # zero-based index
    for d in range(days):
        date = base + timedelta(days=d+1)  # 내일부터 시작
        for slot in slots:
            dt = date + timedelta(minutes=30 * slot)
            yield dt.strftime("%Y%m%d%H%M")

def fetch_for_pair(pair):
    """
    origin/destination dict 입력 ->
    5일 × 8타임슬롯 = 40개의 요청을 병렬 실행
    실패 시 전체 실패로 간주.
    """
    origin = f"{pair['origin_lng']},{pair['origin_lat']}"
    destination = f"{pair['dest_lng']},{pair['dest_lat']}"
    times = list(_build_departure_times())
    total = len(times)

    results = []
    errors = []

    def call_api(departure_time, key):
        params = {
            "origin": origin,
            "destination": destination,
            "departure_time": departure_time,
        }
        headers = {
            "Authorization": f"KakaoAK {key}",
            "Content-Type": "application/json"
        }
        resp = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            raise RuntimeError(f"{departure_time} => status {resp.status_code}")
        data = resp.json()
        return departure_time, data # ✅ 요청보낸 시간과 그 반환값 

    with ThreadPoolExecutor(max_workers=min(total, len(KAKAO_KEYS))) as exe:
        future_to_info = {}
        for idx, departure_time in enumerate(times):
            key = KAKAO_KEYS[idx % len(KAKAO_KEYS)]
            future = exe.submit(call_api, departure_time, key)
            future_to_info[future] = departure_time

        for fut in as_completed(future_to_info):
            dt = future_to_info[fut]
            try:
                departure_time, data = fut.result()
                print(f"[OK] {departure_time}")
                duration = data["routes"][0]["summary"]["duration"]
                print(f"[DATA] {departure_time} → {duration} sec")
                results.append({
                    "departure_time": departure_time,
                    "duration": duration,
                    "origin_id": pair["origin_id"],
                    "destination_id": pair["dest_id"],
                    "origin_name": pair.get("origin_name"),
                    "destination_name": pair.get("dest_name")
                })
            except Exception as e:
                print(f"[ERROR] {dt} -> {e}")
                errors.append(dt)

    if errors:
        raise RuntimeError(f"{len(errors)}/{total} failed: {errors[:3]}...")
    print(f"[DONE] {total}/{total} requests succeeded")
    print(f"[RETURN] Total durations collected: {len(results)}")
    return results

def fetch_wrapper(**context):
    ti = context['ti']  # 현재 TaskInstance
    pair = ti.xcom_pull(task_ids='load_task')  # load_task의 return 값
    if pair:
        return fetch_for_pair(pair)
    else:
        raise ValueError("No pair data received from load_task")