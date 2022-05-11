"""add pictures field

Revision ID: d7706123cdb7
Revises: 7ecd21479cfc
Create Date: 2022-05-11 16:36:51.545201

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7706123cdb7'
down_revision = '7ecd21479cfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('pictures', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('items', 'pictures')
    # ### end Alembic commands ###