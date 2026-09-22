"""Add Phase A user ownership fields.

Revision ID: 20260807_0006
Revises: 20260807_0005
Create Date: 2026-08-07 00:06:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260807_0006"
down_revision: str | Sequence[str] | None = "20260807_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("issuer", sa.String(length=512), nullable=True))
    op.add_column(
        "users",
        sa.Column("external_subject", sa.String(length=512), nullable=True),
    )
    op.create_index(op.f("ix_users_issuer"), "users", ["issuer"], unique=False)
    op.create_index(
        op.f("ix_users_external_subject"),
        "users",
        ["external_subject"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_users_issuer_external_subject",
        "users",
        ["issuer", "external_subject"],
    )

    op.add_column(
        "documents",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(op.f("ix_documents_user_id"), "documents", ["user_id"])
    op.create_foreign_key(
        op.f("fk_documents_user_id_users"),
        "documents",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "file_metadata",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(op.f("ix_file_metadata_user_id"), "file_metadata", ["user_id"])
    op.create_foreign_key(
        op.f("fk_file_metadata_user_id_users"),
        "file_metadata",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "workflow_executions",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        op.f("ix_workflow_executions_user_id"),
        "workflow_executions",
        ["user_id"],
    )
    op.create_foreign_key(
        op.f("fk_workflow_executions_user_id_users"),
        "workflow_executions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_documents_user_id_id",
        "documents",
        ["user_id", "id"],
        unique=False,
    )
    op.create_index(
        "ix_file_metadata_user_id_document_id",
        "file_metadata",
        ["user_id", "document_id"],
        unique=False,
    )
    op.create_index(
        "ix_sessions_user_id_id",
        "sessions",
        ["user_id", "id"],
        unique=False,
    )
    op.create_index(
        "ix_workflow_executions_user_id_id",
        "workflow_executions",
        ["user_id", "id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_workflow_executions_user_id_id", "workflow_executions")
    op.drop_index("ix_sessions_user_id_id", "sessions")
    op.drop_index("ix_file_metadata_user_id_document_id", "file_metadata")
    op.drop_index("ix_documents_user_id_id", "documents")

    op.drop_constraint(
        op.f("fk_workflow_executions_user_id_users"),
        "workflow_executions",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_workflow_executions_user_id"), "workflow_executions")
    op.drop_column("workflow_executions", "user_id")

    op.drop_constraint(
        op.f("fk_file_metadata_user_id_users"),
        "file_metadata",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_file_metadata_user_id"), "file_metadata")
    op.drop_column("file_metadata", "user_id")

    op.drop_constraint(
        op.f("fk_documents_user_id_users"),
        "documents",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_documents_user_id"), "documents")
    op.drop_column("documents", "user_id")

    op.drop_constraint("uq_users_issuer_external_subject", "users", type_="unique")
    op.drop_index(op.f("ix_users_external_subject"), "users")
    op.drop_index(op.f("ix_users_issuer"), "users")
    op.drop_column("users", "external_subject")
    op.drop_column("users", "issuer")
