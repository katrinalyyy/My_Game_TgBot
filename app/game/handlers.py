"""
API обработчики для игр
"""
from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema, querystring_schema
from marshmallow import fields

from .schemas import (
    CreateGameRequestSchema, GameResponseSchema,
    JoinGameRequestSchema, GameBoardResponseSchema,
    SelectQuestionRequestSchema, QuestionResponseSchema,
    AnswerRequestSchema, AnswerResponseSchema,
    ChatIdRequestSchema, LeaderboardResponseSchema
)


async def create_game(request: web.Request):
    try:
        data = await request.json()
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.game.game_manager import GameManager
            game_manager = GameManager(session)
            
            result = await game_manager.start_new_game(
                chat_id=data['chat_id'],
                host_telegram_id=data['host_telegram_id']
            )
            
            return web.json_response(result)
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка создания игры: {str(e)}"},
            status=500
        )


async def join_game(request: web.Request):
    try:
        data = request['json']
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.game.game_manager import GameManager
            game_manager = GameManager(session)
            
            result = await game_manager.add_player(
                chat_id=data['chat_id'],
                player_telegram_id=data['player_telegram_id'],
                player_username=data.get('username'),
                player_first_name=data.get('first_name')
            )
            
            return web.json_response(result)
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка присоединения: {str(e)}"},
            status=500
        )


@docs(
    tags=["games"],
    summary="Начать игру",
    description="Начинает игру после набора игроков"
)
@request_schema(ChatIdRequestSchema())
@response_schema(GameResponseSchema())
async def begin_game(request: web.Request):
    try:
        data = request['json']
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.game.game_manager import GameManager
            game_manager = GameManager(session)
            
            result = await game_manager.begin_game(data['chat_id'])
            return web.json_response(result)
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка начала игры: {str(e)}"},
            status=500
        )


@docs(
    tags=["games"],
    summary="Получить игровую доску",
    description="Возвращает текущее состояние игровой доски"
)
@request_schema(ChatIdRequestSchema())
@response_schema(GameBoardResponseSchema())
async def get_game_board(request: web.Request):
    try:
        data = request['json']
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.game.game_manager import GameManager
            game_manager = GameManager(session)
            
            result = await game_manager.get_game_board(data['chat_id'])
            return web.json_response(result)
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка получения доски: {str(e)}"},
            status=500
        )


@docs(
    tags=["games"],
    summary="Выбрать вопрос",
    description="Выбирает вопрос из игровой доски"
)
@request_schema(SelectQuestionRequestSchema())
@response_schema(QuestionResponseSchema())
async def select_question(request: web.Request):
    try:
        data = request['json']
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.game.game_manager import GameManager
            game_manager = GameManager(session)
            
            result = await game_manager.select_question(
                chat_id=data['chat_id'],
                category=data['category'],
                difficulty=data['difficulty']
            )
            return web.json_response(result)
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка выбора вопроса: {str(e)}"},
            status=500
        )


@docs(
    tags=["games"],
    summary="Ответить на вопрос",
    description="Проверяет ответ игрока на выбранный вопрос"
)
@request_schema(AnswerRequestSchema())
@response_schema(AnswerResponseSchema())
async def answer_question(request: web.Request):
    try:
        data = request['json']
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.game.game_manager import GameManager
            game_manager = GameManager(session)
            
            result = await game_manager.check_answer(
                chat_id=data['chat_id'],
                player_telegram_id=data['player_telegram_id'],
                answer_text=data['answer_text']
            )
            return web.json_response(result)
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка проверки ответа: {str(e)}"},
            status=500
        )


@docs(
    tags=["games"],
    summary="Получить таблицу лидеров",
    description="Возвращает текущие результаты игры"
)
@request_schema(ChatIdRequestSchema())
@response_schema(LeaderboardResponseSchema())
async def get_leaderboard(request: web.Request):
    try:
        data = request['json']
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.game.game_manager import GameManager
            game_manager = GameManager(session)
            
            result = await game_manager.get_leaderboard(data['chat_id'])
            return web.json_response(result)
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка получения результатов: {str(e)}"},
            status=500
        )


@docs(
    tags=["games"],
    summary="Завершить игру",
    description="Завершает текущую игру и показывает финальные результаты"
)
@request_schema(ChatIdRequestSchema())
@response_schema(LeaderboardResponseSchema())
async def finish_game(request: web.Request):
    try:
        data = request['json']
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.game.game_manager import GameManager
            game_manager = GameManager(session)
            
            result = await game_manager.finish_game(data['chat_id'])
            return web.json_response(result)
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка завершения игры: {str(e)}"},
            status=500
        )
