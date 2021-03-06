"""add main_picture field

Revision ID: 007bd05ecf9b
Revises: d7706123cdb7
Create Date: 2022-05-11 17:27:36.710506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007bd05ecf9b'
down_revision = 'd7706123cdb7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('main_picture', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('items', 'main_picture')
    # ### end Alembic commands ###
