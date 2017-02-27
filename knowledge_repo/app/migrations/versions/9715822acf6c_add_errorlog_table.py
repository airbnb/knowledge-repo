"""Add ErrorLog table.

Revision ID: 9715822acf6c
Revises: 860cb49889a9
Create Date: 2017-02-27 10:15:42.372833

"""

# revision identifiers, used by Alembic.
revision = '9715822acf6c'
down_revision = '860cb49889a9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('errorlog',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('function', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('traceback', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('pageviews', sa.Column('id_errorlog', sa.Integer(), nullable=True))
    op.drop_column('pageviews', 'error_message')


def downgrade():
    op.add_column('pageviews', sa.Column('error_message', sa.Text(), nullable=True))
    op.drop_column('pageviews', 'id_errorlog')
    op.drop_table('errorlog')
