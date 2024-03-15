"""empty message

Revision ID: 591dd919684f
Revises: b73bd2d57791
Create Date: 2024-02-21 10:24:42.388283

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '591dd919684f'
down_revision = 'b73bd2d57791'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=mysql.VARCHAR(collation='utf8mb4_bin', length=64),
               type_=sa.String(length=128),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.String(length=128),
               type_=mysql.VARCHAR(collation='utf8mb4_bin', length=64),
               existing_nullable=False)

    # ### end Alembic commands ###