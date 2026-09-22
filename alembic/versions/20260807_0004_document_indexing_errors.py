"""Store safe document indexing failure details.

Revision ID: 20260807_0004
Revises: 20260807_0003
Create Date: 2026-08-07 00:04:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260807_0004"
down_revision: str | Sequence[str] | None = "20260807_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("indexing_error_code", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("indexing_error_message", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "indexing_error_message")
    op.drop_column("documents", "indexing_error_code")
