/**
 * Chat Service - Real RAG API Integration
 * 
 * Connects the chat UI to the RAG service backend.
 * Uses Ollama + Qwen for LLM generation - fully offline capable.
 */

import { ragApi } from '@/core/api-client';

export interface ChatRequest {
    message: string;
    session_id: string;
    mode: 'guest' | 'authenticated';
    tenant_id?: string;
    user_id?: string;
    top_k?: number;
    language?: string;
}

export interface Citation {
    chunk_id: string;
    document_id: string;
    text_excerpt: string;
}

export interface ChatResponse {
    answer: string;
    citations: Citation[];
    confidence: number;
    answer_type: string;
    language: string;
    trace_id?: string;
    latency_ms?: number;
}

/**
 * Send a message to the RAG service and get a real AI response.
 * 
 * Flow:
 * 1. Send query to RAG service
 * 2. RAG retrieves context from Qdrant (tenant-filtered)
 * 3. Context sent to Ollama/Qwen for generation
 * 4. Citation-backed answer returned
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const payload = {
        query: request.message,
        session_id: request.session_id,
        mode: request.mode,
        tenant_id: request.tenant_id || null,
        user_id: request.user_id || null,
        top_k: request.top_k || 5,
        language: request.language || null,
    };

    try {
        const response = await ragApi.post<ChatResponse>('/query', payload);
        return response.data;
    } catch (error: any) {
        // Handle Ollama unavailable
        if (error.code === 'ECONNREFUSED' || error.response?.status === 503) {
            return {
                answer: 'The AI service is currently unavailable. Please ensure Ollama is running and try again.',
                citations: [],
                confidence: 0,
                answer_type: 'error',
                language: 'en',
            };
        }

        // Handle timeout
        if (error.code === 'ECONNABORTED') {
            return {
                answer: 'The request timed out. Please try a shorter question or try again later.',
                citations: [],
                confidence: 0,
                answer_type: 'error',
                language: 'en',
            };
        }

        // Handle other errors gracefully
        console.error('RAG query failed:', error);
        return {
            answer: 'I encountered an error processing your request. Please try again.',
            citations: [],
            confidence: 0,
            answer_type: 'error',
            language: 'en',
        };
    }
}

/**
 * Check if the RAG service is healthy.
 */
export async function checkHealth(): Promise<boolean> {
    try {
        const response = await ragApi.get('/health');
        return response.data?.status === 'healthy';
    } catch {
        return false;
    }
}
