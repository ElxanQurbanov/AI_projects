@echo off
cd /d %~dp0
call .venv\Scripts\activate
python jarvis_v1.py
pause