-- B-09 STAGE-A: Auth Schema Migration
-- 6 tables: users, devices, auth_tokens, refresh_tokens, auth_audit_log, rate_limit_counters
-- Idempotent: IF NOT EXISTS / ON CONFLICT DO NOTHING
-- Migration version: 20260823_B09_auth_v1

BEGIN;

-- 1. users table -- B-09 R2 rework (ARBITRATION_BATCH3 R3):
-- The V4.0 frozen contract (docs/v36/11_DATABASE_SCHEMA.sql:19) defines
-- users(id UUID PK, email TEXT NOT NULL UNIQUE, display_name TEXT,
-- password_hash TEXT, status TEXT, created_at, updated_at). The original
-- STAGE-A migration used CREATE TABLE IF NOT EXISTS users(...) which
-- would silently skip on any database that already shipped the frozen
-- users table -- leaving is_new_user / has_birth_info / has_heluo_model /
-- token_version / last_login_at as zero-coverage columns and breaking
-- get_token_version / bump_token_version at runtime.
--
-- Replaced with idempotent ALTER ADD COLUMN IF NOT EXISTS so the
-- migration lands whether users was created by this file (no-op) or by
-- the frozen contract (the 5 auth columns get added).
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'users'
          AND column_name = 'is_new_user'
    ) THEN
        ALTER TABLE users ADD COLUMN is_new_user BOOLEAN NOT NULL DEFAULT TRUE;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'users'
          AND column_name = 'has_birth_info'
    ) THEN
        ALTER TABLE users ADD COLUMN has_birth_info BOOLEAN NOT NULL DEFAULT FALSE;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'users'
          AND column_name = 'has_heluo_model'
    ) THEN
        ALTER TABLE users ADD COLUMN has_heluo_model BOOLEAN NOT NULL DEFAULT FALSE;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'users'
          AND column_name = 'token_version'
    ) THEN
        ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 1;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'users'
          AND column_name = 'last_login_at'
    ) THEN
        ALTER TABLE users ADD COLUMN last_login_at TIMESTAMPTZ;
    END IF;
END
$$;

-- 2. devices table
CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_type VARCHAR(20) NOT NULL DEFAULT 'pendant',
    device_token_hash VARCHAR(64) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at TIMESTAMPTZ,
    UNIQUE(user_id, device_token_hash)
);

-- 3. auth_tokens table (access tokens - short lived, not persisted for v1)
CREATE TABLE IF NOT EXISTS auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL,
    token_type VARCHAR(20) NOT NULL DEFAULT 'access',
    device_id UUID REFERENCES devices(id) ON DELETE SET NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. refresh_tokens table (long-lived, stored in DB with SHA256 hash)
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL,
    device_id UUID REFERENCES devices(id) ON DELETE SET NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at TIMESTAMPTZ,
    used_at TIMESTAMPTZ
);

-- 5. auth_audit_log table
CREATE TABLE IF NOT EXISTS auth_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    device_id UUID REFERENCES devices(id) ON DELETE SET NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6. rate_limit_counters table
CREATE TABLE IF NOT EXISTS rate_limit_counters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50) NOT NULL,
    client_key VARCHAR(255) NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 1,
    window_start TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(category, client_key)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_devices_user_id ON devices(user_id);
CREATE INDEX IF NOT EXISTS idx_devices_token_hash ON devices(device_token_hash);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_expires_at ON auth_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_auth_audit_log_user_id ON auth_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_audit_log_created_at ON auth_audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_rate_limit_counters_window ON rate_limit_counters(window_start);

-- Record migration version
INSERT INTO migration_versions (version, description)
VALUES ('20260823_B09_auth_v1', 'B-09 STAGE-A: Auth schema 6 tables (users, devices, auth_tokens, refresh_tokens, auth_audit_log, rate_limit_counters)')
ON CONFLICT (version) DO NOTHING;

COMMIT;
