
아키텍쳐 1

E : API수집 Postgresql(원본)
L : Postgresql저장(원본)
T : Postgresql(원본) -> Postgresql(처리)
사용기술 : Airflow / Postgresql / polars

아키텍쳐 2

E : API수집 ice burg(원본)
L : ice burg저장(원본)
T : ice burg(원본) -> Ice Burg(처리)
사용기술 : Airflow / Ice Burg / Spark / Minio


MCP 설정
### 1. node.js v18 + 설치
- apt insatll nodejs
- node -v

### 2. npm 설치
- apt install npm 

### 3. Pycharm 플러그인 설치
- Ai Assistant
- MCP Server

### 4. MCP 서버 구성
항목	값
- Name: 자유
- Command: npx
- Arguments: -y @jetbrains/mcp-proxy
- Environment: Variables	없음 (또는 필요한 경우 IDE_PORT=63342 등 지정 가능)
- Working Directory: 프로젝트 루트 or /tmp

### 5. 서버 동작 확인
- HOST=0.0.0.0 npx -y @jetbrains/mcp-proxy
