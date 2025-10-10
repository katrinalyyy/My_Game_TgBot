from typing import Optional, Tuple, List
from sqlalchemy import select, func, desc
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
    
    async def create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Создать нового пользователя"""
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
    
    async def update_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Optional[User]:
        """Обновить пользователя"""
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        
        if username is not None:
            user.username = username
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        
        await self.session.commit()
        return user
    
    async def get_users_paginated(
        self, page: int = 1, limit: int = 20
    ) -> Tuple[List[User], int]:
        """Получить пользователей с пагинацией"""
        offset = (page - 1) * limit
        
        # Получаем пользователей
        result = await self.session.execute(
            select(User)
            .order_by(desc(User.created_at))
            .offset(offset)
            .limit(limit)
        )
        users = result.scalars().all()
        
        # Получаем общее количество
        count_result = await self.session.execute(
            select(func.count(User.id))
        )
        total = count_result.scalar()
        
        return users, total
    
    async def get_users_count(self) -> int:
        """Получить общее количество пользователей"""
        result = await self.session.execute(
            select(func.count(User.id))
        )
        return result.scalar()
    
    async def get_users_stats_paginated(
        self, page: int = 1, limit: int = 20, sort_by: str = "total_score"
    ) -> Tuple[List[dict], int]:
        """Получить статистику пользователей с пагинацией"""
        offset = (page - 1) * limit
        
        # Определяем поле для сортировки
        order_field = {
            "total_score": desc(User.total_score),
            "total_wins": desc(User.total_wins),
            "win_rate": desc(func.case((User.total_games > 0, User.total_wins / User.total_games), else_=0))
        }.get(sort_by, desc(User.total_score))
        
        # Получаем пользователей с сортировкой
        result = await self.session.execute(
            select(User)
            .order_by(order_field)
            .offset(offset)
            .limit(limit)
        )
        users = result.scalars().all()
        
        # Формируем статистику
        stats = []
        for user in users:
            win_rate = (user.total_wins / user.total_games) if user.total_games > 0 else 0
            stats.append({
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "total_games": user.total_games,
                "total_wins": user.total_wins,
                "total_score": user.total_score,
                "win_rate": round(win_rate, 2)
            })
        
        # Получаем общее количество
        count_result = await self.session.execute(
            select(func.count(User.id))
        )
        total = count_result.scalar()
        
        return stats, total