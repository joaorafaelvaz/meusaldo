"""add personality and weekly goals

Revision ID: c3f4bf42c94e
Revises: b2e3bf42c94d
Create Date: 2026-05-02 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f4bf42c94e'
down_revision: Union[str, None] = 'b2e3bf42c94d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add personality column to workspaces
    with op.batch_alter_table('workspaces') as batch_op:
        batch_op.add_column(sa.Column('personality', sa.String(), server_default='Sarcástico e Engraçado'))

    # Create weekly_goals table
    op.create_table('weekly_goals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workspace_id', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('weekly_goals') as batch_op:
        batch_op.create_index(batch_op.f('ix_weekly_goals_category'), ['category'], unique=False)
        batch_op.create_index(batch_op.f('ix_weekly_goals_id'), ['id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('weekly_goals') as batch_op:
        batch_op.drop_index(batch_op.f('ix_weekly_goals_id'))
        batch_op.drop_index(batch_op.f('ix_weekly_goals_category'))
    op.drop_table('weekly_goals')

    with op.batch_alter_table('workspaces') as batch_op:
        batch_op.drop_column('personality')
