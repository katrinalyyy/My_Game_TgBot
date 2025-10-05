from aiohttp.web import Application
from app.web.handlers import health_check

__all__ = ("setup_routes",)


def setup_routes(app: Application):
    app.router.add_get('/health', health_check)
    
    # TODO: routes для других модулей
    # from app.users.routes import setup_user_routes
    # setup_user_routes(app)
    #
    # from app.game.routes import setup_game_routes
    # setup_game_routes(app)