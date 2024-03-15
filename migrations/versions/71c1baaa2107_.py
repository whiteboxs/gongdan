"""empty message

Revision ID: 71c1baaa2107
Revises: 591dd919684f
Create Date: 2024-02-21 15:39:00.030852

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '71c1baaa2107'
down_revision = '591dd919684f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.alter_column('role_name',
               existing_type=mysql.ENUM('超级管理员', '普通用户', collation='utf8mb4_bin'),
               type_=sa.String(length=16),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.alter_column('role_name',
               existing_type=sa.String(length=16),
               type_=mysql.ENUM('超级管理员', '普通用户', collation='utf8mb4_bin'),
               nullable=True)

    # ### end Alembic commands ###
