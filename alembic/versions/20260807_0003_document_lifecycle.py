"""Use explicit document ingestion lifecycle states.

Revision ID: 20260807_0003
Revises: 20260807_0002
Create Date: 2026-08-07 00:03:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260807_0003"
down_revision: str | Sequence[str] | None = "20260807_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        op.f("ck_documents_document_status"),
        "documents",
        type_="check",
    )
    op.execute("UPDATE documents SET status = 'uploaded' WHERE status = 'pending'")
    op.execute("UPDATE documents SET status = 'indexed' WHERE status = 'ready'")
    op.alter_column(
        "documents",
        "status",
        existing_type=sa.String(length=32),
        server_default="uploaded",
        existing_nullable=False,
    )
    op.create_check_constraint(
        op.f("ck_documents_document_status"),
        "documents",
        "status in ('uploaded', 'processing', 'indexed', 'failed')",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_documents_document_status"),
        "documents",
        type_="check",
    )
    op.execute("UPDATE documents SET status = 'pending' WHERE status = 'uploaded'")
    op.execute("UPDATE documents SET status = 'ready' WHERE status = 'indexed'")
    op.alter_column(
        "documents",
        "status",
        existing_type=sa.String(length=32),
        server_default="pending",
        existing_nullable=False,
    )
    op.create_check_constraint(
        op.f("ck_documents_document_status"),
        "documents",
        "status in ('pending', 'processing', 'ready', 'failed')",
    )
