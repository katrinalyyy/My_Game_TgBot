# Polling + обработка
import asyncio
from typing import Optional

from app.bot.accessor import TelegramBotAccessor


class BotManager:
    def __init__(self, bot_accessor: TelegramBotAccessor):
        self.bot = bot_accessor
        self.is_running = False
        self.polling_task: Optional[asyncio.Task] = None
        self.offset: Optional[int] = None

    async def start(self):
        if self.is_running:
            print("Bot is already running")
            return

        self.is_running = True

        bot_info = await self.bot.get_me()
        print(f"Bot started: @{bot_info.get('username', 'Unknown')}")

        self.polling_task = asyncio.create_task(self._polling_loop())

    async def stop(self):
        if not self.is_running:
            return

        self.is_running = False

        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass

        print("Bot stopped")

    async def _polling_loop(self):
        print("Starting polling...")

        while self.is_running:
            try:
                updates = await self.bot.get_updates(
                    offset=self.offset, timeout=30
                )

                for update in updates:
                    await self._handle_update(update)

                    self.offset = update["update_id"] + 1

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Polling error: {e}")
                await asyncio.sleep(5)

    async def _handle_update(self, update: dict):
        # обработка текстовых сообщений
        if "message" in update:
            await self._handle_message(update["message"])

        # обработка нажатий на кнопки
        elif "callback_query" in update:
            await self._handle_callback_query(update["callback_query"])

    async def _handle_message(self, message: dict):
        # Echo-бот (дублирует сообщения)
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        # коменды/
        if text.startswith("/"):
            await self._handle_command(chat_id, text, message)
        else:
            # ECHO: дублируем сообщение
            await self.bot.send_message(
                chat_id=chat_id, text=f"Вы написали: {text}"
            )

    async def _handle_command(self, chat_id: int, command: str, message: dict):
        # коменды/ обработка

        if command == "/start":
            await self.bot.send_message(
                chat_id=chat_id,
                text="Привет! Я echo-бот. Напиши мне что-нибудь, и я повторю!",
            )

        elif command == "/help":
            await self.bot.send_message(
                chat_id=chat_id,
                text="Доступные команды:\n/start - начать\n/help - помощь",
            )

        else:
            await self.bot.send_message(
                chat_id=chat_id, text=f"Вы написали команду: {command}"
            )

    async def _handle_callback_query(self, callback_query: dict):
        query_id = callback_query["id"]
        data = callback_query.get("data", "")

        # ответ на callback
        await self.bot.answer_callback_query(
            callback_query_id=query_id, text=f"Вы нажали: {data}"
        )
