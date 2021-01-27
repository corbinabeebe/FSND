"""empty message

Revision ID: b0dfc630043a
Revises: d5d46d59d34a
Create Date: 2021-01-26 19:46:45.734689

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0dfc630043a'
down_revision = 'd5d46d59d34a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website')
    # ### end Alembic commands ###
