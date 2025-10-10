"""
Упрощенные API обработчики для администратора (без Swagger)
"""
from aiohttp import web


async def create_category(request: web.Request):
    try:
        data = await request.json()
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.store.database.question_accessor import QuestionAccessor
            question_accessor = QuestionAccessor(session)
            
            category = await question_accessor.create_category(
                name=data['name'],
                description=data.get('description')
            )
            
            return web.json_response(
                {"success": True, "category": category.to_dict()}
            )
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка создания категории: {str(e)}"},
            status=500
        )


async def get_categories(request: web.Request):
    """Получить категории"""
    try:
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.store.database.question_accessor import QuestionAccessor
            question_accessor = QuestionAccessor(session)
            
            categories = await question_accessor.get_categories()
            
            return web.json_response({
                "success": True,
                "categories": [category.to_dict() for category in categories],
                "total": len(categories)
            })
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка получения категорий: {str(e)}"},
            status=500
        )


async def create_question(request: web.Request):
    try:
        data = await request.json()
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.store.database.question_accessor import QuestionAccessor
            question_accessor = QuestionAccessor(session)
            
            question = await question_accessor.create_question(
                category_id=data['category_id'],
                question_text=data['question_text'],
                answer_text=data['answer_text'],
                difficulty=data['difficulty']
            )
            
            return web.json_response(
                {"success": True, "question": question.to_dict()}
            )
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка создания вопроса: {str(e)}"},
            status=500
        )


async def get_questions(request: web.Request):
    """Получить вопросы"""
    try:
        category_id = request.query.get('category_id')
        difficulty = request.query.get('difficulty')
        page = int(request.query.get('page', 1))
        limit = int(request.query.get('limit', 20))
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.store.database.question_accessor import QuestionAccessor
            question_accessor = QuestionAccessor(session)
            
            questions, total = await question_accessor.get_questions_paginated(
                category_id=int(category_id) if category_id else None,
                difficulty=int(difficulty) if difficulty else None,
                page=page,
                limit=limit
            )
            
            return web.json_response({
                "success": True,
                "questions": [question.to_dict() for question in questions],
                "total": total
            })
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка получения вопросов: {str(e)}"},
            status=500
        )


async def get_games(request: web.Request):
    """Получить игровые сессии"""
    try:
        page = int(request.query.get('page', 1))
        limit = int(request.query.get('limit', 20))
        active_only = request.query.get('active_only', 'false').lower() == 'true'
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.store.database.game_accessor import GameAccessor
            game_accessor = GameAccessor(session)
            
            games, total = await game_accessor.get_games_paginated(
                page=page, limit=limit, active_only=active_only
            )
            
            return web.json_response({
                "success": True,
                "games": [game.to_dict() for game in games],
                "total": total
            })
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка получения игр: {str(e)}"},
            status=500
        )


async def get_system_stats(request: web.Request):
    """Получить системную статистику"""
    try:
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.store.database.game_accessor import GameAccessor
            from app.store.database.user_accessor import UserAccessor
            from app.store.database.question_accessor import QuestionAccessor
            
            game_accessor = GameAccessor(session)
            user_accessor = UserAccessor(session)
            question_accessor = QuestionAccessor(session)
            
            total_users = await user_accessor.get_users_count()
            total_games = await game_accessor.get_games_count()
            active_games = await game_accessor.get_active_games_count()
            total_questions = await question_accessor.get_questions_count()
            total_categories = await question_accessor.get_categories_count()
            
            stats = {
                "total_users": total_users,
                "total_games": total_games,
                "active_games": active_games,
                "total_questions": total_questions,
                "total_categories": total_categories,
                "questions_by_difficulty": {
                    "100": await question_accessor.get_questions_count_by_difficulty(100),
                    "200": await question_accessor.get_questions_count_by_difficulty(200),
                    "300": await question_accessor.get_questions_count_by_difficulty(300),
                    "400": await question_accessor.get_questions_count_by_difficulty(400),
                    "500": await question_accessor.get_questions_count_by_difficulty(500),
                }
            }
            
            return web.json_response({
                "success": True,
                "stats": stats
            })
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка получения статистики: {str(e)}"},
            status=500
        )
