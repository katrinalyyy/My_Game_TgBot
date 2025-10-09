"""
Game Manager - управление логикой игры "Своя игра"
"""
from typing import Optional, List, Dict
from enum import Enum
import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.store.database import UserAccessor, GameAccessor, QuestionAccessor
from app.store.database.models import GameSession, Participant, Question


class GameState(Enum):
    WAITING_PLAYERS = "waiting_players"
    GAME_ACTIVE = "game_active"
    QUESTION_SELECTED = "question_selected"
    ANSWER_TIME = "answer_time"
    GAME_FINISHED = "game_finished"


class GameManager:    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_accessor = UserAccessor(session)
        self.game_accessor = GameAccessor(session)
        self.question_accessor = QuestionAccessor(session)
    
    
    async def start_new_game(
        self,
        chat_id: int,
        host_telegram_id: int,
        host_username: Optional[str] = None,
        host_first_name: Optional[str] = None
    ) -> Dict:
        """
        Начать новую игру
        
        Returns:
            Dict с информацией о созданной игре
        """
        # чек, нет ли активной игры
        existing_game = await self.game_accessor.get_active_game_in_chat(chat_id)
        if existing_game:
            return {
                "success": False,
                "error": "В этом чате уже есть активная игра!"
            }
        
        # создать/получить пользователя (ведущего)
        host = await self.user_accessor.get_or_create_user(
            telegram_id=host_telegram_id,
            username=host_username,
            first_name=host_first_name
        )
        
        # создаю игру
        game = await self.game_accessor.create_game_session(
            chat_id=chat_id,
            host_telegram_id=host_telegram_id
        )
        
        await self.game_accessor.log_event(
            game_session_id=game.id,
            event_type="game_created",
            user_telegram_id=host_telegram_id,
            event_data={"chat_id": chat_id}
        )
        
        return {
            "success": True,
            "game_id": game.id,
            "host": {
                "telegram_id": host.telegram_id,
                "username": host.username,
                "first_name": host.first_name
            },
            "message": f"🎮 Игра создана! Ведущий: {host.first_name or host.username}"
        }
    
    async def add_player(
        self,
        chat_id: int,
        player_telegram_id: int,
        player_username: Optional[str] = None,
        player_first_name: Optional[str] = None
    ) -> Dict:
        """Добавить игрока в игру"""
        game = await self.game_accessor.get_active_game_in_chat(chat_id)
        if not game:
            return {"success": False, "error": "Нет активной игры в этом чате"}
        
        if game.state != GameState.WAITING_PLAYERS.value:
            return {"success": False, "error": "Игра уже началась"}
        
        # чек, не ведущий ли это
        if player_telegram_id == game.host_telegram_id:
            return {"success": False, "error": "Ведущий не может быть игроком"}
        
        # чек, не добавлен ли уже
        participants = await self.game_accessor.get_participants(game.id)
        if any(p.user_telegram_id == player_telegram_id for p in participants):
            return {"success": False, "error": "Вы уже в игре"}
        
        # создать/получить пользователя
        player = await self.user_accessor.get_or_create_user(
            telegram_id=player_telegram_id,
            username=player_username,
            first_name=player_first_name
        )
        
        # + участник
        turn_order = len(participants) + 1
        await self.game_accessor.add_participant(
            game_session_id=game.id,
            user_telegram_id=player_telegram_id,
            turn_order=turn_order
        )
        
        await self.game_accessor.log_event(
            game_session_id=game.id,
            event_type="player_joined",
            user_telegram_id=player_telegram_id
        )
        
        return {
            "success": True,
            "player": {
                "telegram_id": player.telegram_id,
                "username": player.username,
                "first_name": player.first_name
            },
            "total_players": turn_order
        }
    
    async def begin_game(self, chat_id: int) -> Dict:
        """Начать игру (после набора игроков)"""
        game = await self.game_accessor.get_active_game_in_chat(chat_id)
        if not game:
            return {"success": False, "error": "Нет активной игры"}
        
        participants = await self.game_accessor.get_participants(game.id)
        if len(participants) < 2:
            return {
                "success": False,
                "error": "Нужно минимум 2 игрока для начала"
            }
        
        # получаем случайные вопросы
        questions = await self.question_accessor.get_random_questions_for_game(
            num_categories=3,  # 3 категории
            difficulties=[100, 200, 300]  # 3 уровня сложности
        )
        
        if len(questions) < 9:
            return {
                "success": False,
                "error": "Недостаточно вопросов в базе данных"
            }
        
        # создаю игровую доску (если её ещё нет)
        await self.question_accessor.create_game_board(
            game_session_id=game.id,
            questions=questions
        )
        
        # выбираю случайного первого игрока
        first_player = random.choice(participants)
        
        # обновляю состояние игры
        await self.game_accessor.update_game_state(game.id, GameState.GAME_ACTIVE.value)
        
        await self.game_accessor.log_event(
            game_session_id=game.id,
            event_type="game_started",
            event_data={
                "first_player": first_player.user_telegram_id,
                "total_questions": len(questions)
            }
        )
        
        # получаем информацию о первом игроке
        first_player_user = await self.user_accessor.get_user_by_telegram_id(
            first_player.user_telegram_id
        )
        
        return {
            "success": True,
            "first_player": {
                "telegram_id": first_player_user.telegram_id,
                "first_name": first_player_user.first_name,
                "username": first_player_user.username
            },
            "total_questions": len(questions)
        }
    
    # ========================================
    # ИГРА
    # ========================================
    
    async def get_game_board(self, chat_id: int) -> Dict:
        """Получить текущую игровую доску"""
        game = await self.game_accessor.get_active_game_in_chat(chat_id)
        if not game:
            return {"success": False, "error": "Нет активной игры"}
        
        board = await self.question_accessor.get_game_board(game.id)
        
        # группирую по категориям
        from collections import defaultdict
        by_category = defaultdict(list)
        
        for entry in board:
            by_category[entry.category_name].append({
                "difficulty": entry.difficulty,
                "is_answered": entry.is_answered,
                "answered_by": entry.answered_by_telegram_id
            })
        
        # сортирую вопросы в каждой категории
        for category in by_category:
            by_category[category].sort(key=lambda x: x["difficulty"])
        
        return {
            "success": True,
            "board": dict(by_category),
            "game_state": game.state
        }
    
    async def select_question(
        self,
        chat_id: int,
        category: str,
        difficulty: int
    ) -> Dict:
        game = await self.game_accessor.get_active_game_in_chat(chat_id)
        if not game:
            return {"success": False, "error": "Нет активной игры"}
        
        board = await self.question_accessor.get_game_board(game.id)
        
        selected = None
        for entry in board:
            if (entry.category_name == category and 
                entry.difficulty == difficulty and 
                not entry.is_answered):
                selected = entry
                break
        
        if not selected:
            return {"success": False, "error": "Этот вопрос уже отвечен или не существует"}
        
        question = await self.question_accessor.get_question_by_id(selected.question_id)
        
        await self.game_accessor.update_game_state(
            game.id,
            GameState.QUESTION_SELECTED.value
        )
        
        await self.game_accessor.log_event(
            game_session_id=game.id,
            event_type="question_selected",
            event_data={
                "question_id": question.id,
                "category": category,
                "difficulty": difficulty
            }
        )
        
        # сохраняю информацию о выбранном вопросе в metadata игры
        print(f"DEBUG: Saving question ID {question.id} for game {game.id}")
        await self.game_accessor.update_game_metadata(
            game.id,
            {"current_question_id": question.id}
        )
        
        return {
            "success": True,
            "question": {
                "id": question.id,
                "text": question.question_text,
                "category": category,
                "difficulty": difficulty
            }
        }
    
    async def save_current_question(self, chat_id: int, question_id: int):
        """Сохранить текущий выбранный вопрос"""
        game = await self.game_accessor.get_active_game_in_chat(chat_id)
        if not game:
            return
        
        print(f"DEBUG: Saving current question {question_id} for game {game.id}")
        await self.game_accessor.update_game_metadata(
            game.id,
            {"current_question_id": question_id}
        )
    
    async def check_answer(
        self,
        chat_id: int,
        player_telegram_id: int,
        answer_text: str
    ) -> Dict:
        """Проверить ответ игрока"""
        game = await self.game_accessor.get_active_game_in_chat(chat_id)
        if not game:
            return {"success": False, "error": "Нет активной игры"}
        
        # получаю ID текущего вопроса из metadata
        current_question_id = game.game_metadata.get("current_question_id")
        if not current_question_id:
            return {"success": False, "error": "Не выбран вопрос для ответа"}
        
        # получаю вопрос
        question = await self.question_accessor.get_question_by_id(current_question_id)
        if not question:
            return {"success": False, "error": "Вопрос не найден"}
        
        print(f"DEBUG: Question ID: {current_question_id}")
        print(f"DEBUG: Question text: {question.question_text}")
        print(f"DEBUG: Correct answer: {question.answer_text}")
        print(f"DEBUG: User answer: {answer_text}")
        
        # чек ответ 
        is_correct = answer_text.strip().lower() == question.answer_text.strip().lower()
        print(f"DEBUG: Is correct: {is_correct}")
        
        # получаю доску для определения сложности
        board = await self.question_accessor.get_game_board(game.id)
        board_entry = next((b for b in board if b.question_id == current_question_id), None)
        
        if not board_entry:
            return {"success": False, "error": "Вопрос не найден на доске"}
        
        score_change = board_entry.difficulty if is_correct else -board_entry.difficulty
        
        # обновляю счёт игрока
        await self.game_accessor.update_participant_score(
            game_session_id=game.id,
            user_telegram_id=player_telegram_id,
            score_delta=score_change
        )
        
        # если ответ правильный - отмечаю вопрос как отвеченный
        if is_correct:
            await self.question_accessor.mark_question_answered(
                game_session_id=game.id,
                category_name=board_entry.category_name,
                difficulty=board_entry.difficulty,
                answered_by_telegram_id=player_telegram_id
            )
        
        # очищаю текущий вопрос из metadata
        await self.game_accessor.update_game_metadata(
            game.id,
            {"current_question_id": None}
        )
        
        await self.game_accessor.log_event(
            game_session_id=game.id,
            event_type="answer_attempt",
            user_telegram_id=player_telegram_id,
            event_data={
                "question_id": current_question_id,
                "answer": answer_text,
                "is_correct": is_correct,
                "score_change": score_change
            }
        )
        
        await self.game_accessor.update_game_state(game.id, GameState.GAME_ACTIVE.value)
        
        return {
            "success": True,
            "is_correct": is_correct,
            "correct_answer": question.answer_text,
            "score_change": score_change
        }
    
    async def get_leaderboard(self, chat_id: int) -> Dict:
        game = await self.game_accessor.get_active_game_in_chat(chat_id)
        if not game:
            return {"success": False, "error": "Нет активной игры"}
        
        participants = await self.game_accessor.get_participants(game.id)
        
        participants.sort(key=lambda p: p.score, reverse=True)
        
        leaderboard = []
        for p in participants:
            user = await self.user_accessor.get_user_by_telegram_id(p.user_telegram_id)
            leaderboard.append({
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "score": p.score
            })
        
        return {
            "success": True,
            "leaderboard": leaderboard
        }
    
    async def finish_game(self, chat_id: int) -> Dict:
        """Завершить игру"""
        game = await self.game_accessor.get_active_game_in_chat(chat_id)
        if not game:
            return {"success": False, "error": "Нет активной игры"}
        
        leaderboard_data = await self.get_leaderboard(chat_id)
        leaderboard = leaderboard_data["leaderboard"]
        
        for idx, player in enumerate(leaderboard):
            is_winner = idx == 0  
            await self.user_accessor.update_user_stats(
                telegram_id=player["telegram_id"],
                total_games_delta=1,
                total_wins_delta=1 if is_winner else 0,
                total_score_delta=player["score"]
            )
        
        # завершаю игру
        await self.game_accessor.finish_game(game.id)
        
        await self.game_accessor.log_event(
            game_session_id=game.id,
            event_type="game_finished",
            event_data={"winner": leaderboard[0]["telegram_id"] if leaderboard else None}
        )
        
        return {
            "success": True,
            "leaderboard": leaderboard
        }