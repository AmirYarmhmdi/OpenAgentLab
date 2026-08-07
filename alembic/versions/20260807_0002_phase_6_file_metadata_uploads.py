"""phase 6 file metadata uploads

Revision ID: 20260807_0002
Revises: 20260807_0001
Create Date: 2026-08-07 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260807_0002"
down_revision: str | None = "20260807_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "file_metadata",
        sa.Column(
            "normalized_extension",
            sa.String(length=16),
            server_default="",
            nullable=False,
        ),
    )
    op.add_column(
        "file_metadata",
        sa.Column(
            "status",
            sa.String(length=32),
            server_default="stored",
            nullable=False,
        ),
    )
    op.add_column(
        "file_metadata",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.alter_column(
        "file_metadata",
        "document_id",
        existing_type=sa.UUID(),
        nullable=True,
    )
    op.alter_column(
        "file_metadata",
        "size_bytes",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.create_check_constraint(
        op.f("ck_file_metadata_file_metadata_status"),
        "file_metadata",
        "status in ('stored', 'failed')",
    )
    op.alter_column(
        "file_metadata",
        "normalized_extension",
        server_default=None,
        existing_type=sa.String(length=16),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_file_metadata_file_metadata_status"),
        "file_metadata",
        type_="check",
    )
    op.alter_column(
        "file_metadata",
        "size_bytes",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "file_metadata",
        "document_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
    op.drop_column("file_metadata", "updated_at")
    op.drop_column("file_metadata", "status")
    op.drop_column("file_metadata", "normalized_extension")
