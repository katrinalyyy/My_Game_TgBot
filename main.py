from aiohttp import web
from app.web.app import setup_app
from dotenv import load_dotenv

load_dotenv()

# start
if __name__ == "__main__":
    app = setup_app()
    web.run_app(
        app,
        host=app.config['web']['host'],
        port=app.config['web']['port']
    )