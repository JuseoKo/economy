MCP 설정
### 1. node.js v20 + 설치
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

### 2. node 버전 확인
node -v   # → v18.x
npm -v    # → v8.x 이상

### 3. Gemini CLI 설치
sudo npm install -g @google/gemini-cli

### 4. Gemini 실행
gemini 

### 5. MCP 서버 연결 설정
sudo nano ~/.gemini/settings.json

{
  "theme": "Atom One",
  "selectedAuthType": "oauth-personal",
  "mcpServers": {
    "httpServer": {
      "httpUrl": "http://localhost:3000/mcp",
      "timeout": 5000
    }
  }
}