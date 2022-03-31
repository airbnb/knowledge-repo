"""Add subtitle field to post database.

Revision ID: d15f6cac07e1
Revises: 009eafe4838f
Create Date: 2018-10-03 12:31:18.462880

"""

# revision identifiers, used by Alembic.
revision = 'd15f6cac07e1'
down_revision = '009eafe4838f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('posts', sa.Column('subtitle', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('posts', 'subtitle')
