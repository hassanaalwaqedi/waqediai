/**
 * Advanced Chat Composer
 * 
 * ChatGPT-style multimodal input with:
 * - Text input
 * - File attachment button
 * - Image upload button  
 * - Send button
 */

'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { useGuestStore } from '@/core/guest-store';

interface Attachment {
    id: string;
    file: File;
    type: 'image' | 'document';
    preview?: string;
}

interface ChatComposerProps {
    onSend: (message: string, attachments: Attachment[]) => void;
    isLoading?: boolean;
    disabled?: boolean;
}

export function ChatComposer({ onSend, isLoading, disabled }: ChatComposerProps) {
    const [input, setInput] = useState('');
    const [attachments, setAttachments] = useState<Attachment[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const imageInputRef = useRef<HTMLInputElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const { authState, triggerAuth } = useGuestStore();
    const isGuest = authState === 'guest';

    const handleSubmit = () => {
        if ((!input.trim() && attachments.length === 0) || isLoading || disabled) return;
        onSend(input.trim(), attachments);
        setInput('');
        setAttachments([]);
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>, type: 'image' | 'document') => {
        const files = e.target.files;
        if (!files) return;

        // Guest check
        if (isGuest) {
            triggerAuth({
                type: 'upload_document',
                message: 'Sign in to upload files',
            });
            e.target.value = '';
            return;
        }

        Array.from(files).forEach((file) => {
            const attachment: Attachment = {
                id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
                file,
                type,
            };

            // Create preview for images
            if (type === 'image') {
                const reader = new FileReader();
                reader.onload = (ev) => {
                    attachment.preview = ev.target?.result as string;
                    setAttachments((prev) => [...prev, attachment]);
                };
                reader.readAsDataURL(file);
            } else {
                setAttachments((prev) => [...prev, attachment]);
            }
        });

        e.target.value = '';
    };

    const removeAttachment = (id: string) => {
        setAttachments((prev) => prev.filter((a) => a.id !== id));
    };

    const handleAttachClick = () => {
        if (isGuest) {
            triggerAuth({
                type: 'upload_document',
                message: 'Sign in to upload documents',
            });
            return;
        }
        fileInputRef.current?.click();
    };

    const handleImageClick = () => {
        if (isGuest) {
            triggerAuth({
                type: 'upload_document',
                message: 'Sign in to upload images',
            });
            return;
        }
        imageInputRef.current?.click();
    };

    return (
        <div className="w-full">
            {/* Attachments Preview */}
            {attachments.length > 0 && (
                <div className="flex gap-2 mb-3 px-4 overflow-x-auto">
                    {attachments.map((attachment) => (
                        <div
                            key={attachment.id}
                            className="relative flex-shrink-0 bg-gray-800 rounded-lg border border-gray-700 p-2"
                        >
                            {attachment.type === 'image' && attachment.preview ? (
                                <img
                                    src={attachment.preview}
                                    alt="Preview"
                                    className="h-16 w-16 object-cover rounded"
                                />
                            ) : (
                                <div className="h-16 w-16 flex flex-col items-center justify-center">
                                    <DocumentIcon className="w-6 h-6 text-blue-400" />
                                    <span className="text-xs text-gray-400 mt-1 truncate max-w-[60px]">
                                        {attachment.file.name.split('.').pop()?.toUpperCase()}
                                    </span>
                                </div>
                            )}
                            <button
                                onClick={() => removeAttachment(attachment.id)}
                                className="absolute -top-2 -right-2 bg-gray-700 hover:bg-gray-600 rounded-full p-1"
                            >
                                <XIcon className="w-3 h-3 text-white" />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Input Container */}
            <div className="relative bg-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-2xl shadow-lg">
                <div className="flex items-end gap-2 p-3">
                    {/* Attach Button */}
                    <button
                        onClick={handleAttachClick}
                        className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition"
                        title={isGuest ? 'Sign in to upload documents' : 'Attach file'}
                    >
                        <AttachIcon className="w-5 h-5" />
                    </button>

                    {/* Image Button */}
                    <button
                        onClick={handleImageClick}
                        className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition"
                        title={isGuest ? 'Sign in to upload images' : 'Upload image'}
                    >
                        <ImageIcon className="w-5 h-5" />
                    </button>

                    {/* Text Input */}
                    <textarea
                        ref={textareaRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Message WaqediAI..."
                        rows={1}
                        className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none focus:outline-none py-2 max-h-32 scrollbar-thin"
                        style={{
                            minHeight: '24px',
                            height: 'auto',
                        }}
                        disabled={disabled}
                    />

                    {/* Send Button */}
                    <button
                        onClick={handleSubmit}
                        disabled={(!input.trim() && attachments.length === 0) || isLoading || disabled}
                        className="p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition"
                    >
                        {isLoading ? (
                            <LoadingSpinner className="w-5 h-5 text-white" />
                        ) : (
                            <SendIcon className="w-5 h-5 text-white" />
                        )}
                    </button>
                </div>
            </div>

            {/* Hidden File Inputs */}
            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                multiple
                className="hidden"
                onChange={(e) => handleFileSelect(e, 'document')}
            />
            <input
                ref={imageInputRef}
                type="file"
                accept="image/png,image/jpeg,image/gif,image/webp"
                multiple
                className="hidden"
                onChange={(e) => handleFileSelect(e, 'image')}
            />
        </div>
    );
}

// Icons
function AttachIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
        </svg>
    );
}

function ImageIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
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

function SendIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
    );
}

function XIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
    );
}

function LoadingSpinner({ className }: { className?: string }) {
    return (
        <svg className={`animate-spin ${className}`} fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
    );
}
