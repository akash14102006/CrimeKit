"""
Add blockchain anchoring tables.

Revision ID: 001_add_blockchain
Revises: a8e67154f876
Create Date: 2026-09-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001_add_blockchain"
down_revision = "a8e67154f876"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── blockchain_protocols ──────────────────────────────────────────────
    op.create_table(
        "blockchain_protocols",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("protocol_name", sa.String(), nullable=False, unique=True),
        sa.Column("protocol_version", sa.String(), nullable=False),
        sa.Column("specification", sa.Text(), nullable=True),
        sa.Column("hash_algorithm", sa.String(), nullable=False, server_default="sha256"),
        sa.Column("anchor_types", sa.JSON(), nullable=True),
        sa.Column("chain_id", sa.Integer(), nullable=True),
        sa.Column("network", sa.String(), nullable=True),
        sa.Column("contract_address", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # ── merkle_batches ────────────────────────────────────────────────────
    op.create_table(
        "merkle_batches",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("merkle_root", sa.String(), nullable=False, index=True),
        sa.Column("leaf_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("tree_depth", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("batch_size", sa.Integer(), nullable=False, server_default=sa.text("128")),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'collecting'")),
        sa.Column("anchor_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("anchored_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── blockchain_anchors ────────────────────────────────────────────────
    op.create_table(
        "blockchain_anchors",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("batch_id", sa.String(), sa.ForeignKey("merkle_batches.id"), nullable=False, index=True),
        sa.Column("tx_hash", sa.String(), nullable=True),
        sa.Column("block_number", sa.Integer(), nullable=True),
        sa.Column("chain_id", sa.Integer(), nullable=False),
        sa.Column("network", sa.String(), nullable=False),
        sa.Column("contract_address", sa.String(), nullable=True),
        sa.Column("merkle_root", sa.String(), nullable=False),
        sa.Column("anchor_type", sa.String(), nullable=False, server_default=sa.text("'evidence'")),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("anchored_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── evidence_commitments ──────────────────────────────────────────────
    op.create_table(
        "evidence_commitments",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("evidence_id", sa.String(), sa.ForeignKey("evidence.id"), nullable=False, index=True),
        sa.Column("case_id", sa.String(), sa.ForeignKey("cases.id"), nullable=True),
        sa.Column("commitment_hash", sa.String(), nullable=False, index=True),
        sa.Column("evidence_sha256", sa.String(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("protocol_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("batch_id", sa.String(), sa.ForeignKey("merkle_batches.id"), nullable=True, index=True),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("anchored_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── merkle_leaves ─────────────────────────────────────────────────────
    op.create_table(
        "merkle_leaves",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("batch_id", sa.String(), sa.ForeignKey("merkle_batches.id"), nullable=False, index=True),
        sa.Column("leaf_index", sa.Integer(), nullable=False),
        sa.Column("leaf_hash", sa.String(), nullable=False),
        sa.Column("evidence_id", sa.String(), sa.ForeignKey("evidence.id"), nullable=True),
        sa.Column("commitment_hash", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # ── artifact_commitments ──────────────────────────────────────────────
    op.create_table(
        "artifact_commitments",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("artifact_id", sa.String(), nullable=False, index=True),
        sa.Column("parent_artifact_id", sa.String(), nullable=True),
        sa.Column("evidence_id", sa.String(), sa.ForeignKey("evidence.id"), nullable=True, index=True),
        sa.Column("artifact_hash", sa.String(), nullable=False),
        sa.Column("commitment_hash", sa.String(), nullable=False, index=True),
        sa.Column("operation_type", sa.String(), nullable=False),
        sa.Column("tool_name", sa.String(), nullable=True),
        sa.Column("tool_version", sa.String(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("protocol_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'committed'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # ── custody_commitments ───────────────────────────────────────────────
    op.create_table(
        "custody_commitments",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("evidence_id", sa.String(), sa.ForeignKey("evidence.id"), nullable=False, index=True),
        sa.Column("custody_entry_id", sa.String(), sa.ForeignKey("chain_of_custody.id"), nullable=True),
        sa.Column("commitment_hash", sa.String(), nullable=False, index=True),
        sa.Column("previous_custody_hash", sa.String(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("actor_id", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("protocol_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'committed'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # ── verification_requests ─────────────────────────────────────────────
    op.create_table(
        "verification_requests",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("evidence_id", sa.String(), sa.ForeignKey("evidence.id"), nullable=False, index=True),
        sa.Column("requested_by", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("evidence_hash_match", sa.Boolean(), nullable=True),
        sa.Column("commitment_valid", sa.Boolean(), nullable=True),
        sa.Column("merkle_proof_valid", sa.Boolean(), nullable=True),
        sa.Column("blockchain_confirmed", sa.Boolean(), nullable=True),
        sa.Column("overall_result", sa.Boolean(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    op.drop_table("verification_requests")
    op.drop_table("custody_commitments")
    op.drop_table("artifact_commitments")
    op.drop_table("merkle_leaves")
    op.drop_table("evidence_commitments")
    op.drop_table("blockchain_anchors")
    op.drop_table("merkle_batches")
    op.drop_table("blockchain_protocols")
