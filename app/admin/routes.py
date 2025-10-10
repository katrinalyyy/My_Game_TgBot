"""
API маршруты для администратора
"""
from aiohttp.web import Application

from .handlers import (
    create_category, get_categories,
    create_question, get_questions,
    get_games, get_system_stats
)

__all__ = ("setup_admin_routes",)


def setup_admin_routes(app: Application):
    
    app.router.add_post("/api/v1/admin/categories", create_category)
    app.router.add_get("/api/v1/admin/categories", get_categories)
    
    app.router.add_post("/api/v1/admin/questions", create_question)
    app.router.add_get("/api/v1/admin/questions", get_questions)
    
    app.router.add_get("/api/v1/admin/games", get_games)
    
    app.router.add_get("/api/v1/admin/stats", get_system_stats)
