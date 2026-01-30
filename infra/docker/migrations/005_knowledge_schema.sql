-- =============================================================================
-- WaqediAI Knowledge/Chunking Schema Migration
-- Version: 005
-- Description: Knowledge chunks for semantic retrieval
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS knowledge;

-- =============================================================================
-- Chunks
-- =============================================================================
CREATE TABLE knowledge.chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(50) NOT NULL,
    tenant_id UUID NOT NULL,
    
    text TEXT NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    
    page_number INT,
    chunk_index INT NOT NULL,
    token_count INT NOT NULL,
    
    strategy VARCHAR(20) NOT NULL,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chunks_document ON knowledge.chunks(document_id);
CREATE INDEX idx_chunks_tenant ON knowledge.chunks(tenant_id);
CREATE INDEX idx_chunks_language ON knowledge.chunks(language);

-- Full text search
CREATE INDEX idx_chunks_text ON knowledge.chunks 
    USING gin(to_tsvector('simple', text));

-- =============================================================================
-- Processing Jobs
-- =============================================================================
CREATE TABLE knowledge.chunking_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(50) NOT NULL,
    tenant_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    chunk_count INT DEFAULT 0,
    strategy VARCHAR(20) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_chunk_jobs_document ON knowledge.chunking_jobs(document_id);
CREATE INDEX idx_chunk_jobs_status ON knowledge.chunking_jobs(status);
