"""
Запуск только веб-сервера (без Telegram бота)
"""
import os
from pathlib import Path

from aiohttp import web

from app.web.app import setup_app

# загрузка переменных из .env
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'

env_vars = {}

if ENV_FILE.exists():
    with open(ENV_FILE, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line_content = line.strip()
            if line_content and not line_content.startswith('#') and '=' in line_content:
                key, value = line_content.split('=', 1)
                env_vars[key.strip()] = value.strip()
                os.environ[key.strip()] = value.strip()

if __name__ == "__main__":
    print("🚀 Запуск веб-сервера...")
    print(f"📁 Рабочая директория: {BASE_DIR}")
    
    try:
        app = setup_app(env_vars=env_vars)
        print("✅ Приложение создано успешно")
        
        # Проверяем маршруты
        routes = []
        for route in app.router.routes():
            routes.append(f"{route.method} {route.resource}")
        
        print(f"📋 Зарегистрировано {len(routes)} маршрутов:")
        for route in routes:
            print(f"  - {route}")
        
        host = app.config["web"]["host"]
        port = app.config["web"]["port"]
        print(f"🌐 Запуск сервера на {host}:{port}")
        
        web.run_app(app, host=host, port=port)
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
