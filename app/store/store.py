from aiohttp.web import Application
from typing import TYPE_CHECKING

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
        
        self.bot_accessor = TelegramBotAccessor(
            token=config['bot']['token']
        )

        self.bot_manager = BotManager(self.bot_accessor)
        
        # TODO: database accessor
        # from app.store.database.accessor import DatabaseAccessor
        # self.database = DatabaseAccessor(config['database'])
    
    async def connect(self):
        await self.bot_accessor.connect()
        # await self.database.connect()
    
    async def disconnect(self):
        await self.bot_accessor.disconnect()
        # await self.database.disconnect()