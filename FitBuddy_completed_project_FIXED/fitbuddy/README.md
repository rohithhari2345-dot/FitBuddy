# FitBuddy — AI Fitness Plan Generator

Complete FastAPI + Jinja2 + SQLite project based on the supplied FitBuddy requirements.

Features:
- adult user profile form
- structured 7-day workout plan generation
- nutrition/recovery tip generation
- SQLite persistence with SQLAlchemy
- feedback-based plan updates
- admin-style user/plan view
- FastAPI /docs
- local fallback when no Gemini API key is configured

This is a general wellness demo for adults (18+), not medical advice.

## Setup

Windows:
```powershell
python -m venv fitbuddy-env
fitbuddy-env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000 and /docs.

Add GEMINI_API_KEY to .env for live Gemini generation. Without it, the app uses a deterministic local fallback so the complete application flow still works.

The project uses Google's current `google-genai` Python SDK. Model names are configurable through `.env`.
