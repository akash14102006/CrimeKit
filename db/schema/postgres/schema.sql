-- CrimeKit canonical schema draft (Postgres)
-- REVIEW: This is a draft. Do not use in production without security review.

-- Enable pgvector extension for vector search (RAG)
CREATE EXTENSION IF NOT EXISTS pgvector;

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT, -- bcrypt/argon2 hash
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Roles and RBAC
CREATE TABLE IF NOT EXISTS roles (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT
);

CREATE TABLE IF NOT EXISTS user_roles (
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

-- Cases (investigation)
CREATE TABLE IF NOT EXISTS cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Evidence
CREATE TABLE IF NOT EXISTS evidence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
  filename TEXT,
  content_type TEXT,
  size_bytes BIGINT,
  storage_path TEXT, -- object storage pointer
  sha256 TEXT, -- integrity/hash
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  -- vector embedding for RAG (nullable)
  embedding vector(1536)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_evidence_case_id ON evidence(case_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Audit / Auth events (simplified)
CREATE TABLE IF NOT EXISTS auth_events (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  event_type TEXT,
  ip_address TEXT,
  user_agent TEXT,
  occurred_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  details JSONB
);
