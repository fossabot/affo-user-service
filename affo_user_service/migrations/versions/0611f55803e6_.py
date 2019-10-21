"""empty message

Revision ID: 0611f55803e6
Revises:
Create Date: 2019-05-20 12:33:43.261414

"""
from alembic import op
import sqlalchemy as sa

import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '0611f55803e6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=True),
    sa.Column('phone', sa.String(length=30), nullable=True),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('password', sa.String(length=256), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('roles', sqlalchemy_utils.types.scalar_list.ScalarListType(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
