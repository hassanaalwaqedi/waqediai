/**
 * Document ingestion service
 * 
 * Connects to ingestion-service API for file upload and management.
 */

import axios from 'axios';
import { tokenManager } from '@/core/api-client';

const INGESTION_API = process.env.NEXT_PUBLIC_INGESTION_API || 'http://localhost:8002';

// Types matching ingestion-service schemas
export interface DocumentUploadResponse {
    document_id: string;
    status: string;
    filename: string;
    content_type: string;
    size_bytes: number;
    file_category: string;
    uploaded_at: string;
}

export interface Document {
    document_id: string;
    filename: string;
    content_type: string;
    size_bytes: number;
    file_category: string;
    status: string;
    language?: string;
    retention_policy: string;
    legal_hold: boolean;
    uploaded_by: string;
    department_id?: string;
    collection_id?: string;
    uploaded_at: string;
    validated_at?: string;
    processed_at?: string;
}

export interface DocumentListItem {
    document_id: string;
    filename: string;
    content_type: string;
    size_bytes: number;
    file_category: string;
    status: string;
    uploaded_at: string;
}

export interface DocumentListResponse {
    items: DocumentListItem[];
    next_cursor?: string;
    total_count?: number;
}

export interface DeleteResponse {
    document_id: string;
    status: string;
    message: string;
}

// Create axios client for ingestion service
const ingestionClient = axios.create({
    baseURL: INGESTION_API,
    timeout: 300000, // 5 min for large uploads
    withCredentials: true,
});

// Add auth headers
ingestionClient.interceptors.request.use((config) => {
    const token = tokenManager.getAccessToken();
    const tenantId = tokenManager.getTenantId();

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    if (tenantId) {
        config.headers['X-Tenant-ID'] = tenantId;
    }

    return config;
});

/**
 * Upload a document to the ingestion service
 */
export async function uploadDocument(
    file: File,
    collectionId?: string,
    onProgress?: (percent: number) => void
): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    if (collectionId) {
        formData.append('collection_id', collectionId);
    }

    const response = await ingestionClient.post('/api/v1/documents', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
            if (onProgress && progressEvent.total) {
                const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                onProgress(percent);
            }
        },
    });

    return response.data;
}

/**
 * List documents with pagination and filters
 */
export async function listDocuments(params?: {
    limit?: number;
    cursor?: string;
    status?: string;
    file_category?: string;
    collection_id?: string;
}): Promise<DocumentListResponse> {
    const response = await ingestionClient.get('/api/v1/documents', {
        params: {
            limit: params?.limit ?? 20,
            cursor: params?.cursor,
            status: params?.status,
            file_category: params?.file_category,
            collection_id: params?.collection_id,
        },
    });

    return response.data;
}

/**
 * Get a single document by ID
 */
export async function getDocument(documentId: string): Promise<Document> {
    const response = await ingestionClient.get(`/api/v1/documents/${documentId}`);
    return response.data;
}

/**
 * Delete a document (soft delete)
 */
export async function deleteDocument(documentId: string): Promise<DeleteResponse> {
    const response = await ingestionClient.delete(`/api/v1/documents/${documentId}`);
    return response.data;
}

/**
 * Get file category icon
 */
export function getFileCategoryIcon(category: string): string {
    switch (category.toUpperCase()) {
        case 'DOCUMENT':
            return '📄';
        case 'IMAGE':
            return '🖼️';
        case 'AUDIO':
            return '🎵';
        case 'VIDEO':
            return '🎬';
        default:
            return '📁';
    }
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

/**
 * Allowed file types for upload
 */
export const ALLOWED_FILE_TYPES = {
    'application/pdf': { label: 'PDF', maxSize: 100 * 1024 * 1024 },
    'image/png': { label: 'PNG', maxSize: 50 * 1024 * 1024 },
    'image/jpeg': { label: 'JPEG', maxSize: 50 * 1024 * 1024 },
    'audio/mpeg': { label: 'MP3', maxSize: 500 * 1024 * 1024 },
    'audio/wav': { label: 'WAV', maxSize: 500 * 1024 * 1024 },
    'video/mp4': { label: 'MP4', maxSize: 2048 * 1024 * 1024 },
};

export function isAllowedFileType(file: File): boolean {
    return file.type in ALLOWED_FILE_TYPES;
}

export function getMaxFileSize(file: File): number {
    const config = ALLOWED_FILE_TYPES[file.type as keyof typeof ALLOWED_FILE_TYPES];
    return config?.maxSize ?? 100 * 1024 * 1024;
}
