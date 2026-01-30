/**
 * Status Badge Component
 * 
 * Displays document processing status with appropriate styling.
 */

'use client';

import { clsx } from 'clsx';

export type DocumentStatus =
    | 'UPLOADED'
    | 'VALIDATED'
    | 'QUEUED'
    | 'PROCESSING'
    | 'PROCESSED'
    | 'FAILED'
    | 'ARCHIVED'
    | 'REJECTED'
    | 'DELETED';

interface StatusBadgeProps {
    status: string;
    size?: 'sm' | 'md';
}

const STATUS_CONFIG: Record<string, { label: string; className: string; animate?: boolean }> = {
    UPLOADED: {
        label: 'Uploaded',
        className: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    },
    VALIDATED: {
        label: 'Validated',
        className: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    },
    QUEUED: {
        label: 'Queued',
        className: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
        animate: true,
    },
    PROCESSING: {
        label: 'Processing',
        className: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
        animate: true,
    },
    PROCESSED: {
        label: 'Processed',
        className: 'bg-green-500/10 text-green-400 border-green-500/20',
    },
    FAILED: {
        label: 'Failed',
        className: 'bg-red-500/10 text-red-400 border-red-500/20',
    },
    ARCHIVED: {
        label: 'Archived',
        className: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
    },
    REJECTED: {
        label: 'Rejected',
        className: 'bg-red-500/10 text-red-400 border-red-500/20',
    },
    DELETED: {
        label: 'Deleted',
        className: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
    },
};

export function StatusBadge({ status, size = 'sm' }: StatusBadgeProps) {
    const config = STATUS_CONFIG[status.toUpperCase()] ?? {
        label: status,
        className: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
    };

    return (
        <span
            className={clsx(
                'inline-flex items-center gap-1.5 rounded-full border font-medium',
                config.className,
                size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'
            )}
        >
            {config.animate && (
                <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-current" />
                </span>
            )}
            {config.label}
        </span>
    );
}
