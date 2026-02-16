@echo off
cd /d %~dp0
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
pause
