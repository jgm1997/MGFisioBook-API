"""initial

Revision ID: 0008
Revises: 0007
Create Date: 2026-01-21 13:29:08.517152
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, Sequence[str], None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.String, nullable=False),
        sa.Column("token", sa.String, nullable=False),
        sa.Column("platform", sa.String, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    op.create_foreign_key(
        "fk_devices_supabase_user_id_auth_users",
        "devices",
        "users",
        ["supabase_user_id"],
        ["id"],
        referent_schema="auth",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(
        "fk_devices_supabase_user_id_auth_users",
        "devices",
        type_="foreignkey",
    )
    op.drop_table("devices")
