/**
 * Message Bubble Component
 * 
 * Renders chat messages with:
 * - User/AI distinction
 * - Attachment previews
 * - Message actions (copy, regenerate)
 * - Citation badges
 */

'use client';

import { useState } from 'react';

interface Attachment {
    id: string;
    type: 'image' | 'document';
    name: string;
    preview?: string;
    url?: string;
}

interface Citation {
    id: string;
    title: string;
    page?: number;
    snippet?: string;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    attachments?: Attachment[];
    citations?: Citation[];
    isStreaming?: boolean;
    isLowConfidence?: boolean;
}

interface MessageBubbleProps {
    message: Message;
    onRegenerate?: () => void;
    onCitationClick?: (citation: Citation) => void;
}

export function MessageBubble({ message, onRegenerate, onCitationClick }: MessageBubbleProps) {
    const [showActions, setShowActions] = useState(false);
    const [copied, setCopied] = useState(false);

    const isUser = message.role === 'user';
    const isAssistant = message.role === 'assistant';

    const handleCopy = async () => {
        await navigator.clipboard.writeText(message.content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div
            className={`group flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}
            onMouseEnter={() => setShowActions(true)}
            onMouseLeave={() => setShowActions(false)}
        >
            {/* Avatar */}
            <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser
                        ? 'bg-blue-600'
                        : 'bg-gradient-to-br from-emerald-500 to-teal-600'
                    }`}
            >
                {isUser ? (
                    <UserIcon className="w-4 h-4 text-white" />
                ) : (
                    <BotIcon className="w-4 h-4 text-white" />
                )}
            </div>

            {/* Content */}
            <div className={`flex-1 max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
                {/* Attachments */}
                {message.attachments && message.attachments.length > 0 && (
                    <div className="flex gap-2 mb-2 flex-wrap">
                        {message.attachments.map((attachment) => (
                            <div
                                key={attachment.id}
                                className="bg-gray-800 rounded-lg border border-gray-700 p-2"
                            >
                                {attachment.type === 'image' && attachment.preview ? (
                                    <img
                                        src={attachment.preview}
                                        alt={attachment.name}
                                        className="max-h-40 rounded"
                                    />
                                ) : (
                                    <div className="flex items-center gap-2 px-2">
                                        <DocumentIcon className="w-5 h-5 text-blue-400" />
                                        <span className="text-sm text-gray-300">{attachment.name}</span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Message Bubble */}
                <div
                    className={`relative rounded-2xl px-4 py-3 ${isUser
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-800 text-gray-100 border border-gray-700'
                        }`}
                >
                    {/* Streaming indicator */}
                    {message.isStreaming && (
                        <div className="flex items-center gap-2 mb-2 text-sm text-gray-400">
                            <LoadingDots />
                            <span>Thinking...</span>
                        </div>
                    )}

                    {/* Content */}
                    <div className="whitespace-pre-wrap">{message.content}</div>

                    {/* Low confidence warning */}
                    {message.isLowConfidence && !isUser && (
                        <div className="mt-2 flex items-center gap-1 text-xs text-yellow-400">
                            <WarningIcon className="w-3 h-3" />
                            <span>Low confidence - verify this information</span>
                        </div>
                    )}

                    {/* Citations */}
                    {message.citations && message.citations.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-700">
                            <div className="text-xs text-gray-400 mb-2">Sources</div>
                            <div className="flex flex-wrap gap-2">
                                {message.citations.map((citation) => (
                                    <button
                                        key={citation.id}
                                        onClick={() => onCitationClick?.(citation)}
                                        className="flex items-center gap-1 px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition"
                                    >
                                        <DocumentIcon className="w-3 h-3" />
                                        <span className="max-w-[120px] truncate">{citation.title}</span>
                                        {citation.page && (
                                            <span className="text-gray-500">p.{citation.page}</span>
                                        )}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Actions (on hover) */}
                {isAssistant && showActions && !message.isStreaming && (
                    <div className="flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <ActionButton onClick={handleCopy} title={copied ? 'Copied!' : 'Copy'}>
                            {copied ? <CheckIcon className="w-4 h-4" /> : <CopyIcon className="w-4 h-4" />}
                        </ActionButton>
                        {onRegenerate && (
                            <ActionButton onClick={onRegenerate} title="Regenerate">
                                <RefreshIcon className="w-4 h-4" />
                            </ActionButton>
                        )}
                        {message.citations && message.citations.length > 0 && (
                            <ActionButton onClick={() => { }} title="View sources">
                                <SourceIcon className="w-4 h-4" />
                            </ActionButton>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

function ActionButton({
    onClick,
    title,
    children,
}: {
    onClick: () => void;
    title: string;
    children: React.ReactNode;
}) {
    return (
        <button
            onClick={onClick}
            title={title}
            className="p-1.5 text-gray-500 hover:text-white hover:bg-gray-700 rounded transition"
        >
            {children}
        </button>
    );
}

function LoadingDots() {
    return (
        <div className="flex gap-1">
            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
    );
}

// Icons
function UserIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
    );
}

function BotIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1v1a2 2 0 01-2 2H6a2 2 0 01-2-2v-1H3a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2M7.5 13A1.5 1.5 0 006 14.5 1.5 1.5 0 007.5 16 1.5 1.5 0 009 14.5 1.5 1.5 0 007.5 13m9 0a1.5 1.5 0 00-1.5 1.5 1.5 1.5 0 001.5 1.5 1.5 1.5 0 001.5-1.5 1.5 1.5 0 00-1.5-1.5M12 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
        </svg>
    );
}

function DocumentIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
    );
}

function CopyIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
    );
}

function RefreshIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
    );
}

function SourceIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
    );
}

function CheckIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
    );
}

function WarningIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
    );
}
