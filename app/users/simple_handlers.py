"""
Упрощенные API обработчики для пользователей (без Swagger)
"""
from aiohttp import web


async def create_user(request: web.Request):
    """Создать пользователя"""
    try:
        data = await request.json()
        store = request.app.store
        
        # Получаем сессию БД
        async for session in store.database.get_session():
            from app.store.database.user_accessor import UserAccessor
            user_accessor = UserAccessor(session)
            
            # Проверяем, существует ли пользователь
            existing_user = await user_accessor.get_user_by_telegram_id(data['telegram_id'])
            if existing_user:
                return web.json_response(
                    {"success": True, "user": existing_user.to_dict()}
                )
            
            # Создаем нового пользователя
            user = await user_accessor.create_user(
                telegram_id=data['telegram_id'],
                username=data.get('username'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name')
            )
            
            return web.json_response(
                {"success": True, "user": user.to_dict()}
            )
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка создания пользователя: {str(e)}"},
            status=500
        )


async def get_user(request: web.Request):
    """Получить пользователя"""
    try:
        telegram_id = int(request.match_info['telegram_id'])
        store = request.app.store
        
        # Получаем сессию БД
        async for session in store.database.get_session():
            from app.store.database.user_accessor import UserAccessor
            user_accessor = UserAccessor(session)
            
            user = await user_accessor.get_user_by_telegram_id(telegram_id)
            if not user:
                return web.json_response(
                    {"success": False, "error": "Пользователь не найден"},
                    status=404
                )
            
            return web.json_response(
                {"success": True, "user": user.to_dict()}
            )
            
    except ValueError:
        return web.json_response(
            {"success": False, "error": "Неверный формат Telegram ID"},
            status=400
        )
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка получения пользователя: {str(e)}"},
            status=500
        )


async def get_users(request: web.Request):
    """Получить список пользователей"""
    try:
        page = int(request.query.get('page', 1))
        limit = int(request.query.get('limit', 20))
        store = request.app.store
        
        # Получаем сессию БД
        async for session in store.database.get_session():
            from app.store.database.user_accessor import UserAccessor
            user_accessor = UserAccessor(session)
            
            users, total = await user_accessor.get_users_paginated(page=page, limit=limit)
            
            return web.json_response({
                "success": True,
                "users": [user.to_dict() for user in users],
                "total": total
            })
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка получения пользователей: {str(e)}"},
            status=500
        )


async def get_users_stats(request: web.Request):
    """Получить статистику пользователей"""
    try:
        page = int(request.query.get('page', 1))
        limit = int(request.query.get('limit', 20))
        sort_by = request.query.get('sort_by', 'total_score')
        store = request.app.store
        
        # Получаем сессию БД
        async for session in store.database.get_session():
            from app.store.database.user_accessor import UserAccessor
            user_accessor = UserAccessor(session)
            
            stats, total = await user_accessor.get_users_stats_paginated(
                page=page, limit=limit, sort_by=sort_by
            )
            
            return web.json_response({
                "success": True,
                "stats": stats,
                "total": total
            })
            
    except Exception as e:
        return web.json_response(
            {"success": False, "error": f"Ошибка получения статистики: {str(e)}"},
            status=500
        )
