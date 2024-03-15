"""empty message

Revision ID: f80ddec431ac
Revises: 990a92c6da2e
Create Date: 2024-03-05 15:13:05.454726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f80ddec431ac'
down_revision = '990a92c6da2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('menu', schema=None) as batch_op:
        batch_op.add_column(sa.Column('permiss', sa.Integer(), autoincrement=True, nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('menu', schema=None) as batch_op:
        batch_op.drop_column('permiss')

    # ### end Alembic commands ###
