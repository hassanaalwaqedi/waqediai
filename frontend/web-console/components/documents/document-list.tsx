/**
 * Document List Component
 * 
 * Paginated grid of documents with filters.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { DocumentCard } from './document-card';
import { listDocuments, DocumentListItem, DocumentListResponse } from '@/services/documents';

interface DocumentListProps {
    refreshTrigger?: number;
    onDocumentSelect?: (documentId: string) => void;
}

type FilterStatus = '' | 'UPLOADED' | 'PROCESSING' | 'PROCESSED' | 'FAILED';
type FilterCategory = '' | 'DOCUMENT' | 'IMAGE' | 'AUDIO' | 'VIDEO';

export function DocumentList({ refreshTrigger = 0, onDocumentSelect }: DocumentListProps) {
    const [documents, setDocuments] = useState<DocumentListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [nextCursor, setNextCursor] = useState<string | null>(null);
    const [hasMore, setHasMore] = useState(false);

    // Filters
    const [statusFilter, setStatusFilter] = useState<FilterStatus>('');
    const [categoryFilter, setCategoryFilter] = useState<FilterCategory>('');

    const fetchDocuments = useCallback(async (cursor?: string) => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await listDocuments({
                limit: 20,
                cursor,
                status: statusFilter || undefined,
                file_category: categoryFilter || undefined,
            });

            if (cursor) {
                setDocuments(prev => [...prev, ...response.items]);
            } else {
                setDocuments(response.items);
            }

            setNextCursor(response.next_cursor ?? null);
            setHasMore(!!response.next_cursor);
        } catch (err) {
            console.error('Failed to fetch documents:', err);
            setError('Failed to load documents. Please try again.');
        } finally {
            setIsLoading(false);
        }
    }, [statusFilter, categoryFilter]);

    // Fetch on mount and filter change
    useEffect(() => {
        fetchDocuments();
    }, [fetchDocuments, refreshTrigger]);

    const handleLoadMore = () => {
        if (nextCursor && !isLoading) {
            fetchDocuments(nextCursor);
        }
    };

    const handleDelete = (documentId: string) => {
        setDocuments(prev => prev.filter(d => d.document_id !== documentId));
    };

    const statusOptions: { value: FilterStatus; label: string }[] = [
        { value: '', label: 'All Status' },
        { value: 'UPLOADED', label: 'Uploaded' },
        { value: 'PROCESSING', label: 'Processing' },
        { value: 'PROCESSED', label: 'Processed' },
        { value: 'FAILED', label: 'Failed' },
    ];

    const categoryOptions: { value: FilterCategory; label: string }[] = [
        { value: '', label: 'All Types' },
        { value: 'DOCUMENT', label: 'Documents' },
        { value: 'IMAGE', label: 'Images' },
        { value: 'AUDIO', label: 'Audio' },
        { value: 'VIDEO', label: 'Video' },
    ];

    return (
        <div className="space-y-4">
            {/* Filters */}
            <div className="flex flex-wrap gap-3">
                <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value as FilterStatus)}
                    className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    {statusOptions.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                </select>

                <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value as FilterCategory)}
                    className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    {categoryOptions.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                </select>

                <button
                    onClick={() => fetchDocuments()}
                    className="px-3 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm text-gray-300 transition-colors flex items-center gap-2"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Refresh
                </button>
            </div>

            {/* Error State */}
            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                    {error}
                </div>
            )}

            {/* Loading State */}
            {isLoading && documents.length === 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[...Array(6)].map((_, i) => (
                        <div key={i} className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4 animate-pulse">
                            <div className="flex items-start gap-3">
                                <div className="w-10 h-10 bg-gray-700 rounded-lg" />
                                <div className="flex-1">
                                    <div className="h-4 bg-gray-700 rounded w-3/4 mb-2" />
                                    <div className="h-3 bg-gray-700 rounded w-1/2" />
                                </div>
                            </div>
                            <div className="mt-3 h-5 bg-gray-700 rounded w-20" />
                        </div>
                    ))}
                </div>
            )}

            {/* Empty State */}
            {!isLoading && documents.length === 0 && !error && (
                <div className="text-center py-12">
                    <div className="w-16 h-16 mx-auto mb-4 bg-gray-800 rounded-full flex items-center justify-center">
                        <span className="text-3xl">📭</span>
                    </div>
                    <h3 className="text-lg font-medium text-gray-300 mb-1">No documents yet</h3>
                    <p className="text-sm text-gray-500">Upload your first document to get started</p>
                </div>
            )}

            {/* Document Grid */}
            {documents.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {documents.map((doc) => (
                        <DocumentCard
                            key={doc.document_id}
                            document={doc}
                            onDelete={handleDelete}
                            onView={onDocumentSelect}
                        />
                    ))}
                </div>
            )}

            {/* Load More */}
            {hasMore && (
                <div className="text-center pt-4">
                    <button
                        onClick={handleLoadMore}
                        disabled={isLoading}
                        className="px-6 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm text-gray-300 transition-colors disabled:opacity-50"
                    >
                        {isLoading ? 'Loading...' : 'Load More'}
                    </button>
                </div>
            )}
        </div>
    );
}
