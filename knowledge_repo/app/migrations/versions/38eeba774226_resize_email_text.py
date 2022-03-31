"""resize_email_text

Revision ID: 38eeba774226
Revises: eb39ac93fc39
Create Date: 2020-03-11 09:46:29.112836

"""

# revision identifiers, used by Alembic.
from knowledge_repo.utils.types import MediumText
import sqlalchemy as sa
from alembic import op
revision = '38eeba774226'
down_revision = 'eb39ac93fc39'


def upgrade():
    with op.batch_alter_table('emails') as batch_op:
        batch_op.alter_column(
            'text',
            existing_type=sa.Text(),
            type_=MediumText(),
            existing_nullable=True,
        )


def downgrade():
    with op.batch_alter_table('emails') as batch_op:
        batch_op.alter_column(
            'text',
            existing_type=MediumText(),
            type_=sa.Text(),
            existing_nullable=True,
        )
