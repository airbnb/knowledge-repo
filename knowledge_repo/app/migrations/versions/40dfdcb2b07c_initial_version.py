"""Initial version

Revision ID: f8113482599e
Revises: None
Create Date: 2016-08-18 17:04:32.542965

"""

# revision identifiers, used by Alembic.
revision = '40dfdcb2b07c'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('type', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('emails',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('trigger_id', sa.Integer(), nullable=True),
    sa.Column('trigger_type', sa.String(length=100), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.Column('object_type', sa.String(length=100), nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('subject', sa.Text(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pageviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('page', sa.String(length=512), nullable=True),
    sa.Column('endpoint', sa.String(length=255), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.Column('object_type', sa.String(length=100), nullable=True),
    sa.Column('ip_address', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('path', sa.String(length=512), nullable=True),
    sa.Column('project', sa.String(length=512), nullable=True),
    sa.Column('repository', sa.String(length=512), nullable=True),
    sa.Column('revision', sa.Integer(), nullable=True),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('tldr', sa.Text(), nullable=True),
    sa.Column('keywords', sa.Text(), nullable=True),
    sa.Column('thumbnail', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('path')
    )
    op.create_table('subscriptions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.Column('object_type', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('votes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.Column('object_type', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('knowledge_post_author',
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'],),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'],)
    )
    op.create_table('knowledge_post_tags',
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'],),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'],)
    )


def downgrade():
    op.drop_table('knowledge_post_tags')
    op.drop_table('knowledge_post_author')
    op.drop_table('votes')
    op.drop_table('users')
    op.drop_table('tags')
    op.drop_table('subscriptions')
    op.drop_table('posts')
    op.drop_table('pageviews')
    op.drop_table('emails')
    op.drop_table('comments')
