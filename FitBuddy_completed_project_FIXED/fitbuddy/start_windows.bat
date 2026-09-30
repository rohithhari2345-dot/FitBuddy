@echo off
if not exist fitbuddy-env python -m venv fitbuddy-env
call fitbuddy-env\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
uvicorn app.main:app --reload
