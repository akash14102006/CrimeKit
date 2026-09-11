"""
Revision ID: a8e67154f876
Revises: 
Create Date: 2026-07-30 00:47:17.929310
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

revision = 'a8e67154f876'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), primary_key=True),
    )

    op.create_table(
        'cases',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_by', sa.String(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'evidence',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('sha256', sa.String(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('uploaded_by', sa.String(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'chain_of_custody',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('evidence_id', sa.String(), sa.ForeignKey('evidence.id'), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('actor_id', sa.String(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('actor_id', sa.String(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=True),
        sa.Column('target_id', sa.String(), nullable=True),
        sa.Column('detail', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=True),
    )


def downgrade():
    op.drop_table('refresh_tokens')
    op.drop_table('audit_logs')
    op.drop_table('chain_of_custody')
    op.drop_table('evidence')
    op.drop_table('cases')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('roles')
