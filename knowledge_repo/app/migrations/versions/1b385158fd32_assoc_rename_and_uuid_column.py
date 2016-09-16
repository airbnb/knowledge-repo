"""assoc_rename_and_uuid_column

Revision ID: 1b385158fd32
Revises: 40dfdcb2b07c
Create Date: 2016-08-17 14:37:40.391822

"""

# revision identifiers, used by Alembic.
revision = '1b385158fd32'
down_revision = '40dfdcb2b07c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table('knowledge_post_author', 'assoc_post_author')
    op.rename_table('knowledge_post_tags', 'assoc_post_tag')
    op.add_column('assoc_post_author', sa.Column('order', sa.Integer(), nullable=True))

    op.add_column('posts', sa.Column('uuid', sa.String(length=100), nullable=True))
    op.create_unique_constraint(None, 'posts', ['uuid'])

    op.add_column('pageviews', sa.Column('object_action', sa.String(length=100), nullable=True))
    op.add_column('pageviews', sa.Column('version', sa.String(length=100), nullable=True))


def downgrade():
    op.drop_column('assoc_post_author', 'order')
    op.rename_table('assoc_post_author', 'knowledge_post_author')
    op.rename_table('assoc_post_tag', 'knowledge_post_tags')

    op.drop_constraint(None, 'posts', type_='unique')
    op.drop_column('posts', 'uuid')

    op.drop_column('pageviews', 'object_action')
    op.drop_column('pageviews', 'version')
