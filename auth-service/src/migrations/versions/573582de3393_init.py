"""init

Revision ID: 573582de3393
Revises: 
Create Date: 2023-09-28 14:44:50.591158

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "573582de3393"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "permissions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=1024), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="auth",
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=1024), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="auth",
    )
    op.create_table(
        "role_permissions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column("permission_id", sa.UUID(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["auth.permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["auth.roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="auth",
    )
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("has_2fa", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("role_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["auth.roles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("id"),
        schema="auth",
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_agent", sa.String(), nullable=False),
        sa.Column("screen_width", sa.Integer(), nullable=True),
        sa.Column("screen_height", sa.Integer(), nullable=True),
        sa.Column("timezone", sa.String(), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "user_agent", "screen_width", "screen_height", "timezone", name="uq_device_details"
        ),
        schema="auth",
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("token"),
        schema="auth",
    )
    op.create_table(
        "social_account",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("social_id", sa.String(), nullable=False),
        sa.Column("social_name", sa.String(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("social_id", "social_name", name="social_pk"),
        schema="auth",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("social_account", schema="auth")
    op.drop_table("refresh_tokens", schema="auth")
    op.drop_table("devices", schema="auth")
    op.drop_table("users", schema="auth")
    op.drop_table("role_permissions", schema="auth")
    op.drop_table("roles", schema="auth")
    op.drop_table("permissions", schema="auth")
    # ### end Alembic commands ###
