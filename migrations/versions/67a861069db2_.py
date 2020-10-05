"""empty message

Revision ID: 67a861069db2
Revises: b05b116b887a
Create Date: 2020-10-05 12:37:11.528455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67a861069db2'
down_revision = 'b05b116b887a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('NewReleases', sa.Column('artists_identifier', sa.String(length=60), nullable=True))
    op.drop_column('NewReleases', 'artists_ids')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('NewReleases', sa.Column('artists_ids', sa.VARCHAR(length=60), autoincrement=False, nullable=True))
    op.drop_column('NewReleases', 'artists_identifier')
    # ### end Alembic commands ###