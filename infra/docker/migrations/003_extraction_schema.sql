-- =============================================================================
-- WaqediAI Extraction Schema Migration
-- Version: 003
-- Description: OCR and STT extraction results
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS extraction;

-- =============================================================================
-- Extraction Jobs
-- =============================================================================
CREATE TABLE extraction.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(50) NOT NULL,
    tenant_id UUID NOT NULL,
    job_type VARCHAR(20) NOT NULL CHECK (job_type IN ('ocr', 'stt')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_ext_jobs_document ON extraction.jobs(document_id);
CREATE INDEX idx_ext_jobs_status ON extraction.jobs(status);
CREATE INDEX idx_ext_jobs_pending ON extraction.jobs(status, created_at)
    WHERE status = 'pending';
CREATE INDEX idx_ext_jobs_tenant ON extraction.jobs(tenant_id);

-- =============================================================================
-- Extraction Results
-- =============================================================================
CREATE TABLE extraction.results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(50) NOT NULL UNIQUE,
    tenant_id UUID NOT NULL,
    extraction_type VARCHAR(20) NOT NULL CHECK (extraction_type IN ('ocr', 'stt')),
    
    -- Result data (JSONB for flexible storage)
    result_data JSONB NOT NULL,
    full_text TEXT,  -- Denormalized for search
    
    -- Metadata
    model_version VARCHAR(50) NOT NULL,
    processing_time_ms INT NOT NULL,
    mean_confidence FLOAT,
    detected_language VARCHAR(10),
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ext_results_document ON extraction.results(document_id);
CREATE INDEX idx_ext_results_tenant ON extraction.results(tenant_id);
CREATE INDEX idx_ext_results_language ON extraction.results(detected_language);
CREATE INDEX idx_ext_results_confidence ON extraction.results(mean_confidence);

-- Full text search on extracted content
CREATE INDEX idx_ext_results_text ON extraction.results 
    USING gin(to_tsvector('english', full_text));

-- =============================================================================
-- Audit Events
-- =============================================================================
CREATE TABLE audit.extraction_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    document_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ext_events_tenant ON audit.extraction_events(tenant_id, created_at DESC);
CREATE INDEX idx_ext_events_document ON audit.extraction_events(document_id);
