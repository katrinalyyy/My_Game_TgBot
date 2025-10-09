"""rename metadata to game_metadata

Revision ID: b004e512f9dc
Revises: 001
Create Date: 2025-10-09 06:30:39.475590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b004e512f9dc'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('game_sessions', 'metadata', new_column_name='game_metadata')

def downgrade():
    op.alter_column('game_sessions', 'game_metadata', new_column_name='metadata')