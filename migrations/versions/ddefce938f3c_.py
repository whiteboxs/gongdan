"""empty message

Revision ID: ddefce938f3c
Revises: f3e51832805b
Create Date: 2023-07-24 09:02:28.755012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddefce938f3c'
down_revision = 'f3e51832805b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedback', schema=None) as batch_op:
        batch_op.add_column(sa.Column('attachment_url', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedback', schema=None) as batch_op:
        batch_op.drop_column('attachment_url')

    # ### end Alembic commands ###
