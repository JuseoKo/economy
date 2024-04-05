FROM apache/airflow:2.8.4-python3.11

COPY .env .
COPY requirements.txt .

RUN pip install -r requirements.txt