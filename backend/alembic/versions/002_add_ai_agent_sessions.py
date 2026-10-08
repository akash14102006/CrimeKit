"""
Add AI Agent Sessions and AI Messages tables.

Revision ID: 002_add_ai_agent_sessions
Revises: 001_add_blockchain
Create Date: 2026-10-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002_add_ai_agent_sessions"
down_revision = "001_add_blockchain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── ai_agent_sessions ─────────────────────────────────────────────────
    op.create_table(
        "ai_agent_sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("case_id", sa.String(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default="active", nullable=False),
        sa.Column("pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_ai_agent_sessions_case_id", "ai_agent_sessions", ["case_id"])
    op.create_index("ix_ai_agent_sessions_agent_id", "ai_agent_sessions", ["agent_id"])
    op.create_index("ix_ai_agent_sessions_user_id", "ai_agent_sessions", ["user_id"])

    # ── ai_messages ───────────────────────────────────────────────────────
    op.create_table(
        "ai_messages",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("session_id", sa.String(), sa.ForeignKey("ai_agent_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_ai_messages_session_id", "ai_messages", ["session_id"])
    op.create_index("ix_ai_messages_agent_id", "ai_messages", ["agent_id"])
    op.create_index("ix_ai_messages_created_at", "ai_messages", ["created_at"])


def downgrade() -> None:
    op.drop_table("ai_messages")
    op.drop_table("ai_agent_sessions")
