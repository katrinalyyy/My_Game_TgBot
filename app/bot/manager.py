import asyncio
import time
from typing import Optional

from app.bot.accessor import TelegramBotAccessor
from app.game import GameManager


class BotManager:    
    def __init__(self, bot_accessor: TelegramBotAccessor):
        self.bot = bot_accessor
        self.is_running = False
        self.polling_task: Optional[asyncio.Task] = None
        self.offset: Optional[int] = None
        
        self.app = None 
    
    def set_app(self, app):
        self.app = app
    
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

    async def _handle_update(self, update: dict):
        if "message" in update:
            await self._handle_message(update["message"])
        elif "callback_query" in update:
            await self._handle_callback(update["callback_query"])

    async def _handle_message(self, message: dict):
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user = message["from"]
        
        if chat_id > 0:
            await self.bot.send_message(
                chat_id=chat_id,
                text="⚠️ Я работаю только в групповых чатах! Добавьте меня в группу."
            )
            return
        
        if text.startswith("/"):
            await self._handle_command(chat_id, text, user)

    async def _handle_command(self, chat_id: int, command: str, user: dict):
        user_id = user["id"]
        username = user.get("username")
        first_name = user.get("first_name", "Игрок")
        
        try:
            async for session in self.app['database'].get_session():
                game_manager = GameManager(session)
                
                await self._process_command_with_manager(
                    chat_id, command, user_id, username, first_name, game_manager
                )
                break
        
        except Exception as e:
            print(f"Error handling command {command}: {e}")
            await self.bot.send_message(
                chat_id=chat_id,
                text="❌ Произошла ошибка при обработке команды. Попробуйте позже."
            )
    
    async def _process_command_with_manager(
        self, 
        chat_id: int, 
        command: str, 
        user_id: int, 
        username: str, 
        first_name: str, 
        game_manager
    ):
        if command == "/start_game":
            result = await game_manager.start_new_game(
                chat_id=chat_id,
                host_telegram_id=user_id,
                host_username=username,
                host_first_name=first_name
            )
            
            if result["success"]:
                text = (
                    f"🎮 {result['message']}\n\n"
                    f"Ожидаем игроков...\n"
                    f"Минимум 2 человека.\n\n"
                    f"Чтобы присоединиться, напишите /join\n"
                    f"Для начала игры: /begin"
                )
            else:
                text = f"❌ {result['error']}"
            
            await self.bot.send_message(chat_id=chat_id, text=text)
        
        elif command == "/join":
            result = await game_manager.add_player(
                chat_id=chat_id,
                player_telegram_id=user_id,
                player_username=username,
                player_first_name=first_name
            )
            
            if result["success"]:
                text = f"✅ {first_name} присоединился к игре! (Всего игроков: {result['total_players']})"
            else:
                text = f"❌ {result['error']}"
            
            await self.bot.send_message(chat_id=chat_id, text=text)
        
        elif command == "/begin":
            result = await game_manager.begin_game(chat_id)
            
            if result["success"]:
                text = (
                    f"🎉 Игра начинается!\n\n"
                    f"Первым выбирает вопрос: {result['first_player']['first_name']}\n"
                    f"Всего вопросов: {result['total_questions']}\n\n"
                    f"Используйте /board чтобы увидеть доску"
                )
            else:
                text = f"❌ {result['error']}"
            
            await self.bot.send_message(chat_id=chat_id, text=text)
        
        elif command == "/board":
            board_result = await game_manager.get_game_board(chat_id)
            
            if not board_result["success"]:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ {board_result['error']}"
                )
                return
            
            board = board_result["board"]
            text = "🎯 ИГРОВАЯ ДОСКА\n\n"
            
            for category, questions in board.items():
                available = [str(q["difficulty"]) for q in questions if not q["is_answered"]]
                if available:
                    text += f"📌 {category}: {', '.join(available)}\n"
            
            text += "\n💡 Выберите вопрос: /select Категория Сложность"
            text += "\n(Например: /select География 100)"
            
            await self.bot.send_message(chat_id=chat_id, text=text)
        
        elif command.startswith("/select"):
            parts = command.split(maxsplit=2)
            if len(parts) < 3:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Формат: /select Категория Сложность\nПример: /select География 100"
                )
                return
            
            category = parts[1]
            try:
                difficulty = int(parts[2])
            except ValueError:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Сложность должна быть числом"
                )
                return
            
            question_result = await game_manager.select_question(
                chat_id=chat_id,
                category=category,
                difficulty=difficulty,
                selecting_player_id=user_id
            )
            
            if not question_result["success"]:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ {question_result['error']}"
                )
                return
            
            question = question_result["question"]
            
            turn_info = await game_manager.get_current_turn_info(chat_id)
            current_player = turn_info.get("current_player", {})
            
            text = (
                f"❓ ВОПРОС за {question['difficulty']} очков\n"
                f"📚 {question['category']}\n\n"
                f"{question['text']}\n\n"
                f"🎯 Выбирает: {current_player.get('first_name', 'Игрок')}\n"
                f"⏰ У вас 30 секунд на ответ!\n\n"
                f"💡 Чтобы ответить: /answer ваш_ответ"
            )
            
            game = await game_manager.game_accessor.get_active_game_in_chat(chat_id)
            await game_manager.game_accessor.update_game_metadata(
                game.id,
                {"turn_start_time": time.time()}
            )
            
            await self.bot.send_message(chat_id=chat_id, text=text)
            
            asyncio.create_task(self._handle_turn_timeout(chat_id, user_id))
        
        elif command.startswith("/answer"):
            answer_text = command.replace("/answer", "").strip()
            if not answer_text:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Укажите ответ: /answer ваш_ответ"
                )
                return
            
            result = await game_manager.check_answer(
                chat_id=chat_id,
                player_telegram_id=user_id,
                answer_text=answer_text
            )
            
            if not result["success"]:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ {result['error']}"
                )
                return
            
            if result["is_correct"]:
                text = (
                    f"✅ Правильно! +{result['score_change']} очков\n"
                    f"🏆 {first_name} получает {result['score_change']} очков!\n\n"
                    f"🎯 Следующий ход выбирает новый игрок!"
                )
            else:
                if result["is_race_mode"]:
                    text = (
                        f"❌ Неправильно! {result['score_change']} очков\n"
                        f"📉 {first_name} теряет {abs(result['score_change'])} очков\n\n"
                        f"🏃‍♂️ Время вышло! Теперь гонка!\n"
                        f"Первым ответит - получит очки!"
                    )
                else:
                    text = (
                        f"❌ Неправильно! {result['score_change']} очков\n"
                        f"📉 {first_name} теряет {abs(result['score_change'])} очков\n\n"
                        f"🏃‍♂️ Время вышло! Теперь гонка!\n"
                        f"Первым ответит - получит очки!"
                    )
            
            await self.bot.send_message(chat_id=chat_id, text=text)
        
        elif command == "/score":
            leaderboard_result = await game_manager.get_leaderboard(chat_id)
            
            if not leaderboard_result["success"]:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ {leaderboard_result['error']}"
                )
                return
            
            text = "🏆 ТЕКУЩИЕ РЕЗУЛЬТАТЫ\n\n"
            for idx, player in enumerate(leaderboard_result["leaderboard"], 1):
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "  "
                text += f"{medal} {idx}. {player['first_name']}: {player['score']} очков\n"
            
            await self.bot.send_message(chat_id=chat_id, text=text)
        
        elif command == "/stop_game":
            finish_result = await game_manager.finish_game(chat_id)
            
            if not finish_result["success"]:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ {finish_result['error']}"
                )
                return
            
            text = "🏁 ИГРА ЗАВЕРШЕНА!\n\n🏆 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:\n\n"
            for idx, player in enumerate(finish_result["leaderboard"], 1):
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "  "
                text += f"{medal} {idx}. {player['first_name']}: {player['score']} очков\n"
            
            await self.bot.send_message(chat_id=chat_id, text=text)
        
        elif command == "/help":
            text = (
                "📖 КОМАНДЫ ИГРЫ:\n\n"
                "🎮 /start_game - создать игру\n"
                "👥 /join - присоединиться\n"
                "▶️ /begin - начать игру\n"
                "🎯 /board - показать доску\n"
                "📌 /select - выбрать вопрос\n"
                "🏆 /score - таблица результатов\n"
                "🛑 /stop_game - завершить игру"
            )
            await self.bot.send_message(chat_id=chat_id, text=text)
    
    async def _handle_turn_timeout(self, chat_id: int, selecting_player_id: int):
        try:
            await asyncio.sleep(30)
            
            async for session in self.app['database'].get_session():
                from app.game.game_manager import GameManager
                game_manager = GameManager(session)
                
                game = await game_manager.game_accessor.get_active_game_in_chat(chat_id)
                if not game:
                    return
                
                current_question_id = game.game_metadata.get("current_question_id")
                if not current_question_id:
                    return
                
                current_player_id = game.game_metadata.get("current_player_id")
                if current_player_id != selecting_player_id:
                    return
                
                await game_manager.game_accessor.update_game_metadata(
                    game.id,
                    {
                        "is_race_mode": True,
                        "race_start_time": time.time()
                    }
                )
                
                user = await game_manager.user_accessor.get_user_by_telegram_id(selecting_player_id)
                player_name = user.first_name if user else "Игрок"
                
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"⏰ Время вышло!\n"
                        f"🏃‍♂️ Теперь гонка! Любой игрок может ответить первым!\n"
                        f"💡 Используйте: /answer ваш_ответ"
                    )
                )
                
        except Exception as e:
            print(f"Error in turn timeout handler: {e}")

    async def _handle_callback(self, callback_query: dict):
        query_id = callback_query["id"]
        
        await self.bot.answer_callback_query(
            callback_query_id=query_id,
            text="Кнопки пока не реализованы"
        )
