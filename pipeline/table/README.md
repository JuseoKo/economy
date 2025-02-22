### 1. 초기화
alembic init alembic

### 2. 마이그레이션 파일 생성
alembic revision --autogenerate -m "메세지"

### 3. 마이그레이션 적용
alembic upgrade head

### 4. 마이그레이션 확인
alembic current