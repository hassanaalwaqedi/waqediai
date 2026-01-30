/**
 * Knowledge / RAG service
 */

import axios from 'axios';
import Cookies from 'js-cookie';
import { API_ENDPOINTS } from '@/core/api-client';

export interface RAGQuery {
    query: string;
    top_k?: number;
    conversation_id?: string;
    filters?: Record<string, string>;
}

export interface Citation {
    chunk_id: string;
    document_id: string;
    text_excerpt: string;
}

export interface RAGResponse {
    answer: string;
    citations: Citation[];
    confidence: number;
    answer_type: string;
    language: string;
    trace_id?: string;
    latency_ms?: number;
}

const ragClient = axios.create({
    baseURL: API_ENDPOINTS.rag,
    timeout: 120000,
    withCredentials: true,
});

// Add auth headers
ragClient.interceptors.request.use((config) => {
    const token = Cookies.get('access_token');
    const tenantId = Cookies.get('tenant_id');

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    if (tenantId) {
        config.headers['X-Tenant-ID'] = tenantId;
    }

    return config;
});

/**
 * Execute RAG query
 */
export async function queryKnowledge(params: RAGQuery): Promise<RAGResponse> {
    const tenantId = Cookies.get('tenant_id');
    if (!tenantId) {
        throw new Error('No tenant context');
    }

    const response = await ragClient.post('/query', {
        tenant_id: tenantId,
        ...params,
    });

    return response.data;
}

/**
 * Get conversation history
 */
export async function getConversationHistory(conversationId: string): Promise<RAGResponse[]> {
    const response = await ragClient.get(`/conversations/${conversationId}`);
    return response.data;
}
