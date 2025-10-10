from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.store.database.models import (
    GameSession, Participant, GameBoard, QuestionAttempt, GameEvent
)


class GameAccessor:    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_game_session(
        self,
        chat_id: int,
        host_telegram_id: int
    ) -> GameSession:
        game = GameSession(
            chat_id=chat_id,
            host_telegram_id=host_telegram_id,
            state='waiting_players'
        )
        self.session.add(game)
        await self.session.commit()
        await self.session.refresh(game)
        return game
    
    async def get_active_game_in_chat(self, chat_id: int) -> Optional[GameSession]:
        result = await self.session.execute(
            select(GameSession)
            .where(
                and_(
                    GameSession.chat_id == chat_id,
                    GameSession.is_active == True
                )
            )
            .options(
                selectinload(GameSession.participants),
                selectinload(GameSession.board)
            )
        )
        return result.scalar_one_or_none()
    
    async def add_participant(
        self,
        game_session_id: int,
        user_telegram_id: int,
        turn_order: int
    ) -> Participant:
        # + участника в игру
        participant = Participant(
            game_session_id=game_session_id,
            user_telegram_id=user_telegram_id,
            turn_order=turn_order
        )
        self.session.add(participant)
        await self.session.commit()
        await self.session.refresh(participant)
        return participant
    
    async def get_participants(self, game_session_id: int) -> List[Participant]:
        # получить всех участников игры
        result = await self.session.execute(
            select(Participant)
            .where(
                and_(
                    Participant.game_session_id == game_session_id,
                    Participant.is_active == True
                )
            )
            .order_by(Participant.turn_order)
        )
        return list(result.scalars().all())
    
    async def update_game_state(self, game_session_id: int, new_state: str):
        result = await self.session.execute(
            select(GameSession).where(GameSession.id == game_session_id)
        )
        game = result.scalar_one()
        game.state = new_state
        await self.session.commit()
    
    async def update_game_metadata(self, game_session_id: int, metadata_updates: dict):
        from sqlalchemy import update, text
        
        result = await self.session.execute(
            select(GameSession.game_metadata).where(GameSession.id == game_session_id)
        )
        current_metadata = result.scalar() or {}
        
        current_metadata.update(metadata_updates)
        
        await self.session.execute(
            update(GameSession)
            .where(GameSession.id == game_session_id)
            .values(game_metadata=current_metadata)
        )
        
        await self.session.commit()
    
    async def update_participant_score(
        self,
        game_session_id: int,
        user_telegram_id: int,
        score_delta: int
    ):
        # обновляю счёт участника
        result = await self.session.execute(
            select(Participant).where(
                and_(
                    Participant.game_session_id == game_session_id,
                    Participant.user_telegram_id == user_telegram_id
                )
            )
        )
        participant = result.scalar_one()
        participant.score += score_delta
        await self.session.commit()
    
    async def finish_game(self, game_session_id: int):
        # завершаю игру
        result = await self.session.execute(
            select(GameSession).where(GameSession.id == game_session_id)
        )
        game = result.scalar_one()
        game.state = 'game_finished'
        game.is_active = False
        game.finished_at = datetime.utcnow()
        await self.session.commit()
    
    async def log_event(
        self,
        game_session_id: int,
        event_type: str,
        user_telegram_id: Optional[int] = None,
        event_data: dict = None
    ):
        # записываю событие игры
        event = GameEvent(
            game_session_id=game_session_id,
            event_type=event_type,
            user_telegram_id=user_telegram_id,
            event_data=event_data or {}
        )
        self.session.add(event)
        await self.session.commit()
    
    async def get_games_paginated(
        self, page: int = 1, limit: int = 20, active_only: bool = False
    ) -> Tuple[List[GameSession], int]:
        """Получить игры с пагинацией"""
        offset = (page - 1) * limit
        
        # Базовый запрос
        query = select(GameSession)
        
        if active_only:
            query = query.where(GameSession.is_active == True)
        
        # Получаем игры
        result = await self.session.execute(
            query.order_by(desc(GameSession.created_at))
            .offset(offset)
            .limit(limit)
        )
        games = result.scalars().all()
        
        # Получаем общее количество
        count_query = select(func.count(GameSession.id))
        if active_only:
            count_query = count_query.where(GameSession.is_active == True)
        
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()
        
        return games, total
    
    async def get_games_count(self) -> int:
        """Получить общее количество игр"""
        result = await self.session.execute(
            select(func.count(GameSession.id))
        )
        return result.scalar()
    
    async def get_active_games_count(self) -> int:
        """Получить количество активных игр"""
        result = await self.session.execute(
            select(func.count(GameSession.id)).where(GameSession.is_active == True)
        )
        return result.scalar()
    
    async def cleanup_old_games(self, days_old: int = 30) -> int:
        """Удалить старые завершенные игры"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Находим старые завершенные игры
        result = await self.session.execute(
            select(GameSession.id).where(
                and_(
                    GameSession.is_active == False,
                    GameSession.finished_at < cutoff_date
                )
            )
        )
        old_game_ids = [row[0] for row in result.fetchall()]
        
        if not old_game_ids:
            return 0
        
        # Удаляем связанные записи (события, участников, доску)
        from sqlalchemy import delete
        
        await self.session.execute(
            delete(GameEvent).where(GameEvent.game_session_id.in_(old_game_ids))
        )
        await self.session.execute(
            delete(Participant).where(Participant.game_session_id.in_(old_game_ids))
        )
        await self.session.execute(
            delete(GameBoard).where(GameBoard.game_session_id.in_(old_game_ids))
        )
        
        # Удаляем сами игры
        await self.session.execute(
            delete(GameSession).where(GameSession.id.in_(old_game_ids))
        )
        
        await self.session.commit()
        return len(old_game_ids)