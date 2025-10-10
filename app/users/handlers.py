"""
API обработчики для пользователей
"""
from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema, querystring_schema

from .schemas import (
    CreateUserRequestSchema, UpdateUserRequestSchema,
    UserResponseSchema, UsersListResponseSchema, UserStatsResponseSchema
)
from app.common.schemas import PaginationQuerySchema, UserStatsQuerySchema


@docs(
    tags=["users"],
    summary="Создать пользователя",
    description="Создает нового пользователя в системе"
)
@request_schema(CreateUserRequestSchema())
@response_schema(UserResponseSchema())
async def create_user(request: web.Request):
    try:
        data = await request.json()
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.store.database.user_accessor import UserAccessor
            user_accessor = UserAccessor(session)
            
            existing_user = await user_accessor.get_user_by_telegram_id(data['telegram_id'])
            if existing_user:
                return web.json_response(
                    {"success": True, "user": existing_user.to_dict()}
                )
            
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


@docs(
    tags=["users"],
    summary="Получить пользователя",
    description="Возвращает информацию о пользователе по Telegram ID"
)
@response_schema(UserResponseSchema())
async def get_user(request: web.Request):
    try:
        telegram_id = int(request.match_info['telegram_id'])
        store = request.app.store
        
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


@docs(
    tags=["users"],
    summary="Обновить пользователя",
    description="Обновляет информацию о пользователе"
)
@request_schema(UpdateUserRequestSchema())
@response_schema(UserResponseSchema())
async def update_user(request: web.Request):
    try:
        telegram_id = int(request.match_info['telegram_id'])
        data = await request.json()
        store = request.app.store
        
        async for session in store.database.get_session():
            from app.store.database.user_accessor import UserAccessor
            user_accessor = UserAccessor(session)
            
            user = await user_accessor.update_user(
                telegram_id=telegram_id,
                username=data.get('username'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name')
            )
            
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
            {"success": False, "error": f"Ошибка обновления пользователя: {str(e)}"},
            status=500
        )


@docs(
    tags=["users"],
    summary="Получить список пользователей",
    description="Возвращает список всех пользователей с пагинацией"
)
@querystring_schema(PaginationQuerySchema())
@response_schema(UsersListResponseSchema())
async def get_users(request: web.Request):
    try:
        page = int(request.query.get('page', 1))
        limit = int(request.query.get('limit', 20))
        store = request.app.store
        
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


@docs(
    tags=["users"],
    summary="Получить статистику пользователей",
    description="Возвращает топ пользователей по различным метрикам"
)
@querystring_schema(UserStatsQuerySchema())
@response_schema(UserStatsResponseSchema())
async def get_users_stats(request: web.Request):
    try:
        page = int(request.query.get('page', 1))
        limit = int(request.query.get('limit', 20))
        sort_by = request.query.get('sort_by', 'total_score')
        store = request.app.store
        
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
