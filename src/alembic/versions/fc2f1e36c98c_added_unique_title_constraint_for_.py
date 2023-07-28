"""added unique title constraint for products

Revision ID: fc2f1e36c98c
Revises: 436f06e6408d
Create Date: 2023-07-27 17:26:38.984193

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc2f1e36c98c'
down_revision = '436f06e6408d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # add unique key contraint on title column of products.
    op.create_unique_constraint(
        constraint_name='products_title_key',
        table_name='products',
        columns=['title']
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # drop unique key contraint on title column of products.
    op.drop_constraint(
        constraint_name='products_title_key',
        table_name='products'
    )
    # ### end Alembic commands ###
