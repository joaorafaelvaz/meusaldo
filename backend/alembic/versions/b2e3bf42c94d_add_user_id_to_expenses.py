"""add user_id to expenses

Revision ID: b2e3bf42c94d
Revises: d1e2bf42c94c
Create Date: 2026-05-01 11:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2e3bf42c94d'
down_revision = 'd1e2bf42c94c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_expense_user_id', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.drop_constraint('fk_expense_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')
