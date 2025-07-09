from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from scripts.load_task import load_single_origin_destination_pair
from scripts.fetch_task import fetch_wrapper
from scripts.clean_task import clean_task
from scripts.save_task import save_task

# 기본 파라미터 정의
default_args = {
    'owner': 'siu',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['admin@example.com'],
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

# DAG 정의
with DAG(
    dag_id='api_to_postgres_dag',
    default_args=default_args,
    description='API에서 데이터 받아서 PostgreSQL에 저장하는 DAG',
    schedule_interval='@daily',       # 매일 0시
    start_date=datetime(2024, 1, 1),  # 시작 기준일
    catchup=False,                    # 과거 날짜 자동 실행 방지
    tags=['api', 'postgres'],
) as dag:
    
    # Task 정의
    load_task = PythonOperator(
        task_id='load_task',
        python_callable=load_single_origin_destination_pair
    )

    fetch_task = PythonOperator(
        task_id='fetch_task',
        python_callable=fetch_wrapper
    )

    clean_task = PythonOperator(
        task_id='clean_task',
        python_callable=clean_task
    )

    save_task = PythonOperator(
        task_id='save_task',
        python_callable=save_task
    )

    # Task 순서 지정
    load_task >> fetch_task >> clean_task >> save_task