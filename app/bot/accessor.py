from typing import Any

import aiohttp
from marshmallow import ValidationError

from .schemas import TelegramResponseSchema


class TelegramBotAccessor:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.session: aiohttp.ClientSession | None = None

    async def connect(self):
        self.session = aiohttp.ClientSession()
        print("Telegram Bot API connected")

    async def disconnect(self):
        if self.session:
            await self.session.close()
            print("Telegram Bot API disconnected")

    async def _make_request(self, method: str, **params) -> dict[str, Any]:
        url = f"{self.base_url}/{method}"  # простой вариант работает лучше
        
        if method == "getMe":
            async with self.session.get(url) as response:
                result = await response.json()
        else:
            async with self.session.post(url, json=params) as response:
                result = await response.json()

        if not result.get("ok"):
            print(f"Telegram API error: {result}")
            return {}

        return result.get("result", {})

    async def get_updates(
        self, offset: int | None = None, timeout: int = 30
    ) -> list[dict]:
        params = {
            "timeout": timeout,
            "allowed_updates": ["message", "callback_query"],
        }

        if offset is not None:
            params["offset"] = offset

        result = await self._make_request("getUpdates", **params)
        return result if isinstance(result, list) else []

    async def send_message(
        self, chat_id: int, text: str, reply_markup: dict | None = None
    ) -> dict:
        params = {"chat_id": chat_id, "text": text}

        if reply_markup:
            params["reply_markup"] = reply_markup

        return await self._make_request("sendMessage", **params)

    async def send_message_with_keyboard(
        self, chat_id: int, text: str, buttons: list[list[dict]]
    ) -> dict:
        keyboard = {"inline_keyboard": buttons}

        return await self.send_message(chat_id, text, reply_markup=keyboard)

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: str | None = None,
        show_alert: bool = False,
    ):
        params = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert,
        }

        if text:
            params["text"] = text

        return await self._make_request("answerCallbackQuery", **params)

    async def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup: dict | None = None,
    ):
        params = {"chat_id": chat_id, "message_id": message_id, "text": text}

        if reply_markup:
            params["reply_markup"] = reply_markup

        return await self._make_request("editMessageText", **params)

    async def get_me(self) -> dict:
        # инфа о боте
        return await self._make_request("getMe")
