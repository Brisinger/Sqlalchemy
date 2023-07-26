"""added user phone number

Revision ID: 436f06e6408d
Revises: dd272afd1e32
Create Date: 2023-07-26 11:00:21.945123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '436f06e6408d'
down_revision = 'dd272afd1e32'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### adding phone_number column to users ###
    op.add_column(
        table_name='users', 
        column=sa.Column(
            name='phone_number',
            type_=sa.VARCHAR(length=50),
            nullable=True
        )
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### dropping phone_number column from users ###
    op.drop_column('users', 'phone_number')
    # ### end Alembic commands ###
