-- Migration: 006_identity_oauth.sql
-- Email + OAuth Identity Extension

-- OAuth accounts table
CREATE TABLE IF NOT EXISTS auth.oauth_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_oauth_accounts_user_id ON auth.oauth_accounts(user_id);
CREATE INDEX idx_oauth_accounts_provider_user_id ON auth.oauth_accounts(provider, provider_user_id);

-- Email verifications table
CREATE TABLE IF NOT EXISTS auth.email_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_email_verifications_token ON auth.email_verifications(token);
CREATE INDEX idx_email_verifications_user_id ON auth.email_verifications(user_id);

-- Add email_verified column to users if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'auth' AND table_name = 'users' AND column_name = 'email_verified'
    ) THEN
        ALTER TABLE auth.users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE;
    END IF;
END $$;

-- Add status column to users if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'auth' AND table_name = 'users' AND column_name = 'status'
    ) THEN
        ALTER TABLE auth.users ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';
    END IF;
END $$;

-- Audit log for auth events
CREATE TABLE IF NOT EXISTS audit.auth_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    user_id UUID,
    email VARCHAR(255),
    tenant_id UUID,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_auth_events_user_id ON audit.auth_events(user_id);
CREATE INDEX idx_auth_events_event_type ON audit.auth_events(event_type);
CREATE INDEX idx_auth_events_created_at ON audit.auth_events(created_at);

COMMENT ON TABLE auth.oauth_accounts IS 'OAuth provider accounts linked to users';
COMMENT ON TABLE auth.email_verifications IS 'Email verification tokens';
COMMENT ON TABLE audit.auth_events IS 'Audit log for authentication events';
