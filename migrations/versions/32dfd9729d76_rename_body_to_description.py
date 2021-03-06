"""rename body to description

Revision ID: 32dfd9729d76
Revises: 1b43a664914b
Create Date: 2022-05-11 00:17:12.933805

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '32dfd9729d76'
down_revision = '1b43a664914b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('description', sa.String(length=255), nullable=False))
    op.drop_column('items', 'body')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('body', mysql.VARCHAR(length=255), nullable=False))
    op.drop_column('items', 'description')
    # ### end Alembic commands ###
