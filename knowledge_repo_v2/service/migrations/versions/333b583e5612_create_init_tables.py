"""create init tables

Revision ID: 333b583e5612
Revises: 
Create Date: 2022-12-05 22:53:39.778852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "333b583e5612"
down_revision = None
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

from knowledge_repo.utils.types import MediumText

def upgrade():
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("type", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "emails",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("trigger_id", sa.Integer(), nullable=True),
        sa.Column("trigger_type", sa.String(length=100), nullable=True),
        sa.Column("object_id", sa.Integer(), nullable=True),
        sa.Column("object_type", sa.String(length=100), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("text", MediumText(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
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
    op.create_table(
        "pageviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("page", sa.String(length=512), nullable=True),
        sa.Column("endpoint", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("object_id", sa.Integer(), nullable=True),
        sa.Column("object_type", sa.String(length=100), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("id_errorlog", sa.Integer(), nullable=True),
        sa.Column('object_action', sa.String(length=100), nullable=True),
        sa.Column('version', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.Index(
            "object_id_type_action_index",
            "pageviews",
            ["object_id", "object_type", "object_action"],
            unique=False,
            ),
    )
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(length=512), nullable=True),
        sa.Column("project", sa.String(length=512), nullable=True),
        sa.Column("repository", sa.String(length=512), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("subtitle", sa.Text(), nullable=True),
        sa.Column("tldr", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("thumbnail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.Integer(), nullable=True),
        sa.Column("private", sa.Integer(), nullable=True),
        sa.Column('uuid', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("path"),
        sa.UniqueConstraint('uq_uuid', ['uuid']),
    )
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("object_id", sa.Integer(), nullable=True),
        sa.Column("object_type", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column('identifier', sa.String(length=500), nullable=True),
        sa.Column('password', sa.String(length=500), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('name', sa.String(length=500), nullable=True),
        sa.Column('preferred_name', sa.String(length=500), nullable=True),
        sa.Column('avatar_uri', sa.Text(), nullable=True),
        sa.Column('email', sa.String(length=500), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "votes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("object_id", sa.Integer(), nullable=True),
        sa.Column("object_type", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table('index_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=512), nullable=False),
        sa.Column('value', sa.String(length=512), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('type', 'name', name='_uc_type_name')
    )
    op.create_table(
        "assoc_post_author",
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True)
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["posts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
    )
    op.create_table(
        "assoc_post_tag",
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column("tag_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["posts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.id"],
        ),
    )
    op.create_table('groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('assoc_group_user',
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table('assoc_post_group',
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], )
    )


def downgrade():
    op.drop_table("knowledge_post_tags")
    op.drop_table("knowledge_post_author")
    op.drop_table("votes")
    op.drop_table("users")
    op.drop_table("tags")
    op.drop_table("subscriptions")
    op.drop_table("posts")
    op.drop_table("pageviews")
    op.drop_table("emails")
    op.drop_table("comments")
