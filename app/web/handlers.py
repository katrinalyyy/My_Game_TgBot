from aiohttp import web

from .schemas import ErrorResponseSchema, HealthCheckResponseSchema

__all__ = ("health_check",)


def health_check(request: web.Request):
    try:
        store = request.app.store

        bot_running = False
        if store and hasattr(store, "bot_manager"):
            bot_running = store.bot_manager.is_running

        # пофиксила - Marshmallow для сериализации ответа
        schema = HealthCheckResponseSchema()
        response_data = {
            "status": "ok",
            "bot_running": bot_running
        }
        
        return web.json_response(schema.dump(response_data))
    
    except Exception as e:
        # пофиксила - обработка ошибок с Marshmallow
        error_schema = ErrorResponseSchema()
        error_data = {
            "error": f"Internal server error: {e!s}",
            "code": 500
        }
        return web.json_response(
            error_schema.dump(error_data), 
            status=500
        )
