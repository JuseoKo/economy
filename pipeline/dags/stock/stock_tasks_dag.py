import pendulum

from airflow.models.dag import DAG
from airflow.providers.standard.operators.python import PythonOperator
from pipeline.tasks.stock.krx import StockList, StockPrice

with DAG(
    dag_id="stock_price",
    schedule="0 18 * * *",
    start_date=pendulum.datetime(2023, 1, 1, tz="Asia/Seoul"),
    catchup=False,
    tags={"stock-price"},
) as dag:
    stock_list = StockList()
    stock_price = StockPrice()

    stock_list_task = PythonOperator(
        task_id="stock_list_task",
        python_callable=stock_list.run,
    )

    stock_price_task = PythonOperator(
        task_id="stock_price_task",
        python_callable=stock_price.run,
    )

    stock_list_task >> stock_price_task
