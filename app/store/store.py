import os
from typing import TYPE_CHECKING

from aiohttp.web import Application

if TYPE_CHECKING:
    from app.bot.accessor import TelegramBotAccessor
    from app.bot.manager import BotManager

__all__ = ("Store",)


class Store:
    def __init__(self, app: Application):
        self.app = app

        from app.bot.accessor import TelegramBotAccessor
        from app.bot.manager import BotManager

        config = app.config
        
        # DEBUG
        print(f"DEBUG in Store: config['bot']['token'] = {config.get('bot', {}).get('token', 'NOT_IN_CONFIG')[:20]}...")
        print(f"DEBUG in Store: os.getenv('BOT_TOKEN') = {os.getenv('BOT_TOKEN', 'NOT_IN_ENV')[:20]}...")

        self.bot_accessor = TelegramBotAccessor(token=config["bot"]["token"])

        self.bot_manager = BotManager(self.bot_accessor)

        from app.database import get_database
        self.database = get_database(app)

    async def connect(self):
        await self.bot_accessor.connect()

    async def disconnect(self):
        await self.bot_accessor.disconnect()