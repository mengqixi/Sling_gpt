# 女包 AI 生图工具

项目说明见 [docs/README.md](docs/README.md)。

快速启动：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

另开终端：

```powershell
cd frontend
npm install
npm run dev
```
