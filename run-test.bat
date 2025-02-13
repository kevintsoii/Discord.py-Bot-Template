@echo off

if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
)

pip install -r requirements.txt

python -B bot.py --development

pause