"""empty message

Revision ID: f3e51832805b
Revises: fea43ecf4bf3
Create Date: 2023-07-21 16:12:13.241572

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f3e51832805b'
down_revision = 'fea43ecf4bf3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ticket', schema=None) as batch_op:
        batch_op.add_column(sa.Column('attachment_url', sa.String(length=255), nullable=True))
        batch_op.drop_column('image_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ticket', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', mysql.VARCHAR(collation='utf8mb4_bin', length=255), nullable=True))
        batch_op.drop_column('attachment_url')

    # ### end Alembic commands ###
