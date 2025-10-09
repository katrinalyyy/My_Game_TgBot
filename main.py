import os
from pathlib import Path
from aiohttp import web

# загрузка переменных из .env
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'

env_vars = {}

if ENV_FILE.exists():
    with open(ENV_FILE, 'r', encoding='utf-8-sig') as f:  # utf-8-sig убирает BOM иначе увы
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
                os.environ[key.strip()] = value.strip()

from app.web.app import setup_app

if __name__ == "__main__":
    app = setup_app(env_vars=env_vars)
    web.run_app(
        app, host=app.config["web"]["host"], port=app.config["web"]["port"]
    )