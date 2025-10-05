from aiohttp import web
from dotenv import load_dotenv

from app.web.app import setup_app

load_dotenv()

# start
if __name__ == "__main__":
    app = setup_app()
    web.run_app(
        app, host=app.config["web"]["host"], port=app.config["web"]["port"]
    )
