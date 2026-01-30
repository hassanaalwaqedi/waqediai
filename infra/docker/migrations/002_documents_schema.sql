-- =============================================================================
-- WaqediAI Documents Schema Migration
-- Version: 002
-- Description: Document metadata and lifecycle tables
-- =============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS documents;

-- =============================================================================
-- Collections (optional document groupings)
-- =============================================================================
CREATE TABLE documents.collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_collections_tenant ON documents.collections(tenant_id);

-- =============================================================================
-- Documents
-- =============================================================================
CREATE TABLE documents.documents (
    id VARCHAR(50) PRIMARY KEY,
    tenant_id UUID NOT NULL,
    uploaded_by UUID NOT NULL,
    department_id UUID,
    collection_id UUID REFERENCES documents.collections(id) ON DELETE SET NULL,
    
    -- File properties
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    size_bytes BIGINT NOT NULL,
    checksum_sha256 VARCHAR(64) NOT NULL,
    
    -- Classification
    file_category VARCHAR(20) NOT NULL
        CHECK (file_category IN ('DOCUMENT', 'IMAGE', 'AUDIO', 'VIDEO')),
    language VARCHAR(10),
    
    -- Lifecycle
    status VARCHAR(20) NOT NULL DEFAULT 'UPLOADED'
        CHECK (status IN ('UPLOADED', 'VALIDATED', 'QUEUED', 'PROCESSING', 
                          'PROCESSED', 'FAILED', 'ARCHIVED', 'REJECTED', 'DELETED')),
    retention_policy VARCHAR(50) NOT NULL DEFAULT 'standard',
    legal_hold BOOLEAN NOT NULL DEFAULT false,
    
    -- Storage reference
    storage_bucket VARCHAR(100) NOT NULL,
    storage_key VARCHAR(500) NOT NULL,
    
    -- Timestamps
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    validated_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    
    -- Custom metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for common queries
CREATE INDEX idx_documents_tenant ON documents.documents(tenant_id);
CREATE INDEX idx_documents_status ON documents.documents(status);
CREATE INDEX idx_documents_tenant_status ON documents.documents(tenant_id, status);
CREATE INDEX idx_documents_collection ON documents.documents(collection_id);
CREATE INDEX idx_documents_uploaded_at ON documents.documents(uploaded_at DESC);
CREATE INDEX idx_documents_category ON documents.documents(file_category);
CREATE INDEX idx_documents_deleted ON documents.documents(deleted_at) WHERE deleted_at IS NULL;

-- =============================================================================
-- Document Status History (Audit Trail)
-- =============================================================================
CREATE TABLE documents.status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(50) NOT NULL REFERENCES documents.documents(id) ON DELETE CASCADE,
    from_status VARCHAR(20),
    to_status VARCHAR(20) NOT NULL,
    changed_by UUID,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_status_history_document ON documents.status_history(document_id);
CREATE INDEX idx_status_history_time ON documents.status_history(created_at DESC);

-- =============================================================================
-- Processing Jobs (Track processing attempts)
-- =============================================================================
CREATE TABLE documents.processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(50) NOT NULL REFERENCES documents.documents(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 3,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_jobs_document ON documents.processing_jobs(document_id);
CREATE INDEX idx_jobs_status ON documents.processing_jobs(status);
CREATE INDEX idx_jobs_pending ON documents.processing_jobs(status, created_at) 
    WHERE status = 'PENDING';

-- =============================================================================
-- Retention Policies
-- =============================================================================
CREATE TABLE documents.retention_policies (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    retention_days INT NOT NULL,
    archive_after_days INT,
    auto_delete BOOLEAN NOT NULL DEFAULT false,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed default retention policies
INSERT INTO documents.retention_policies (id, name, retention_days, archive_after_days, auto_delete, description) VALUES
    ('standard', 'Standard Retention', 730, 180, true, '2 years retention, archive after 6 months'),
    ('extended', 'Extended Retention', 2555, 365, true, '7 years retention, archive after 1 year'),
    ('legal', 'Legal Hold', -1, NULL, false, 'Indefinite retention, manual deletion only'),
    ('temporary', 'Temporary', 30, NULL, true, '30 days retention, auto-delete');

-- =============================================================================
-- Audit Log for Document Operations
-- =============================================================================
CREATE TABLE audit.document_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    document_id VARCHAR(50),
    user_id UUID,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_doc_events_tenant ON audit.document_events(tenant_id, created_at DESC);
CREATE INDEX idx_doc_events_document ON audit.document_events(document_id, created_at DESC);
CREATE INDEX idx_doc_events_type ON audit.document_events(event_type);
