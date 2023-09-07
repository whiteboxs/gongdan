"""empty message

Revision ID: 903784127da7
Revises: f546176edc06
Create Date: 2023-09-06 14:46:27.607082

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '903784127da7'
down_revision = 'f546176edc06'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ticket', schema=None) as batch_op:
        batch_op.alter_column('attachment_url',
               existing_type=mysql.VARCHAR(collation='utf8mb4_bin', length=255),
               type_=sa.String(length=512),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ticket', schema=None) as batch_op:
        batch_op.alter_column('attachment_url',
               existing_type=sa.String(length=512),
               type_=mysql.VARCHAR(collation='utf8mb4_bin', length=255),
               existing_nullable=True)

    # ### end Alembic commands ###