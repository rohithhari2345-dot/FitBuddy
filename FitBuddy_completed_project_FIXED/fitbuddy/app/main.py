from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="FitBuddy — AI Fitness Plan Generator",
    description="AI-powered 7-day adult wellness plan generator with feedback updates.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    init_db()
