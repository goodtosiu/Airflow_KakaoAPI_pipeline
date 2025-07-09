import os
import psycopg2
from airflow.models import Variable
from airflow.models.xcom_arg import XComArg

def save_task(**context):
    """
    보간된 duration 데이터를 PostgreSQL에 저장하고,
    성공 시 include/origin.txt와 destination.txt를 갱신합니다.
    """
    interpolated_data = context["ti"].xcom_pull(task_ids="clean_task")

    if not interpolated_data:
        raise ValueError("No interpolated data received from clean_task")

    origin_id = interpolated_data[0]["origin_id"]
    destination_id = interpolated_data[0]["destination_id"]
    origin_name = interpolated_data[0]["origin_name"]
    destination_name = interpolated_data[0]["destination_name"]

    conn = psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="postgres",
        port="5432"
    )

    insert_query = """
    INSERT INTO travel_time (
        origin_id, destination_id, origin_name,
        destination_name, departure_time, duration
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (origin_id, destination_id, departure_time)
    DO NOTHING;
    """

    try:
        with conn:
            with conn.cursor() as cur:
                for row in interpolated_data:
                    cur.execute(insert_query, (
                        row["origin_id"],
                        row["destination_id"],
                        row["origin_name"],
                        row["destination_name"],
                        row["departure_time"],
                        row["duration"]
                    ))
    finally:
        conn.close()

    # 저장 완료되면 파일 업데이트 로직 (규칙 기반)
    new_origin_id = origin_id
    new_destination_id = destination_id

    if destination_id < 41:
        new_destination_id += 1
    else:
        new_destination_id = 1
        new_origin_id += 1

    with open("include/origin_id.txt", "w") as f:
        f.write(str(new_origin_id))

    with open("include/destination_id.txt", "w") as f:
        f.write(str(new_destination_id))

    print(f"Updated to next pair: ({new_origin_id}, {new_destination_id})")