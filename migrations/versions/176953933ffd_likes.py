"""likes

Revision ID: 176953933ffd
Revises: 4b8af0cedd36
Create Date: 2019-06-26 10:33:05.866973

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '176953933ffd'
down_revision = '4b8af0cedd36'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('likes',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('video_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('likes')
    # ### end Alembic commands ###
