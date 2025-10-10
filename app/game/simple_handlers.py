"""
Упрощенные API обработчики для игр (без Swagger)
"""
from aiohttp import web


async def create_game(request: web.Request):
    """Создать новую игру"""
    try:
        data = await request.json()
        store = request.app.store
        
        # Получаем сессию БД
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
    """Присоединиться к игре"""
    try:
        data = await request.json()
        store = request.app.store
        
        # Получаем сессию БД
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


async def begin_game(request: web.Request):
    """Начать игру"""
    try:
        data = await request.json()
        store = request.app.store
        
        # Получаем сессию БД
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


async def get_game_board(request: web.Request):
    """Получить игровую доску"""
    try:
        data = await request.json()
        store = request.app.store
        
        # Получаем сессию БД
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


async def select_question(request: web.Request):
    """Выбрать вопрос"""
    try:
        data = await request.json()
        store = request.app.store
        
        # Получаем сессию БД
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


async def answer_question(request: web.Request):
    """Ответить на вопрос"""
    try:
        data = await request.json()
        store = request.app.store
        
        # Получаем сессию БД
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


async def get_leaderboard(request: web.Request):
    """Получить таблицу лидеров"""
    try:
        data = await request.json()
        store = request.app.store
        
        # Получаем сессию БД
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


async def finish_game(request: web.Request):
    """Завершить игру"""
    try:
        data = await request.json()
        store = request.app.store
        
        # Получаем сессию БД
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
