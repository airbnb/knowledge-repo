"""add_pageview_indexes

Revision ID: eb39ac93fc39
Revises: d15f6cac07e1
Create Date: 2019-11-15 15:30:55.010491

"""

# revision identifiers, used by Alembic.
revision = 'eb39ac93fc39'
down_revision = 'd15f6cac07e1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(
        "object_id_type_action_index",
        "pageviews",
        ["object_id", "object_type", "object_action"],
        unique=False,
    )

def downgrade():
    op.drop_index("object_id_type_action_index", table_name="pageviews")
