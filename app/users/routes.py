"""
API маршруты для пользователей
"""
from aiohttp.web import Application

from .handlers import (
    create_user, get_user, get_users, get_users_stats
)

__all__ = ("setup_user_routes",)


def setup_user_routes(app: Application):
    
    app.router.add_post("/api/v1/users", create_user)
    app.router.add_get("/api/v1/users", get_users)
    app.router.add_get("/api/v1/users/{telegram_id}", get_user)
    
    app.router.add_get("/api/v1/users/stats", get_users_stats)