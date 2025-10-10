from aiohttp import web

from .schemas import ErrorResponseSchema, HealthCheckResponseSchema

__all__ = ("api_info", "health_check")


async def api_info(request: web.Request):
    api_info = {
        "name": "My Game Telegram Bot API",
        "version": "v1",
        "description": "REST API для игры 'Своя игра' в Telegram боте",
        "endpoints": {
            "health": "/health",
            "games": "/api/v1/games",
            "users": "/api/v1/users", 
            "admin": "/api/v1/admin"
        },
        "documentation": "См. файлы API_README.md и API_EXAMPLES.md"
    }
    return web.json_response(api_info)


async def health_check(request: web.Request):
    try:
        store = request.app.store

        bot_running = False
        if store and hasattr(store, "bot_manager"):
            bot_running = store.bot_manager.is_running

        response_data = {
            "status": "ok",
            "bot_running": bot_running,
            "timestamp": "2025-01-09T10:30:00Z"
        }
        
        return web.json_response(response_data)
    
    except Exception as e:
        error_data = {
            "error": f"Internal server error: {e!s}",
            "code": 500
        }
        return web.json_response(error_data, status=500)
