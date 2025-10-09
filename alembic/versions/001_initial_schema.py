"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2025-10-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(255)),
        sa.Column('first_name', sa.String(255)),
        sa.Column('last_name', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('total_games', sa.Integer(), server_default='0'),
        sa.Column('total_wins', sa.Integer(), server_default='0'),
        sa.Column('total_score', sa.Integer(), server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index('idx_users_telegram_id', 'users', ['telegram_id'])

    # 2. Categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # 3. Questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('answer_text', sa.Text(), nullable=False),
        sa.Column('difficulty', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.CheckConstraint('difficulty IN (100, 200, 300, 400, 500)')
    )
    op.create_index('idx_questions_category', 'questions', ['category_id'])
    op.create_index('idx_questions_difficulty', 'questions', ['difficulty'])

    # 4. Game sessions table
    op.create_table(
        'game_sessions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('host_telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('state', sa.String(50), nullable=False, server_default='waiting_players'),
        sa.Column('current_player_telegram_id', sa.BigInteger()),
        sa.Column('started_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('finished_at', sa.TIMESTAMP()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['host_telegram_id'], ['users.telegram_id']),
        sa.ForeignKeyConstraint(['current_player_telegram_id'], ['users.telegram_id'])
    )
    op.create_index('idx_game_sessions_chat', 'game_sessions', ['chat_id'])
    op.create_index('idx_game_sessions_state', 'game_sessions', ['state'])
    op.create_index('idx_game_sessions_active', 'game_sessions', ['is_active'], 
                    postgresql_where=sa.text('is_active = true'))

    # 5. Participants table
    op.create_table(
        'participants',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('game_session_id', sa.BigInteger(), nullable=False),
        sa.Column('user_telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('score', sa.Integer(), server_default='0'),
        sa.Column('turn_order', sa.Integer()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('joined_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['game_session_id'], ['game_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_telegram_id'], ['users.telegram_id']),
        sa.UniqueConstraint('game_session_id', 'user_telegram_id')
    )
    op.create_index('idx_participants_game', 'participants', ['game_session_id'])
    op.create_index('idx_participants_user', 'participants', ['user_telegram_id'])

    # 6. Game board table
    op.create_table(
        'game_board',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('game_session_id', sa.BigInteger(), nullable=False),
        sa.Column('question_id', sa.Integer()),
        sa.Column('category_name', sa.String(255), nullable=False),
        sa.Column('difficulty', sa.Integer(), nullable=False),
        sa.Column('is_answered', sa.Boolean(), server_default='false'),
        sa.Column('answered_by_telegram_id', sa.BigInteger()),
        sa.Column('answered_at', sa.TIMESTAMP()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['game_session_id'], ['game_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id']),
        sa.ForeignKeyConstraint(['answered_by_telegram_id'], ['users.telegram_id']),
        sa.UniqueConstraint('game_session_id', 'category_name', 'difficulty')
    )
    op.create_index('idx_game_board_session', 'game_board', ['game_session_id'])
    op.create_index('idx_game_board_answered', 'game_board', ['is_answered'])

    # 7. Question attempts table
    op.create_table(
        'question_attempts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('game_session_id', sa.BigInteger(), nullable=False),
        sa.Column('question_id', sa.Integer()),
        sa.Column('user_telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('answer_text', sa.Text()),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('score_change', sa.Integer(), nullable=False),
        sa.Column('attempt_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['game_session_id'], ['game_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id']),
        sa.ForeignKeyConstraint(['user_telegram_id'], ['users.telegram_id'])
    )
    op.create_index('idx_attempts_game', 'question_attempts', ['game_session_id'])
    op.create_index('idx_attempts_question', 'question_attempts', ['question_id'])
    op.create_index('idx_attempts_user', 'question_attempts', ['user_telegram_id'])

    # 8. Game events table
    op.create_table(
        'game_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('game_session_id', sa.BigInteger(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('user_telegram_id', sa.BigInteger()),
        sa.Column('event_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['game_session_id'], ['game_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_telegram_id'], ['users.telegram_id'])
    )
    op.create_index('idx_events_game', 'game_events', ['game_session_id'])
    op.create_index('idx_events_type', 'game_events', ['event_type'])
    op.create_index('idx_events_created', 'game_events', ['created_at'])


def downgrade():
    op.drop_table('game_events')
    op.drop_table('question_attempts')
    op.drop_table('game_board')
    op.drop_table('participants')
    op.drop_table('game_sessions')
    op.drop_table('questions')
    op.drop_table('categories')
    op.drop_table('users')