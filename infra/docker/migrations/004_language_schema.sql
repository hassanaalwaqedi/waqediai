-- =============================================================================
-- WaqediAI Language Schema Migration
-- Version: 004
-- Description: Linguistic artifacts and processing metadata
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS language;

-- =============================================================================
-- Linguistic Artifacts
-- =============================================================================
CREATE TABLE language.artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(50) NOT NULL,
    tenant_id UUID NOT NULL,
    
    -- Text content
    original_text TEXT NOT NULL,
    normalized_text TEXT NOT NULL,
    translated_text TEXT,
    
    -- Language info
    language_code VARCHAR(10) NOT NULL,
    detection_confidence FLOAT NOT NULL,
    script VARCHAR(20),
    
    -- Normalization
    normalization_version VARCHAR(20) NOT NULL,
    normalization_changes JSONB DEFAULT '[]',
    
    -- Translation
    is_translated BOOLEAN DEFAULT false,
    translation_engine VARCHAR(50),
    translation_source_id UUID,
    
    -- Position
    page_number INT,
    segment_index INT NOT NULL,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lang_artifacts_document ON language.artifacts(document_id);
CREATE INDEX idx_lang_artifacts_tenant ON language.artifacts(tenant_id);
CREATE INDEX idx_lang_artifacts_language ON language.artifacts(language_code);
CREATE INDEX idx_lang_artifacts_confidence ON language.artifacts(detection_confidence);

-- Full text search on normalized text
CREATE INDEX idx_lang_artifacts_text ON language.artifacts 
    USING gin(to_tsvector('simple', normalized_text));

-- =============================================================================
-- Translation Configurations (per tenant)
-- =============================================================================
CREATE TABLE language.translation_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL UNIQUE,
    strategy VARCHAR(20) NOT NULL DEFAULT 'native'
        CHECK (strategy IN ('native', 'canonical', 'hybrid')),
    canonical_language VARCHAR(10) DEFAULT 'en',
    translate_on_ingest BOOLEAN DEFAULT false,
    translation_engine VARCHAR(50) DEFAULT 'google',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trans_config_tenant ON language.translation_configs(tenant_id);

-- =============================================================================
-- Processing Jobs
-- =============================================================================
CREATE TABLE language.processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(50) NOT NULL,
    tenant_id UUID NOT NULL,
    extraction_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    artifacts_count INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_lang_jobs_document ON language.processing_jobs(document_id);
CREATE INDEX idx_lang_jobs_status ON language.processing_jobs(status);

-- =============================================================================
-- Audit Events
-- =============================================================================
CREATE TABLE audit.language_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    document_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lang_events_tenant ON audit.language_events(tenant_id, created_at DESC);
CREATE INDEX idx_lang_events_document ON audit.language_events(document_id);
