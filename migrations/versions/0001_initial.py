"""initial

Revision ID: 0001
Revises:
Create Date: 2026-01-13 23:52:08.517152
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ------------------
    # PATIENTS
    # ------------------
    op.create_table(
        "patients",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("supabase_user_id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_patients_email"),
        sa.UniqueConstraint("supabase_user_id", name="uq_patients_supabase_user_id"),
    )

    op.create_foreign_key(
        "fk_patients_supabase_user_id_auth_users",
        "patients",
        "users",
        ["supabase_user_id"],
        ["id"],
        referent_schema="auth",
        ondelete="CASCADE",
    )

    # ------------------
    # THERAPISTS
    # ------------------
    op.create_table(
        "therapists",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("supabase_user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("specialty", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_therapists_email"),
        sa.UniqueConstraint("supabase_user_id", name="uq_therapists_supabase_user_id"),
    )

    op.create_foreign_key(
        "fk_therapists_supabase_user_id_auth_users",
        "therapists",
        "users",
        ["supabase_user_id"],
        ["id"],
        referent_schema="auth",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_therapists_supabase_user_id_auth_users",
        "therapists",
        type_="foreignkey",
    )
    op.drop_table("therapists")

    op.drop_constraint(
        "fk_patients_supabase_user_id_auth_users",
        "patients",
        type_="foreignkey",
    )
    op.drop_table("patients")
