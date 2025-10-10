"""
API маршруты для игр
"""
from aiohttp.web import Application

from .handlers import (
    create_game, join_game, begin_game, get_game_board,
    select_question, answer_question, get_leaderboard, finish_game
)

__all__ = ("setup_game_routes",)


def setup_game_routes(app: Application):
    
    app.router.add_post("/api/v1/games", create_game)
    app.router.add_post("/api/v1/games/join", join_game)
    app.router.add_post("/api/v1/games/begin", begin_game)
    app.router.add_post("/api/v1/games/finish", finish_game)
    
    app.router.add_post("/api/v1/games/board", get_game_board)
    app.router.add_post("/api/v1/games/select-question", select_question)
    app.router.add_post("/api/v1/games/answer", answer_question)
    app.router.add_post("/api/v1/games/leaderboard", get_leaderboard)
