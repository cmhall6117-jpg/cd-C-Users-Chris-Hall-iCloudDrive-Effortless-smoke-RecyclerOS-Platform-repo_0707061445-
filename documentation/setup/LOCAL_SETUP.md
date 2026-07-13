# Local Development Setup

Required:
- Flutter SDK
- Visual Studio Code
- Flutter VS Code extension
- Git
- Android Studio / Android SDK
- Python 3.11+
- Docker Desktop

Commands:
```bash
flutter doctor
docker compose up -d
cd services/api
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```
