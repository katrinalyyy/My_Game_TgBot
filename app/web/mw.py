import traceback
from collections.abc import Callable

from aiohttp import web

__all__ = ("setup_middlewares",)


@web.middleware
async def error_middleware(request: web.Request, handler: Callable):
    try:
        return await handler(request)
    except web.HTTPException:
        raise
    except Exception as e:
        print(f"Error processing request: {e}")
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)


def setup_middlewares(app: web.Application):
    app.middlewares.append(error_middleware)
