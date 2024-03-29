"""empty message

Revision ID: 01dda0bf8a27
Revises: ebe3ffa70daf
Create Date: 2023-12-19 17:42:14.626038

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '01dda0bf8a27'
down_revision = 'ebe3ffa70daf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.alter_column('role_name',
               existing_type=mysql.ENUM('超级管理员', '普通用户', collation='utf8mb4_bin'),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.alter_column('role_name',
               existing_type=mysql.ENUM('超级管理员', '普通用户', collation='utf8mb4_bin'),
               nullable=False)

    # ### end Alembic commands ###
