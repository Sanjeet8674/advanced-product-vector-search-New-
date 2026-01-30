@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Running Local Demo...
python scripts/run_local_demo.py
pause
