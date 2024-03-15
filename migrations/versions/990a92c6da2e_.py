"""empty message

Revision ID: 990a92c6da2e
Revises: 039cad0aec54
Create Date: 2024-03-05 15:01:36.695020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '990a92c6da2e'
down_revision = '039cad0aec54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('menu', schema=None) as batch_op:
        batch_op.add_column(sa.Column('icon', sa.String(length=16), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('menu', schema=None) as batch_op:
        batch_op.drop_column('icon')

    # ### end Alembic commands ###
