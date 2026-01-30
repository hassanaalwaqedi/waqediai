/**
 * Upload Zone Component
 * 
 * Drag-and-drop file upload with progress tracking.
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import { clsx } from 'clsx';
import {
    uploadDocument,
    isAllowedFileType,
    getMaxFileSize,
    formatFileSize,
    ALLOWED_FILE_TYPES,
    DocumentUploadResponse
} from '@/services/documents';

interface UploadZoneProps {
    onUploadComplete?: (doc: DocumentUploadResponse) => void;
    onUploadError?: (error: Error) => void;
    collectionId?: string;
}

interface UploadingFile {
    id: string;
    file: File;
    progress: number;
    status: 'uploading' | 'success' | 'error';
    error?: string;
}

export function UploadZone({ onUploadComplete, onUploadError, collectionId }: UploadZoneProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [uploads, setUploads] = useState<UploadingFile[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const processFile = async (file: File) => {
        // Validate file type
        if (!isAllowedFileType(file)) {
            const error = `File type ${file.type || 'unknown'} not supported`;
            onUploadError?.(new Error(error));
            return;
        }

        // Validate file size
        const maxSize = getMaxFileSize(file);
        if (file.size > maxSize) {
            const error = `File too large. Maximum size is ${formatFileSize(maxSize)}`;
            onUploadError?.(new Error(error));
            return;
        }

        const uploadId = `upload_${Date.now()}_${Math.random().toString(36).slice(2)}`;

        // Add to upload list
        setUploads(prev => [...prev, {
            id: uploadId,
            file,
            progress: 0,
            status: 'uploading',
        }]);

        try {
            const result = await uploadDocument(
                file,
                collectionId,
                (progress) => {
                    setUploads(prev => prev.map(u =>
                        u.id === uploadId ? { ...u, progress } : u
                    ));
                }
            );

            setUploads(prev => prev.map(u =>
                u.id === uploadId ? { ...u, status: 'success', progress: 100 } : u
            ));

            onUploadComplete?.(result);

            // Remove from list after delay
            setTimeout(() => {
                setUploads(prev => prev.filter(u => u.id !== uploadId));
            }, 2000);

        } catch (err) {
            const error = err instanceof Error ? err.message : 'Upload failed';
            setUploads(prev => prev.map(u =>
                u.id === uploadId ? { ...u, status: 'error', error } : u
            ));
            onUploadError?.(new Error(error));
        }
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const files = Array.from(e.dataTransfer.files);
        files.forEach(processFile);
    }, [collectionId]);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        files.forEach(processFile);
        // Reset input
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    }, [collectionId]);

    const allowedTypes = Object.keys(ALLOWED_FILE_TYPES).join(',');

    return (
        <div className="space-y-4">
            {/* Drop Zone */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={clsx(
                    'relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
                    isDragging
                        ? 'border-blue-500 bg-blue-500/10 scale-[1.02]'
                        : 'border-gray-700 hover:border-gray-600 hover:bg-gray-800/50'
                )}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept={allowedTypes}
                    onChange={handleFileSelect}
                    className="hidden"
                />

                <div className="flex flex-col items-center gap-3">
                    <div className={clsx(
                        'w-14 h-14 rounded-full flex items-center justify-center transition-colors',
                        isDragging ? 'bg-blue-500/20' : 'bg-gray-800'
                    )}>
                        <svg
                            className={clsx(
                                'w-7 h-7 transition-colors',
                                isDragging ? 'text-blue-400' : 'text-gray-400'
                            )}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={1.5}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                    </div>

                    <div>
                        <p className={clsx(
                            'text-base font-medium transition-colors',
                            isDragging ? 'text-blue-400' : 'text-gray-300'
                        )}>
                            {isDragging ? 'Drop files here' : 'Drop files or click to upload'}
                        </p>
                        <p className="text-sm text-gray-500 mt-1">
                            PDF, Images, Audio, Video up to 2GB
                        </p>
                    </div>
                </div>
            </div>

            {/* Upload Progress */}
            {uploads.length > 0 && (
                <div className="space-y-2">
                    {uploads.map((upload) => (
                        <div
                            key={upload.id}
                            className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg"
                        >
                            <div className="flex-shrink-0 text-2xl">
                                {upload.status === 'success' ? '✅' : upload.status === 'error' ? '❌' : '📄'}
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-200 truncate">
                                    {upload.file.name}
                                </p>
                                <p className="text-xs text-gray-500">
                                    {formatFileSize(upload.file.size)}
                                </p>
                            </div>
                            <div className="flex-shrink-0 w-24">
                                {upload.status === 'uploading' && (
                                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-blue-500 transition-all duration-300"
                                            style={{ width: `${upload.progress}%` }}
                                        />
                                    </div>
                                )}
                                {upload.status === 'success' && (
                                    <span className="text-xs text-green-400">Complete</span>
                                )}
                                {upload.status === 'error' && (
                                    <span className="text-xs text-red-400 truncate" title={upload.error}>
                                        Failed
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
