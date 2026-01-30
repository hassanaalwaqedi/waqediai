-- =============================================================================
-- Database Initialization Script
-- Creates schemas for multi-tenant isolation
-- =============================================================================

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas for service isolation
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS documents;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant permissions
GRANT ALL ON SCHEMA auth TO waqedi;
GRANT ALL ON SCHEMA documents TO waqedi;
GRANT ALL ON SCHEMA audit TO waqedi;

-- Create tenants table
CREATE TABLE IF NOT EXISTS auth.tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    tier VARCHAR(50) DEFAULT 'standard',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create users table
CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES auth.tenants(id),
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

-- Create index for tenant lookups
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON auth.users(tenant_id);

-- Insert default tenant for development
INSERT INTO auth.tenants (id, name, tier)
VALUES ('00000000-0000-0000-0000-000000000001', 'Development Tenant', 'enterprise')
ON CONFLICT DO NOTHING;
