from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.store.database.models import User


class UserAccessor:    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            if username and user.username != username:
                user.username = username
            if first_name and user.first_name != first_name:
                user.first_name = first_name
            if last_name and user.last_name != last_name:
                user.last_name = last_name
            await self.session.commit()
            return user

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user_stats(
        self,
        telegram_id: int,
        total_games_delta: int = 0,
        total_wins_delta: int = 0,
        total_score_delta: int = 0
    ):
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return
        
        user.total_games += total_games_delta
        user.total_wins += total_wins_delta
        user.total_score += total_score_delta
        
        await self.session.commit()