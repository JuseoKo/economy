import pytest
from base import DBConnection
from sqlalchemy import text


@pytest.mark.db_connection
def test_db_connection():
    try:
        # api-db 세션 테스트
        api_session = DBConnection(db="api-db").create_engine()
        api_session.execute(text('SELECT 1'))
        api_session.close()
        # airflow-db 세션 테스트
        airflow_session = DBConnection(db="airflow-db").create_engine()
        airflow_session.execute(text('SELECT 1'))
        airflow_session.close()

    except Exception as e:
        print("Error connecting to database:", e)
        raise


