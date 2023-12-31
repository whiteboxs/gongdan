"""empty message

Revision ID: 517a60bee63b
Revises: 9857a64bec54
Create Date: 2023-08-17 15:20:34.983422

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '517a60bee63b'
down_revision = '9857a64bec54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignee', schema=None) as batch_op:
        batch_op.alter_column('department',
               existing_type=mysql.VARCHAR(collation='utf8mb4_bin', length=16),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignee', schema=None) as batch_op:
        batch_op.alter_column('department',
               existing_type=mysql.VARCHAR(collation='utf8mb4_bin', length=16),
               nullable=True)

    # ### end Alembic commands ###
