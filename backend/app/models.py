from sqlalchemy import Column, String, Boolean, DateTime, Integer, BigInteger, ForeignKey, Table, Text
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy import JSON
import uuid
from .database import Base


# Association table for users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    roles = relationship('Role', secondary=user_roles, back_populates='users')


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    users = relationship('User', secondary=user_roles, back_populates='roles')


class Case(Base):
    __tablename__ = 'cases'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default='open')
    priority = Column(String, default='medium')
    assigned_to = Column(String, ForeignKey('users.id'), nullable=True)
    created_by = Column(String, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Evidence(Base):
    __tablename__ = 'evidence'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey('cases.id'), nullable=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    bucket = Column(String, nullable=True, index=True)
    object_key = Column(String, nullable=True, index=True)
    sha256 = Column(String, nullable=False, index=True)
    size = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    uploaded_by = Column(String, ForeignKey('users.id'), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class ChainOfCustody(Base):
    __tablename__ = 'chain_of_custody'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String, ForeignKey('evidence.id', ondelete='SET NULL'), nullable=True, index=True)
    action = Column(String, nullable=False)  # e.g., 'ingest', 'transfer', 'access', 'delete'
    actor_id = Column(String, ForeignKey('users.id'), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)


class ForensicJob(Base):
    __tablename__ = 'forensic_jobs'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String, ForeignKey('evidence.id'), nullable=False)
    processors = Column(JSON, nullable=True)  # list of processor names
    status = Column(String, default='queued')  # queued, running, completed, failed
    queued_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)


class ForensicResult(Base):
    __tablename__ = 'forensic_results'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String, ForeignKey('evidence.id'), nullable=False)
    processor = Column(String, nullable=False)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = 'documents'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String, ForeignKey('evidence.id'), nullable=True)
    text = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Embedding(Base):
    __tablename__ = 'embeddings'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey('documents.id'), nullable=False)
    vector = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = Column(String, ForeignKey('users.id'), nullable=True)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=True)
    target_id = Column(String, nullable=True)
    detail = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    token = Column(String, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)


class PersistentKV(Base):
    __tablename__ = 'persistent_kv'
    key = Column(String, primary_key=True)
    value = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MFAConfig(Base):
    __tablename__ = 'mfa_configs'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), unique=True, nullable=False)
    totp_secret = Column(String, nullable=False)
    is_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)


class ApiKey(Base):
    __tablename__ = 'api_keys'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False, index=True)
    key_prefix = Column(String, nullable=False)
    environment = Column(String, default='live')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    scopes = Column(JSON, nullable=True)


class UploadSession(Base):
    __tablename__ = 'upload_sessions'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    tenant_id = Column(String, nullable=True)
    case_id = Column(String, ForeignKey('cases.id'), nullable=True)
    filename = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    chunk_size = Column(BigInteger, nullable=False, default=104857600)
    total_chunks = Column(Integer, nullable=False)
    completed_chunks = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default='pending')
    upload_id = Column(String, nullable=True)
    bucket = Column(String, nullable=False)
    object_key = Column(String, nullable=False)
    sha256 = Column(String, nullable=True)
    md5 = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    evidence_id = Column(String, ForeignKey('evidence.id'), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    parts = Column(JSON, nullable=True, default=list)


class UploadChunk(Base):
    __tablename__ = 'upload_chunks'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('upload_sessions.id'), nullable=False)
    chunk_number = Column(Integer, nullable=False)
    size = Column(BigInteger, nullable=False)
    sha256 = Column(String, nullable=True)
    etag = Column(String, nullable=True)
    status = Column(String, nullable=False, default='pending')
    retries = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_at = Column(DateTime(timezone=True), nullable=True)
