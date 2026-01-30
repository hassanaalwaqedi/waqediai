/**
 * Documents Management Page
 * 
 * Full-featured document upload and management interface.
 */

'use client';

import { useState, useCallback } from 'react';
import { useSession } from 'next-auth/react';
import { UploadZone, DocumentList } from '@/components/documents';
import { DocumentUploadResponse } from '@/services/documents';

export default function DocumentsPage() {
    const { data: session, status } = useSession();
    const [refreshTrigger, setRefreshTrigger] = useState(0);
    const [showUpload, setShowUpload] = useState(true);
    const [recentUpload, setRecentUpload] = useState<DocumentUploadResponse | null>(null);

    const handleUploadComplete = useCallback((doc: DocumentUploadResponse) => {
        setRecentUpload(doc);
        setRefreshTrigger(prev => prev + 1);

        // Clear notification after 5 seconds
        setTimeout(() => setRecentUpload(null), 5000);
    }, []);

    const handleUploadError = useCallback((error: Error) => {
        console.error('Upload error:', error);
    }, []);

    if (status === 'loading') {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-950">
                <div className="text-gray-400">Loading...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-950 to-gray-900">
            {/* Header */}
            <header className="sticky top-0 z-10 bg-gray-950/80 backdrop-blur-sm border-b border-gray-800/50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-xl font-semibold text-white">Documents</h1>
                            <p className="text-sm text-gray-400 mt-0.5">
                                Upload and manage your knowledge base
                            </p>
                        </div>
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => setShowUpload(!showUpload)}
                                className={`
                                    px-4 py-2 rounded-lg text-sm font-medium transition-colors
                                    ${showUpload
                                        ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                        : 'bg-blue-600 text-white hover:bg-blue-700'
                                    }
                                `}
                            >
                                {showUpload ? 'Hide Upload' : 'Upload Files'}
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
                {/* Success Notification */}
                {recentUpload && (
                    <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4 flex items-center gap-3">
                        <span className="text-2xl">✅</span>
                        <div className="flex-1">
                            <p className="text-sm font-medium text-green-400">
                                Document uploaded successfully
                            </p>
                            <p className="text-xs text-green-400/70 mt-0.5">
                                {recentUpload.filename} • {recentUpload.file_category}
                            </p>
                        </div>
                        <button
                            onClick={() => setRecentUpload(null)}
                            className="text-green-400/70 hover:text-green-400"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                )}

                {/* Upload Zone */}
                {showUpload && (
                    <section>
                        <UploadZone
                            onUploadComplete={handleUploadComplete}
                            onUploadError={handleUploadError}
                        />
                    </section>
                )}

                {/* Document List */}
                <section>
                    <DocumentList
                        refreshTrigger={refreshTrigger}
                        onDocumentSelect={(id) => {
                            console.log('Selected document:', id);
                            // TODO: Navigate to document detail or open modal
                        }}
                    />
                </section>
            </main>
        </div>
    );
}
