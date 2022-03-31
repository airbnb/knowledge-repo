"""Add support for external authentication.

Revision ID: 009eafe4838f
Revises: 9715822acf6c
Create Date: 2017-07-23 02:16:39.493032

"""

# revision identifiers, used by Alembic.
revision = '009eafe4838f'
down_revision = '9715822acf6c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('users', 'username', new_column_name='identifier', existing_type=sa.String(length=500))

    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('password', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('name', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('preferred_name', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('avatar_uri', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('email', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('last_login_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('username')
        batch_op.drop_column('preferred_name')
        batch_op.drop_column('password')
        batch_op.drop_column('name')
        batch_op.drop_column('last_login_at')
        batch_op.drop_column('email')
        batch_op.drop_column('active')
        batch_op.drop_column('avatar_uri')

    op.alter_column('users', 'identifier', new_column_name='username', existing_type=sa.String(length=500))
