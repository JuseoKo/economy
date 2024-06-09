from airflow.models.dag import DAG
from datetime import datetime

with DAG(
    dag_id="stock_all",
    tags=["stock"],
    description="[매일] stock 데이터를 업데이트하는 DAG입니다.",
    schedule_interval="0 0 * * *",
    start_date=datetime(2024, 1, 1),  # DAG의 시작 날짜
    catchup=False
) as dag:
    from tasks.stock.us_stock import us_stock_base_to_database
    from airflow.operators.python import PythonOperator

    us_stock_base_to_database_all = PythonOperator(
        task_id="us_stock_base_to_database_all",
        python_callable=us_stock_base_to_database,
    )

    us_stock_base_to_database_all