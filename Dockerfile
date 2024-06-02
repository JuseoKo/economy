FROM apache/airflow:2.9.1-python3.11

#COPY .env .
COPY requirements.txt .

RUN pip install -r requirements.txt