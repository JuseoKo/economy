# 수정중

주식 데이터 수집 및 분석을 위한 데이터 파이프라인 프로젝트입니다.

## 프로젝트 개요

이 프로젝트는 한국 주식 시장(KRX)의 주가 데이터와 DART(전자공시시스템)의 재무제표 데이터를 수집하고 처리하는 자동화된 파이프라인을 제공합니다. 
Apache Airflow를 사용하여 데이터 수집 워크플로우를 관리하며, 수집된 데이터는 PostgreSQL 데이터베이스에 저장됩니다.

## 주요 기능

- KRX에서 주식 목록 및 가격 데이터 수집
- DART에서 기업 재무제표 데이터 수집
- 수집된 데이터의 자동 처리 및 저장

## 기술 스택

- **Python 3.12.10**: 주요 프로그래밍 언어
- **Apache Airflow**: 워크플로우 관리 및 스케줄링
- **PostgreSQL**: 데이터 저장
- **Docker & Docker Compose**: 컨테이너화 및 배포
- **SQLAlchemy & Alembic**: 데이터베이스 ORM 및 마이그레이션
- **pandas**: 데이터 처리 및 분석

## 프로젝트 구조

```
stock_ai/
├── alembic/                  # 데이터베이스 마이그레이션 관련 파일
├── docker/                   # Docker 관련 파일
│   ├── Dockerfile
│   └── docker-compose.yaml
├── logs/                     # 로그 파일
├── mcp/                      # API 서버 관련 파일
│   └── main.py
├── pipeline/                 # 데이터 파이프라인 관련 파일
│   ├── dags/                 # Airflow DAG 정의
│   │   └── stock/
│   ├── runs/                 # 실행 스크립트
│   │   └── stock/
│   ├── table/                # 데이터베이스 테이블 모델
│   │   └── models/
│   ├── tasks/                # 데이터 수집 및 처리 작업
│   │   └── stock/
│   └── utils/                # 유틸리티 함수
├── requirements.txt          # 프로젝트 의존성
└── README.md                 # 프로젝트 설명
```

## 설치 및 실행 방법

### 사전 요구사항

- Docker 및 Docker Compose 설치
- Python 3.12.10 (로컬 개발 시)

### 설치 및 실행

1. 저장소 클론:
   ```bash
   git clone https://github.com/yourusername/stock_ai.git
   cd stock_ai
   ```

2. 환경 변수 설정:
   ```bash
   cp .env.example .env
   # .env 파일을 편집하여 필요한 환경 변수 설정
   ```

3. Docker Compose로 서비스 실행:
   ```bash
   docker-compose -f docker/docker-compose.yaml up -d
   ```

4. Airflow 웹 인터페이스 접속:
   ```
   http://localhost:8080
   ```
   기본 사용자 이름과 비밀번호는 모두 `airflow`입니다.


## 개발 환경 설정

로컬 개발 환경 설정:

```bash
# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head
```

## 라이센스
