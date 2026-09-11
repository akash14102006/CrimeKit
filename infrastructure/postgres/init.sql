-- CrimeKit Database Initialization Script
-- Runs once when PostgreSQL container starts for the first time.
-- Tables are created by SQLAlchemy (database.init_db()) at application startup.
-- This script handles only extensions and permissions.

\connect crimekit

-- ============================================================
-- 1. Extensions
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- ============================================================
-- 2. Grant Permissions
-- ============================================================
-- Grant to the user specified in POSTGRES_USER env var
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'crimekit_app') THEN
    GRANT CONNECT ON DATABASE crimekit TO crimekit_app;
    GRANT USAGE ON SCHEMA public TO crimekit_app;
    GRANT CREATE ON SCHEMA public TO crimekit_app;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO crimekit_app;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO crimekit_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO crimekit_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO crimekit_app;
  END IF;
END
$$;
