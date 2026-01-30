-- =============================================================================
-- WaqediAI Identity Schema Migration
-- Version: 001
-- Description: Initial identity schema for multi-tenant authentication
-- =============================================================================

-- Create schemas
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS audit;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- Tenants
-- =============================================================================
CREATE TABLE auth.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(63) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    tier VARCHAR(20) NOT NULL DEFAULT 'standard'
        CHECK (tier IN ('free', 'standard', 'enterprise')),
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tenants_slug ON auth.tenants(slug);
CREATE INDEX idx_tenants_active ON auth.tenants(is_active) WHERE is_active = true;

-- =============================================================================
-- Departments
-- =============================================================================
CREATE TABLE auth.departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES auth.tenants(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES auth.departments(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_departments_tenant ON auth.departments(tenant_id);

-- =============================================================================
-- Users
-- =============================================================================
CREATE TABLE auth.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES auth.tenants(id) ON DELETE CASCADE,
    department_id UUID REFERENCES auth.departments(id) ON DELETE SET NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'active', 'suspended', 'deleted')),
    profile JSONB DEFAULT '{}',
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant_email ON auth.users(tenant_id, email);
CREATE INDEX idx_users_status ON auth.users(status) WHERE status != 'deleted';
CREATE INDEX idx_users_department ON auth.users(department_id) WHERE department_id IS NOT NULL;

-- =============================================================================
-- Permissions
-- =============================================================================
CREATE TABLE auth.permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    scope VARCHAR(20) NOT NULL
        CHECK (scope IN ('own', 'department', 'tenant', 'system')),
    description TEXT,
    UNIQUE(resource, action, scope)
);

-- =============================================================================
-- Roles
-- =============================================================================
CREATE TABLE auth.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES auth.tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    scope VARCHAR(20) NOT NULL DEFAULT 'tenant'
        CHECK (scope IN ('system', 'tenant', 'department')),
    is_system BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_roles_tenant ON auth.roles(tenant_id);
CREATE INDEX idx_roles_system ON auth.roles(is_system) WHERE is_system = true;

-- =============================================================================
-- User-Role Assignments
-- =============================================================================
CREATE TABLE auth.user_roles (
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES auth.roles(id) ON DELETE CASCADE,
    scope_type VARCHAR(20),
    scope_id UUID,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    granted_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    PRIMARY KEY (user_id, role_id, COALESCE(scope_type, ''), COALESCE(scope_id, '00000000-0000-0000-0000-000000000000'))
);

CREATE INDEX idx_user_roles_user ON auth.user_roles(user_id);
CREATE INDEX idx_user_roles_role ON auth.user_roles(role_id);

-- =============================================================================
-- Role-Permission Mappings
-- =============================================================================
CREATE TABLE auth.role_permissions (
    role_id UUID NOT NULL REFERENCES auth.roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES auth.permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE INDEX idx_role_permissions_role ON auth.role_permissions(role_id);

-- =============================================================================
-- Refresh Tokens
-- =============================================================================
CREATE TABLE auth.refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    family_id UUID NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user ON auth.refresh_tokens(user_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_refresh_tokens_family ON auth.refresh_tokens(family_id);
CREATE INDEX idx_refresh_tokens_hash ON auth.refresh_tokens(token_hash);

-- =============================================================================
-- Audit Log
-- =============================================================================
CREATE TABLE audit.auth_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    user_id UUID,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant_time ON audit.auth_events(tenant_id, created_at DESC);
CREATE INDEX idx_audit_user_time ON audit.auth_events(user_id, created_at DESC);
CREATE INDEX idx_audit_type ON audit.auth_events(event_type);

-- =============================================================================
-- Seed Data: System Roles
-- =============================================================================
INSERT INTO auth.roles (id, name, description, scope, is_system) VALUES
    ('10000000-0000-0000-0000-000000000001', 'super_admin', 'Platform-wide administration', 'system', true),
    ('10000000-0000-0000-0000-000000000002', 'tenant_admin', 'Full tenant administration', 'tenant', true),
    ('10000000-0000-0000-0000-000000000003', 'dept_admin', 'Department administration', 'department', true),
    ('10000000-0000-0000-0000-000000000004', 'analyst', 'Query and view access', 'department', true),
    ('10000000-0000-0000-0000-000000000005', 'viewer', 'Read-only access', 'department', true);

-- =============================================================================
-- Seed Data: Permissions
-- =============================================================================
INSERT INTO auth.permissions (id, resource, action, scope, description) VALUES
    -- Tenant management
    ('20000000-0000-0000-0000-000000000001', 'tenants', 'manage', 'system', 'Manage all tenants'),
    
    -- User management
    ('20000000-0000-0000-0000-000000000010', 'users', 'create', 'tenant', 'Create users in tenant'),
    ('20000000-0000-0000-0000-000000000011', 'users', 'read', 'tenant', 'View all users in tenant'),
    ('20000000-0000-0000-0000-000000000012', 'users', 'update', 'tenant', 'Update any user in tenant'),
    ('20000000-0000-0000-0000-000000000013', 'users', 'delete', 'tenant', 'Delete any user in tenant'),
    ('20000000-0000-0000-0000-000000000014', 'users', 'manage', 'tenant', 'Full user management'),
    ('20000000-0000-0000-0000-000000000015', 'users', 'read', 'department', 'View users in department'),
    ('20000000-0000-0000-0000-000000000016', 'users', 'manage', 'department', 'Manage users in department'),
    
    -- Document management
    ('20000000-0000-0000-0000-000000000020', 'documents', 'upload', 'tenant', 'Upload documents'),
    ('20000000-0000-0000-0000-000000000021', 'documents', 'read', 'tenant', 'View all documents'),
    ('20000000-0000-0000-0000-000000000022', 'documents', 'read', 'department', 'View department documents'),
    ('20000000-0000-0000-0000-000000000023', 'documents', 'delete', 'own', 'Delete own documents'),
    ('20000000-0000-0000-0000-000000000024', 'documents', 'delete', 'tenant', 'Delete any document'),
    
    -- Query execution
    ('20000000-0000-0000-0000-000000000030', 'queries', 'execute', 'tenant', 'Execute queries'),
    ('20000000-0000-0000-0000-000000000031', 'queries', 'execute', 'department', 'Execute department queries'),
    
    -- Audit access
    ('20000000-0000-0000-0000-000000000040', 'audit', 'read', 'tenant', 'View audit logs');

-- =============================================================================
-- Seed Data: Role-Permission Mappings
-- =============================================================================
-- Tenant Admin permissions
INSERT INTO auth.role_permissions (role_id, permission_id) VALUES
    ('10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000010'),
    ('10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000011'),
    ('10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000012'),
    ('10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000013'),
    ('10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000014'),
    ('10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000020'),
    ('10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000021'),
    ('10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000024'),
    ('10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000030'),
    ('10000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000040');

-- Dept Admin permissions
INSERT INTO auth.role_permissions (role_id, permission_id) VALUES
    ('10000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000015'),
    ('10000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000016'),
    ('10000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000020'),
    ('10000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000022'),
    ('10000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000023'),
    ('10000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000031');

-- Analyst permissions
INSERT INTO auth.role_permissions (role_id, permission_id) VALUES
    ('10000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000020'),
    ('10000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000022'),
    ('10000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000023'),
    ('10000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000031');

-- Viewer permissions
INSERT INTO auth.role_permissions (role_id, permission_id) VALUES
    ('10000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000022');

-- =============================================================================
-- Seed Data: Development Tenant and Admin User
-- =============================================================================
INSERT INTO auth.tenants (id, slug, name, tier) VALUES
    ('00000000-0000-0000-0000-000000000001', 'dev-tenant', 'Development Tenant', 'enterprise');

-- Password: 'admin123456!' (Argon2id hash - regenerate for production!)
INSERT INTO auth.users (id, tenant_id, email, password_hash, status, profile) VALUES
    ('00000000-0000-0000-0000-000000000001', 
     '00000000-0000-0000-0000-000000000001',
     'admin@dev-tenant.local',
     '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$RdescudvJCsgt3ub+b+dWRWJTmaaJObG',
     'active',
     '{"first_name": "Admin", "last_name": "User", "display_name": "Admin"}');

-- Assign tenant_admin role to dev admin
INSERT INTO auth.user_roles (user_id, role_id) VALUES
    ('00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002');
