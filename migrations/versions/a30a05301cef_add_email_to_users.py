"""add email to users

Revision ID: a30a05301cef
Revises: a16d526c742e
Create Date: 2026-04-18 09:54:12.573160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a30a05301cef'
down_revision = 'a16d526c742e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=254), nullable=True))
        batch_op.create_unique_constraint('uq_users_email', ['email'])


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_email', type_='unique')
        batch_op.drop_column('email')

    op.create_table('measurements',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date', sa.DATE(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('waist', sa.FLOAT(), nullable=True),
    sa.Column('hips', sa.FLOAT(), nullable=True),
    sa.Column('chest', sa.FLOAT(), nullable=True),
    sa.Column('neck', sa.FLOAT(), nullable=True),
    sa.Column('body_fat', sa.FLOAT(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
