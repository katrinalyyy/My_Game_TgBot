import os
import yaml
from aiohttp.web import Application as AiohttpApplication

from app.database import setup_database
from app.store.store import Store
from app.web.mw import setup_middlewares
from app.web.routes import setup_routes

__all__ = ("Application", "setup_app")


class Application(AiohttpApplication):
    config = None
    store = None
    database = None


def setup_app(config_path: str = "etc/config.yaml", env_vars: dict = None) -> Application:
    env_vars = env_vars or {}
    
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    # подстановка переменных окружения
    config = _substitute_env_vars(raw_config, env_vars)

    app = Application()
    app.config = config
    
    setup_database(app)
    app.store = Store(app)

    setup_middlewares(app)
    setup_routes(app)

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    return app

# подстановка переменных окружения
def _substitute_env_vars(config: dict, env_vars: dict) -> dict:
    if isinstance(config, dict):
        return {k: _substitute_env_vars(v, env_vars) for k, v in config.items()}
    if isinstance(config, list):
        return [_substitute_env_vars(item, env_vars) for item in config]
    if isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        var_expr = config[2:-1]
        if ":" in var_expr:
            var_name, default = var_expr.split(":", 1)
            return env_vars.get(var_name, os.getenv(var_name, default))
        return env_vars.get(var_expr, os.getenv(var_expr, config))
    return config

# запуск бота
async def on_startup(app: Application):
    print("Starting application...")
    await app.store.connect()
    await app.store.bot_manager.start()
    print("Application started!")


async def on_cleanup(app: Application):
    print("Shutting down application...")
    await app.store.bot_manager.stop()
    await app.store.disconnect()
    print("Application stopped!")