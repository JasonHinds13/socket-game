"""empty message

Revision ID: 92755e59dabd
Revises: cbbbf762e2d2
Create Date: 2020-05-07 22:07:42.871524

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92755e59dabd'
down_revision = 'cbbbf762e2d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rooms',
    sa.Column('room_id', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_open', sa.Boolean(), nullable=True),
    sa.Column('number_of_users', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('room_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rooms')
    # ### end Alembic commands ###
