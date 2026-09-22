"""Add persistent ordered conversation messages.

Revision ID: 20260807_0005
Revises: 20260807_0004
Create Date: 2026-08-07 00:05:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260807_0005"
down_revision: str | Sequence[str] | None = "20260807_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conversation_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default="submitted",
            nullable=False,
        ),
        sa.Column("error_message", sa.String(length=512), nullable=True),
        sa.Column(
            "citations",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "sources",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "message_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role in ('user', 'assistant')",
            name=op.f("ck_conversation_messages_conversation_message_role"),
        ),
        sa.CheckConstraint(
            "status in ('submitted', 'answered', 'failed')",
            name=op.f("ck_conversation_messages_conversation_message_status"),
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name=op.f("fk_conversation_messages_session_id_sessions"),
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflow_executions.id"],
            name=op.f("fk_conversation_messages_workflow_id_workflow_executions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversation_messages")),
        sa.UniqueConstraint(
            "session_id",
            "sequence",
            name=op.f("uq_conversation_messages_session_sequence"),
        ),
    )
    op.create_index(
        op.f("ix_conversation_messages_session_id"),
        "conversation_messages",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_workflow_id"),
        "conversation_messages",
        ["workflow_id"],
        unique=False,
    )

    op.create_table(
        "conversation_message_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_metadata_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reference_type", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "reference_type in ('attachment', 'referenced')",
            name=op.f(
                "ck_conversation_message_documents_"
                "conversation_message_document_reference_type"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_conversation_message_documents_document_id_documents"),
        ),
        sa.ForeignKeyConstraint(
            ["file_metadata_id"],
            ["file_metadata.id"],
            name=op.f(
                "fk_conversation_message_documents_file_metadata_id_file_metadata"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["conversation_messages.id"],
            name=op.f(
                "fk_conversation_message_documents_message_id_conversation_messages"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversation_message_documents")),
    )
    op.create_index(
        op.f("ix_conversation_message_documents_document_id"),
        "conversation_message_documents",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_message_documents_file_metadata_id"),
        "conversation_message_documents",
        ["file_metadata_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_message_documents_message_id"),
        "conversation_message_documents",
        ["message_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_conversation_message_documents_message_id"),
        table_name="conversation_message_documents",
    )
    op.drop_index(
        op.f("ix_conversation_message_documents_file_metadata_id"),
        table_name="conversation_message_documents",
    )
    op.drop_index(
        op.f("ix_conversation_message_documents_document_id"),
        table_name="conversation_message_documents",
    )
    op.drop_table("conversation_message_documents")
    op.drop_index(
        op.f("ix_conversation_messages_workflow_id"),
        table_name="conversation_messages",
    )
    op.drop_index(
        op.f("ix_conversation_messages_session_id"),
        table_name="conversation_messages",
    )
    op.drop_table("conversation_messages")
