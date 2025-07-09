import psycopg2
import os

def load_single_origin_destination_pair():
    """
    하나의 origin_id와 destination_id를 파일에서 읽고,
    PostgreSQL에서 해당 행을 조회해 API 요청 조합으로 만든다.
    """
    with open("include/origin_id.txt", "r") as f:
        origin_id = int(f.read().strip())

    with open("include/destination_id.txt", "r") as f:
        destination_id = int(f.read().strip())

    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "airflow_pipeline-postgres-1"),
        dbname=os.environ.get("POSTGRES_DB", "airflow"),
        user=os.environ.get("POSTGRES_USER", "airflow"),
        password=os.environ.get("POSTGRES_PASSWORD", "airflow"),
        port=5432
    )
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, latitude, longitude FROM origin WHERE id = %s",
        (origin_id,)
    )
    origin = cursor.fetchone()

    cursor.execute(
        "SELECT id, name, latitude, longitude FROM destination WHERE id = %s",
        (destination_id,)
    )
    destination = cursor.fetchone()

    conn.close()

    if not origin or not destination:
        raise ValueError(f"Origin({origin_id}) or Destination({destination_id}) not found.")

    pair = {
        "origin_id": origin[0],
        "origin_name": origin[1],
        "origin_lat": origin[2],
        "origin_lng": origin[3],
        "dest_id": destination[0],
        "dest_name": destination[1],
        "dest_lat": destination[2],
        "dest_lng": destination[3],
    }

    print(f"요청 조합: origin({origin_id}) → destination({destination_id})")
    return pair