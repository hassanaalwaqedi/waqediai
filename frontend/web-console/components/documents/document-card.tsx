/**
 * Document Card Component
 * 
 * Displays a single document with status and actions.
 */

'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { clsx } from 'clsx';
import { StatusBadge } from './status-badge';
import {
    DocumentListItem,
    getFileCategoryIcon,
    formatFileSize,
    deleteDocument
} from '@/services/documents';

interface DocumentCardProps {
    document: DocumentListItem;
    onDelete?: (documentId: string) => void;
    onView?: (documentId: string) => void;
}

export function DocumentCard({ document, onDelete, onView }: DocumentCardProps) {
    const [isDeleting, setIsDeleting] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);

    const handleDelete = async () => {
        if (!showConfirm) {
            setShowConfirm(true);
            return;
        }

        setIsDeleting(true);
        try {
            await deleteDocument(document.document_id);
            onDelete?.(document.document_id);
        } catch (error) {
            console.error('Failed to delete document:', error);
        } finally {
            setIsDeleting(false);
            setShowConfirm(false);
        }
    };

    const icon = getFileCategoryIcon(document.file_category);
    const uploadDate = format(new Date(document.uploaded_at), 'MMM d, yyyy');

    return (
        <div className={clsx(
            'group relative bg-gray-800/50 border border-gray-700/50 rounded-xl p-4',
            'hover:border-gray-600 hover:bg-gray-800 transition-all duration-200',
            isDeleting && 'opacity-50 pointer-events-none'
        )}>
            {/* File Icon and Info */}
            <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-10 h-10 bg-gray-700/50 rounded-lg flex items-center justify-center text-xl">
                    {icon}
                </div>
                <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-200 truncate pr-8">
                        {document.filename}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-500">
                            {formatFileSize(document.size_bytes)}
                        </span>
                        <span className="text-gray-600">•</span>
                        <span className="text-xs text-gray-500">
                            {uploadDate}
                        </span>
                    </div>
                </div>
            </div>

            {/* Status Badge */}
            <div className="mt-3">
                <StatusBadge status={document.status} />
            </div>

            {/* Actions (visible on hover) */}
            <div className={clsx(
                'absolute top-3 right-3 flex items-center gap-1',
                'opacity-0 group-hover:opacity-100 transition-opacity'
            )}>
                {onView && (
                    <button
                        onClick={() => onView(document.document_id)}
                        className="p-1.5 text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded-md transition-colors"
                        title="View details"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                    </button>
                )}
                <button
                    onClick={handleDelete}
                    className={clsx(
                        'p-1.5 rounded-md transition-colors',
                        showConfirm
                            ? 'text-red-400 bg-red-500/10 hover:bg-red-500/20'
                            : 'text-gray-400 hover:text-red-400 hover:bg-gray-700'
                    )}
                    title={showConfirm ? 'Click again to confirm' : 'Delete'}
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </div>

            {/* Delete Confirmation Overlay */}
            {showConfirm && (
                <div className="absolute inset-0 bg-gray-900/80 rounded-xl flex items-center justify-center">
                    <div className="text-center">
                        <p className="text-sm text-gray-300 mb-3">Delete this document?</p>
                        <div className="flex gap-2 justify-center">
                            <button
                                onClick={() => setShowConfirm(false)}
                                className="px-3 py-1.5 text-xs bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-lg transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleDelete}
                                className="px-3 py-1.5 text-xs bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
