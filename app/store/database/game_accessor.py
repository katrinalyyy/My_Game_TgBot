from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_
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