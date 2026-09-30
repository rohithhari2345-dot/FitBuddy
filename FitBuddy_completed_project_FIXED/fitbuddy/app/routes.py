from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import SessionLocal, UserPlan
from .gemini_generator import (
    generate_nutrition_tip_with_flash,
    generate_workout_gemini,
)
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "title": "FitBuddy — AI Fitness Plan Generator"},
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"request": request, "title": "FitBuddy", "error": str(exc)},
            status_code=422,
        )

    user = data.model_dump()
    plan = generate_workout_gemini(user)
    tip = generate_nutrition_tip_with_flash(user)

    record = UserPlan(**user, original_plan=plan, nutrition_tip=tip)
    db.add(record)
    db.commit()
    db.refresh(record)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "request": request,
            "title": "Your FitBuddy Plan",
            "record": record,
            "message": None,
        },
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    record_id: int = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    payload = FeedbackRequest(record_id=record_id, feedback=feedback)
    record = db.get(UserPlan, payload.record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    user = {
        "username": record.username,
        "user_id": record.user_id,
        "age": record.age,
        "weight": record.weight,
        "goal": record.goal,
        "intensity": record.intensity,
    }
    record.feedback = payload.feedback
    record.updated_plan = update_workout_plan(
        user, record.original_plan, payload.feedback
    )
    db.commit()
    db.refresh(record)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "request": request,
            "title": "Updated FitBuddy Plan",
            "record": record,
            "message": "Your plan has been updated based on your feedback.",
        },
    )


@router.get("/admin", response_class=HTMLResponse)
def all_users(
    request: Request,
    token: str | None = None,
    db: Session = Depends(get_db),
):
    configured = os.getenv("ADMIN_TOKEN", "").strip()
    if configured and token != configured:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    users = db.query(UserPlan).order_by(UserPlan.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"request": request, "title": "FitBuddy Admin", "users": users},
    )


@router.get("/api/health")
def health():
    return {"status": "ok", "service": "fitbuddy"}


@router.get("/api/users")
def api_users(db: Session = Depends(get_db)):
    users = db.query(UserPlan).order_by(UserPlan.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "user_id": u.user_id,
            "username": u.username,
            "age": u.age,
            "goal": u.goal,
            "intensity": u.intensity,
            "has_updated_plan": bool(u.updated_plan),
        }
        for u in users
    ]
