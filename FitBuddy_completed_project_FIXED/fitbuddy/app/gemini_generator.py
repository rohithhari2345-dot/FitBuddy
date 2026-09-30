from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

WORKOUT_MODEL = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-3.8-flash")
NUTRITION_MODEL = os.getenv("GEMINI_NUTRITION_MODEL", "gemini-3.8-flash")

try:
    from google import genai
except ImportError:
    genai = None


def _client():
    key = os.getenv("GEMINI_API_KEY")
    if not key or genai is None:
        return None
    return genai.Client(api_key=key)


def _generate(prompt: str, model: str) -> str | None:
    client = _client()
    if client is None:
        return None
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return getattr(response, "text", None)
    except Exception:
        return None


def _fallback_plan(user: dict[str, Any]) -> str:
    return f'''7-DAY FITBUDDY PLAN

Profile
- Goal: {user["goal"]}
- Intensity: {user["intensity"].capitalize()}
- Age: {user["age"]}

Day 1 — Full Body Foundation
Warm-up: 5–10 minutes of easy movement.
Main: squat pattern, push movement, row/pull movement, hip-hinge pattern, light core work.
Cool-down: easy walking and gentle mobility.

Day 2 — Cardio + Mobility
20–30 minutes of comfortable cardio, followed by 10 minutes of mobility.

Day 3 — Upper Body + Core
Warm-up, controlled push/pull exercises, and a short core circuit. Stop if you feel pain.

Day 4 — Recovery
Easy walking and gentle mobility. Keep the effort light.

Day 5 — Lower Body
Controlled leg and hip exercises with comfortable resistance. Focus on technique.

Day 6 — Full Body Conditioning
Short intervals of moderate activity with generous recovery between rounds.

Day 7 — Rest / Optional Easy Activity
Rest, or choose a relaxed walk and mobility session.

Safety notes
- Adjust volume and resistance to your experience level.
- Stop for sharp or worsening pain or concerning symptoms.
- Progress gradually rather than trying to do everything at once.
'''


def generate_workout_gemini(user: dict[str, Any]) -> str:
    prompt = f'''
You are FitBuddy, a general wellness planning assistant for adults.
Create a practical, structured 7-day workout plan from:
username={user["username"]}
age={user["age"]}
weight_kg={user["weight"]}
goal={user["goal"]}
intensity={user["intensity"]}

Requirements:
- Seven clearly labeled days.
- Include warm-up, main work, and cool-down/recovery where appropriate.
- Keep instructions concise and actionable.
- Do not diagnose medical conditions.
- Do not prescribe extreme dieting, starvation, dehydration, or unsafe exercise.
- Tell the user to stop for pain or concerning symptoms and seek professional guidance.
- Do not promise specific body-composition outcomes.
'''
    return _generate(prompt, WORKOUT_MODEL) or _fallback_plan(user)


def generate_nutrition_tip_with_flash(user: dict[str, Any]) -> str:
    prompt = f'''
Give one concise, practical nutrition/recovery tip for an adult fitness user.
Goal: {user["goal"]}
Intensity: {user["intensity"]}
Keep it general wellness advice. Avoid calorie prescriptions, restrictive diets,
supplements, or guaranteed weight-change claims. Return 3–5 sentences.
'''
    return _generate(prompt, NUTRITION_MODEL) or (
        "Build meals around a mix of protein-rich foods, vegetables or fruit, "
        "and a satisfying carbohydrate source. Drink water regularly, especially "
        "around exercise. Give sleep and recovery the same priority as training."
    )


def update_workout_plan(user: dict[str, Any], original_plan: str, feedback: str) -> str:
    prompt = f'''
You are revising an existing adult wellness workout plan.
User goal: {user["goal"]}
Intensity: {user["intensity"]}

Original plan:
{original_plan}

User feedback:
{feedback}

Return a revised 7-day plan. Keep what is working, address the feedback,
and make only reasonable, gradual changes. Avoid unsafe or extreme exercise.
Do not provide medical diagnosis or treatment.
'''
    return _generate(prompt, WORKOUT_MODEL) or (
        original_plan
        + "\n\nUPDATED BASED ON FEEDBACK\n"
        + f"Feedback considered: {feedback}\n"
        + "Use easier or harder versions of movements according to comfort, "
          "while preserving recovery days and gradual progression."
    )
