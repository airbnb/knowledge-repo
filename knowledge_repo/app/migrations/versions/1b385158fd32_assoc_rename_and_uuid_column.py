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

    with op.batch_alter_table('assoc_post_author') as batch_op:
        batch_op.add_column(sa.Column('order', sa.Integer(), nullable=True))

    with op.batch_alter_table('posts') as batch_op:
        batch_op.add_column(sa.Column('uuid', sa.String(length=100), nullable=True))
        batch_op.create_unique_constraint('uq_uuid', ['uuid'])

    with op.batch_alter_table('pageviews') as batch_op:
        batch_op.add_column(sa.Column('object_action', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('version', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('assoc_post_author') as batch_op:
        batch_op.drop_column('order')

    op.rename_table('assoc_post_author', 'knowledge_post_author')
    op.rename_table('assoc_post_tag', 'knowledge_post_tags')

    with op.batch_alter_table('posts') as batch_op:
        batch_op.drop_constraint('uq_uuid', type_='unique')
        batch_op.drop_column('uuid')

    with op.batch_alter_table('pageviews') as batch_op:
        batch_op.drop_column('pageviews', 'object_action')
        batch_op.drop_column('pageviews', 'version')
