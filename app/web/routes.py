from aiohttp.web import Application

from app.web.handlers import api_info, health_check
from app.game.routes import setup_game_routes
from app.users.routes import setup_user_routes
from app.admin.routes import setup_admin_routes

__all__ = ("setup_routes",)


def setup_routes(app: Application):
    app.router.add_get("/", api_info)
    app.router.add_get("/health", health_check)
    
    setup_game_routes(app)
    setup_user_routes(app)
    setup_admin_routes(app)
