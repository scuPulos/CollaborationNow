"""added title and desired_size to the Listing table

Revision ID: bbaf0300d682
Revises: f91a9d3ada73
Create Date: 2019-11-09 21:18:11.538038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbaf0300d682'
down_revision = 'f91a9d3ada73'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('listing', sa.Column('desired_size', sa.Integer(), nullable=True))
    op.add_column('listing', sa.Column('title', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('listing', 'title')
    op.drop_column('listing', 'desired_size')
    # ### end Alembic commands ###
