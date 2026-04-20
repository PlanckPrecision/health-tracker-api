"""add weekly_loss_pct to goals

Revision ID: b1c4e7a2f093
Revises: a30a05301cef
Create Date: 2026-04-20 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b1c4e7a2f093'
down_revision = 'a30a05301cef'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('goals', schema=None) as batch_op:
        batch_op.add_column(sa.Column('weekly_loss_pct', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('goals', schema=None) as batch_op:
        batch_op.drop_column('weekly_loss_pct')
