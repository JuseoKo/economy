import pendulum

from airflow.models.dag import DAG
from airflow.providers.standard.operators.python import PythonOperator
from pipeline.tasks.stock.dart import DartPerformanceList, DartPerFormance

with DAG(
    dag_id="dart_performance",
    schedule="0 18 * * *",
    start_date=pendulum.datetime(2023, 1, 1, tz="Asia/Seoul"),
    catchup=False,
    tags={"stock", "dart"},
    doc_md="""
    ### DART 재무제표 DAG

    - DART에서 재무제표 목록을 가져와서 데이터베이스에 저장합니다.
    - 저장된 목록을 기반으로 재무제표 데이터를 수집하고 처리하여 저장합니다.
    """,
) as dag:
    dart_performance_list = DartPerformanceList()
    dart_performance = DartPerFormance()

    dart_performance_list_task = PythonOperator(
        task_id="dart_performance_list_task",
        python_callable=dart_performance_list.run,
    )

    dart_performance_task = PythonOperator(
        task_id="dart_performance_task",
        python_callable=dart_performance.run,
        op_kwargs={"title": "DART 재무제표"},
    )

    dart_performance_list_task >> dart_performance_task
