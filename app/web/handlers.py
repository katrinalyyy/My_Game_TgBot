from aiohttp import web

__all__ = ("health_check",)


async def health_check(request: web.Request):
    store = request.app.store

    bot_running = False
    if store and hasattr(store, "bot_manager"):
        bot_running = store.bot_manager.is_running

    return web.json_response({"status": "ok", "bot_running": bot_running})
