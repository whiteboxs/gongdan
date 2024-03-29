"""empty message

Revision ID: b26e93f385c0
Revises: 523bb38a03f7
Create Date: 2023-12-29 16:43:40.684733

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b26e93f385c0'
down_revision = '523bb38a03f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('jenkins_k8s',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('job_name', sa.String(length=255), nullable=False),
    sa.Column('job_id', sa.Integer(), nullable=True),
    sa.Column('job_info', sa.Text(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('jenkins_k8s')
    # ### end Alembic commands ###
