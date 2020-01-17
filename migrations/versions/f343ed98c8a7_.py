"""empty message

Revision ID: f343ed98c8a7
Revises: 42ae5b3169fb
Create Date: 2020-01-17 11:26:11.814622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f343ed98c8a7'
down_revision = '42ae5b3169fb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('worktime', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'worktime')
    # ### end Alembic commands ###
