"""followers table

Revision ID: 523ebdce849f
Revises: b43b3e42bd9d
Create Date: 2020-09-13 10:22:46.950957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '523ebdce849f'
down_revision = 'b43b3e42bd9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('followers')
    # ### end Alembic commands ###
