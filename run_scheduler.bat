@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt
python machine_shop_scheduler.py
pause
