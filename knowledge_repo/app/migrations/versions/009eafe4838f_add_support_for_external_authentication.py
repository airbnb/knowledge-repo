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
    # Migrate from `usernames` to `identifiers`
    op.alter_column('users', 'username', new_column_name='identifier', existing_type=sa.String(length=500))
    op.add_column('users', sa.Column('username', sa.String(length=500), nullable=True))

    # Add new fields
    op.add_column('users', sa.Column('password', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('active', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('name', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('preferred_name', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('avatar_uri', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('email', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('users', 'username')
    op.alter_column('users', 'identifier', new_column_name='username', existing_type=sa.String(length=500))

    # Remove new fields
    op.drop_column('users', 'preferred_name')
    op.drop_column('users', 'password')
    op.drop_column('users', 'name')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'email')
    op.drop_column('users', 'active')
    op.drop_column('users', 'avatar_uri')
