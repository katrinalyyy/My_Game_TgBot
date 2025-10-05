from aiohttp.web import Application as AiohttpApplication
import yaml
import os
from app.store.store import Store
from app.web.routes import setup_routes
from app.web.mw import setup_middlewares

__all__ = ("Application", "setup_app")


class Application(AiohttpApplication):
    config = None
    store = None
    database = None


def setup_app(config_path: str = "etc/config.yaml") -> Application:
    with open(config_path, 'r') as f:
        raw_config = yaml.safe_load(f)
    
    config = _substitute_env_vars(raw_config)
    
    app = Application()
    app.config = config
    
    app.store = Store(app)
    
    setup_middlewares(app)
    
    setup_routes(app)
    
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    
    return app


def _substitute_env_vars(config: dict) -> dict:
    # подстановка переменных окружения
    if isinstance(config, dict):
        return {k: _substitute_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_substitute_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
        # тк формат ${VAR_NAME:default_value}
        var_expr = config[2:-1]
        if ':' in var_expr:
            var_name, default = var_expr.split(':', 1)
            return os.getenv(var_name, default)
        else:
            return os.getenv(var_expr, config)
    return config


# запуск бота
async def on_startup(app: Application):
    print("Starting application...")
    
    # к БД
    # await app.store.database.connect()

    await app.store.connect()
    await app.store.bot_manager.start()
    print("Application started!")


# если стопаем бота
async def on_cleanup(app: Application):
    print("Shutting down application...")
    await app.store.bot_manager.stop()
    await app.store.disconnect()
    print("Application stopped!")