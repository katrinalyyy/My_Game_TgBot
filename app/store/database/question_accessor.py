from typing import List, Optional, Tuple, Dict
import random
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.store.database.models import Category, Question, GameBoard


class QuestionAccessor:
    # класс для работы с вопросами
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_categories(self) -> List[Category]:
        """Получить все активные категории"""
        result = await self.session.execute(
            select(Category).where(Category.is_active == True)
        )
        return list(result.scalars().all())
    
    async def get_random_questions_for_game(
        self,
        num_categories: int = 5,
        difficulties: List[int] = None
    ) -> List[Question]:
        if difficulties is None:
            difficulties = [100, 200, 300, 400, 500]
        
        result = await self.session.execute(
            select(Category).where(Category.is_active == True)
        )
        all_categories = list(result.scalars().all())
        
        if len(all_categories) < num_categories:
            num_categories = len(all_categories)
        
        selected_categories = random.sample(all_categories, num_categories)
        
        questions = []
        for category in selected_categories:
            for difficulty in difficulties:
                result = await self.session.execute(
                    select(Question).where(
                        and_(
                            Question.category_id == category.id,
                            Question.difficulty == difficulty,
                            Question.is_active == True
                        )
                    )
                )
                category_questions = list(result.scalars().all())
                
                if category_questions:
                    questions.append(random.choice(category_questions))
        
        return questions
    
    async def get_question_by_id(self, question_id: int) -> Optional[Question]:
        result = await self.session.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()
    
    async def create_game_board(
        self,
        game_session_id: int,
        questions: List[Question]
    ) -> List[GameBoard]:
        existing_board = await self.get_game_board(game_session_id)
        if existing_board:
            return existing_board
        
        board_entries = []
        
        for question in questions:
            result = await self.session.execute(
                select(Category).where(Category.id == question.category_id)
            )
            category = result.scalar_one()

            existing_entry = await self.session.execute(
                select(GameBoard).where(
                    and_(
                        GameBoard.game_session_id == game_session_id,
                        GameBoard.category_name == category.name,
                        GameBoard.difficulty == question.difficulty
                    )
                )
            )
            
            if existing_entry.scalar_one_or_none():
                continue
            
            board_entry = GameBoard(
                game_session_id=game_session_id,
                question_id=question.id,
                category_name=category.name,
                difficulty=question.difficulty,
                is_answered=False
            )
            self.session.add(board_entry)
            board_entries.append(board_entry)
        
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            return await self.get_game_board(game_session_id)
            
        return board_entries
    
    async def get_game_board(self, game_session_id: int) -> List[GameBoard]:
        result = await self.session.execute(
            select(GameBoard)
            .where(GameBoard.game_session_id == game_session_id)
            .order_by(GameBoard.category_name, GameBoard.difficulty)
        )
        return list(result.scalars().all())
    
    async def mark_question_answered(
        self,
        game_session_id: int,
        category_name: str,
        difficulty: int,
        answered_by_telegram_id: int
    ):
        result = await self.session.execute(
            select(GameBoard).where(
                and_(
                    GameBoard.game_session_id == game_session_id,
                    GameBoard.category_name == category_name,
                    GameBoard.difficulty == difficulty
                )
            )
        )
        board_entry = result.scalar_one()
        board_entry.is_answered = True
        board_entry.answered_by_telegram_id = answered_by_telegram_id
        
        from datetime import datetime
        board_entry.answered_at = datetime.utcnow()
        
        await self.session.commit()
    
    async def get_available_questions(self, game_session_id: int) -> List[GameBoard]:
        result = await self.session.execute(
            select(GameBoard).where(
                and_(
                    GameBoard.game_session_id == game_session_id,
                    GameBoard.is_answered == False
                )
            )
        )
        return list(result.scalars().all())
    
    async def add_category(self, name: str, description: str = None) -> Category:
        category = Category(name=name, description=description)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category
    
    async def add_question(
        self,
        category_id: int,
        question_text: str,
        answer_text: str,
        difficulty: int
    ) -> Question:
        question = Question(
            category_id=category_id,
            question_text=question_text,
            answer_text=answer_text,
            difficulty=difficulty
        )
        self.session.add(question)
        await self.session.commit()
        await self.session.refresh(question)
        return question
    
    async def create_category(self, name: str, description: Optional[str] = None) -> Category:
        """Создать новую категорию"""
        category = Category(
            name=name,
            description=description
        )
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category
    
    async def get_categories(self) -> List[Category]:
        """Получить все категории"""
        result = await self.session.execute(
            select(Category).order_by(Category.name)
        )
        return list(result.scalars().all())
    
    async def get_questions_paginated(
        self,
        category_id: Optional[int] = None,
        difficulty: Optional[int] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Question], int]:
        """Получить вопросы с пагинацией и фильтрацией"""
        offset = (page - 1) * limit
        
        # Базовый запрос
        query = select(Question)
        
        # Добавляем фильтры
        conditions = []
        if category_id:
            conditions.append(Question.category_id == category_id)
        if difficulty:
            conditions.append(Question.difficulty == difficulty)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Получаем вопросы
        result = await self.session.execute(
            query.order_by(desc(Question.created_at))
            .offset(offset)
            .limit(limit)
        )
        questions = result.scalars().all()
        
        # Получаем общее количество
        count_query = select(func.count(Question.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()
        
        return questions, total
    
    async def get_questions_count(self) -> int:
        """Получить общее количество вопросов"""
        result = await self.session.execute(
            select(func.count(Question.id))
        )
        return result.scalar()
    
    async def get_categories_count(self) -> int:
        """Получить общее количество категорий"""
        result = await self.session.execute(
            select(func.count(Category.id))
        )
        return result.scalar()
    
    async def get_questions_count_by_difficulty(self, difficulty: int) -> int:
        """Получить количество вопросов по сложности"""
        result = await self.session.execute(
            select(func.count(Question.id)).where(Question.difficulty == difficulty)
        )
        return result.scalar()
    
    async def get_random_question_by_category_and_difficulty(
        self, category_name: str, difficulty: int
    ) -> Dict:
        """Получить случайный вопрос по категории и сложности"""
        # Сначала находим категорию
        category_result = await self.session.execute(
            select(Category).where(Category.name == category_name)
        )
        category = category_result.scalar_one_or_none()
        
        if not category:
            return {"success": False, "error": f"Категория '{category_name}' не найдена"}
        
        # Получаем случайный вопрос
        result = await self.session.execute(
            select(Question).where(
                and_(
                    Question.category_id == category.id,
                    Question.difficulty == difficulty,
                    Question.is_active == True
                )
            )
        )
        questions = result.scalars().all()
        
        if not questions:
            return {"success": False, "error": f"Нет вопросов в категории '{category_name}' сложности {difficulty}"}
        
        question = random.choice(questions)
        return {"success": True, "question": question}