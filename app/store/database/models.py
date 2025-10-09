from datetime import datetime
from sqlalchemy import (
    BigInteger, Integer, String, Text, Boolean, TIMESTAMP,
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    # базовый класс для всех моделей пока так
    pass


class User(Base):
    # пользователь Telegram
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    total_games: Mapped[int] = mapped_column(Integer, default=0)
    total_wins: Mapped[int] = mapped_column(Integer, default=0)
    total_score: Mapped[int] = mapped_column(Integer, default=0)

    # отношения
    hosted_games: Mapped[List["GameSession"]] = relationship(
        "GameSession", back_populates="host", foreign_keys="GameSession.host_telegram_id"
    )
    participations: Mapped[List["Participant"]] = relationship(
        "Participant", back_populates="user"
    )
    attempts: Mapped[List["QuestionAttempt"]] = relationship(
        "QuestionAttempt", back_populates="user"
    )

    def __repr__(self):
        return f"<User {self.telegram_id} ({self.username})>"


class Category(Base):
    # категория вопросов
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # отношения
    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Category {self.name}>"


class Question(Base):
    # вопрос для игры
    __tablename__ = 'questions'
    __table_args__ = (
        CheckConstraint('difficulty IN (100, 200, 300, 400, 500)', name='check_difficulty'),
        Index('idx_questions_category', 'category_id'),
        Index('idx_questions_difficulty', 'difficulty'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id', ondelete='CASCADE'))
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # отношения
    category: Mapped["Category"] = relationship("Category", back_populates="questions")
    board_entries: Mapped[List["GameBoard"]] = relationship("GameBoard", back_populates="question")
    attempts: Mapped[List["QuestionAttempt"]] = relationship("QuestionAttempt", back_populates="question")

    def __repr__(self):
        return f"<Question {self.id}: {self.question_text[:30]}... ({self.difficulty})>"


class GameEvent(Base):
    """События игры (для логирования и восстановления)"""
    __tablename__ = 'game_events'
    __table_args__ = (
        Index('idx_events_game', 'game_session_id'),
        Index('idx_events_type', 'event_type'),
        Index('idx_events_created', 'created_at'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    game_session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('game_sessions.id', ondelete='CASCADE')
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    user_telegram_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey('users.telegram_id')
    )
    event_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    game: Mapped["GameSession"] = relationship("GameSession", back_populates="events")
    user: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self):
        return f"<GameEvent {self.event_type} at {self.created_at}>"


class GameSession(Base):
    """Игровая сессия"""
    __tablename__ = 'game_sessions'
    __table_args__ = (
        Index('idx_game_sessions_chat', 'chat_id'),
        Index('idx_game_sessions_state', 'state'),
        Index('idx_game_sessions_active', 'is_active', postgresql_where="is_active = true"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    host_telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.telegram_id'), nullable=False
    )
    state: Mapped[str] = mapped_column(String(50), default='waiting_players')
    current_player_telegram_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey('users.telegram_id')
    )
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    game_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    host: Mapped["User"] = relationship(
        "User", back_populates="hosted_games", foreign_keys=[host_telegram_id]
    )
    current_player: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[current_player_telegram_id]
    )
    participants: Mapped[List["Participant"]] = relationship(
        "Participant", back_populates="game", cascade="all, delete-orphan"
    )
    board: Mapped[List["GameBoard"]] = relationship(
        "GameBoard", back_populates="game", cascade="all, delete-orphan"
    )
    attempts: Mapped[List["QuestionAttempt"]] = relationship(
        "QuestionAttempt", back_populates="game", cascade="all, delete-orphan"
    )
    events: Mapped[List["GameEvent"]] = relationship(
        "GameEvent", back_populates="game", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<GameSession {self.id} in chat {self.chat_id} ({self.state})>"


class Participant(Base):
    """Участник игры"""
    __tablename__ = 'participants'
    __table_args__ = (
        UniqueConstraint('game_session_id', 'user_telegram_id', name='uq_participant'),
        Index('idx_participants_game', 'game_session_id'),
        Index('idx_participants_user', 'user_telegram_id'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    game_session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('game_sessions.id', ondelete='CASCADE')
    )
    user_telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.telegram_id')
    )
    score: Mapped[int] = mapped_column(Integer, default=0)
    turn_order: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    game: Mapped["GameSession"] = relationship("GameSession", back_populates="participants")
    user: Mapped["User"] = relationship("User", back_populates="participations")

    def __repr__(self):
        return f"<Participant {self.user_telegram_id} in game {self.game_session_id} ({self.score} pts)>"


class GameBoard(Base):
    """Игровая доска (вопросы в текущей игре)"""
    __tablename__ = 'game_board'
    __table_args__ = (
        UniqueConstraint('game_session_id', 'category_name', 'difficulty', name='uq_board_cell'),
        Index('idx_game_board_session', 'game_session_id'),
        Index('idx_game_board_answered', 'is_answered'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    game_session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('game_sessions.id', ondelete='CASCADE')
    )
    question_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('questions.id'))
    category_name: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    is_answered: Mapped[bool] = mapped_column(Boolean, default=False)
    answered_by_telegram_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey('users.telegram_id')
    )
    answered_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    # отношения
    game: Mapped["GameSession"] = relationship("GameSession", back_populates="board")
    question: Mapped[Optional["Question"]] = relationship("Question", back_populates="board_entries")
    answered_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self):
        status = "✅" if self.is_answered else "❓"
        return f"<GameBoard {status} {self.category_name} {self.difficulty}>"


class QuestionAttempt(Base):
    # попытка ответа на вопрос
    __tablename__ = 'question_attempts'
    __table_args__ = (
        Index('idx_attempts_game', 'game_session_id'),
        Index('idx_attempts_question', 'question_id'),
        Index('idx_attempts_user', 'user_telegram_id'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    game_session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('game_sessions.id', ondelete='CASCADE')
    )
    question_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('questions.id'))
    user_telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.telegram_id')
    )
    answer_text: Mapped[Optional[str]] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score_change: Mapped[int] = mapped_column(Integer, nullable=False)
    attempt_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # отношения
    game: Mapped["GameSession"] = relationship("GameSession", back_populates="attempts")
    question: Mapped[Optional["Question"]] = relationship("Question", back_populates="attempts")
    user: Mapped["User"] = relationship("User", back_populates="attempts")