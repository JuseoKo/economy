FROM apache/airflow:2.10.5-python3.12

#COPY .env .
#COPY requirements.txt .
WORKDIR /opt/airflow

# 상위 디렉토리의 requirements.txt를 복사
COPY requirements.txt .

RUN pip install uv
RUN uv pip install --no-cache-dir -r requirements.txt