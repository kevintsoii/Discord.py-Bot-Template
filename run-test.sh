#!/bin/bash

docker-compose up -d

if [ -d ".venv/bin" ]; then
    source .venv/bin/activate
fi

pip install -r requirements.txt

python -B bot.py --development
