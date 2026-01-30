/**
 * Chat Page - Production Quality
 * 
 * ChatGPT-style interface with:
 * - Welcome panel for empty state
 * - Multimodal chat composer
 * - Message bubbles with actions
 * - Guest mode support
 */

'use client';

import { useEffect, useState, useRef, useMemo } from 'react';
import { useSession } from 'next-auth/react';
import { useGuestStore } from '@/core/guest-store';
import { AuthModal } from '@/components/auth-modal';
import { ChatComposer } from '@/components/chat/chat-composer';
import { WelcomePanel } from '@/components/chat/welcome-panel';
import { MessageBubble, Message } from '@/components/chat/message-bubble';
import { sendMessage as sendRagMessage } from '@/services/chat-service';

interface Attachment {
    id: string;
    file: File;
    type: 'image' | 'document';
    preview?: string;
}

export default function HomePage() {
    const { data: session, status } = useSession();
    const {
        authState,
        guestSession,
        initGuestSession,
        setAuthState,
        decrementMessages,
        upgradeToUser,
    } = useGuestStore();

    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Generate stable session ID for guest tracking
    const sessionId = useMemo(() => {
        if (typeof window !== 'undefined') {
            let id = sessionStorage.getItem('waqedi_session_id');
            if (!id) {
                id = `session_${Date.now()}_${Math.random().toString(36).slice(2)}`;
                sessionStorage.setItem('waqedi_session_id', id);
            }
            return id;
        }
        return `session_${Date.now()}`;
    }, []);

    const isGuest = authState === 'guest';
    const hasMessages = messages.length > 0;

    // Initialize auth state
    useEffect(() => {
        if (status === 'authenticated' && session) {
            setAuthState('authenticated');
            upgradeToUser(session.userId);
        } else if (status === 'unauthenticated') {
            if (!guestSession) {
                initGuestSession();
            } else {
                setAuthState('guest');
            }
        }
    }, [status, session]);

    // Scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async (content: string, attachments: Attachment[]) => {
        if (!content.trim() && attachments.length === 0) return;

        // Add user message
        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content,
            timestamp: new Date(),
            attachments: attachments.map((a) => ({
                id: a.id,
                type: a.type,
                name: a.file.name,
                preview: a.preview,
            })),
        };

        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);

        // Decrement guest messages
        if (isGuest) {
            decrementMessages();
        }

        // Add streaming placeholder
        const assistantId = (Date.now() + 1).toString();
        setMessages((prev) => [
            ...prev,
            {
                id: assistantId,
                role: 'assistant',
                content: '',
                timestamp: new Date(),
                isStreaming: true,
            },
        ]);

        try {
            // Call real RAG API - Ollama + Qwen for LLM generation
            const ragResponse = await sendRagMessage({
                message: content,
                session_id: sessionId,
                mode: isGuest ? 'guest' : 'authenticated',
                tenant_id: session?.tenantId as string | undefined,
                user_id: session?.userId as string | undefined,
            });

            // Convert RAG citations to UI format
            const uiCitations = ragResponse.citations.length > 0
                ? ragResponse.citations.map((c, idx) => ({
                    id: c.chunk_id,
                    title: c.document_id,
                    page: idx + 1,
                    excerpt: c.text_excerpt,
                }))
                : undefined;

            // Update with real AI response
            setMessages((prev) =>
                prev.map((m) =>
                    m.id === assistantId
                        ? {
                            ...m,
                            content: ragResponse.answer,
                            isStreaming: false,
                            citations: uiCitations,
                            confidence: ragResponse.confidence,
                            traceId: ragResponse.trace_id,
                        }
                        : m
                )
            );
        } catch (error) {
            console.error('Failed to send message:', error);
            setMessages((prev) =>
                prev.map((m) =>
                    m.id === assistantId
                        ? {
                            ...m,
                            content: 'Sorry, I encountered an error. Please try again.',
                            isStreaming: false,
                        }
                        : m
                )
            );
        } finally {
            setIsLoading(false);
        }
    };

    const handlePromptClick = (prompt: string) => {
        handleSend(prompt, []);
    };

    const handleRegenerate = (messageId: string) => {
        // Find the user message before this assistant message and resend
        const index = messages.findIndex((m) => m.id === messageId);
        if (index > 0) {
            const userMessage = messages[index - 1];
            if (userMessage.role === 'user') {
                // Remove the assistant message and resend
                setMessages((prev) => prev.filter((m) => m.id !== messageId));
                handleSend(userMessage.content, []);
            }
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gradient-to-b from-gray-950 via-gray-950 to-gray-900">
            {/* Header */}
            <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800/50 backdrop-blur-sm">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center">
                        <span className="text-lg">🧠</span>
                    </div>
                    <h1 className="text-lg font-semibold text-white">WaqediAI</h1>

                    {isGuest && guestSession && (
                        <span className="text-xs bg-yellow-500/10 text-yellow-400 px-2.5 py-1 rounded-full border border-yellow-500/20">
                            Guest · {guestSession.messagesRemaining} messages left
                        </span>
                    )}
                </div>

                {isGuest ? (
                    <button
                        onClick={() =>
                            useGuestStore.getState().triggerAuth({
                                type: 'save_conversation',
                                message: 'Sign in to save your conversations',
                            })
                        }
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition"
                    >
                        Sign In
                    </button>
                ) : (
                    <div className="flex items-center gap-3">
                        <span className="text-sm text-gray-400">{session?.user?.email}</span>
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-700 rounded-full flex items-center justify-center text-white text-sm font-medium">
                            {session?.user?.name?.[0] || 'U'}
                        </div>
                    </div>
                )}
            </header>

            {/* Main Content */}
            <div className="flex-1 overflow-hidden flex flex-col">
                {!hasMessages ? (
                    /* Welcome Panel */
                    <WelcomePanel onPromptClick={handlePromptClick} />
                ) : (
                    /* Messages */
                    <div className="flex-1 overflow-y-auto px-4 py-6">
                        <div className="max-w-3xl mx-auto space-y-6">
                            {messages.map((message) => (
                                <MessageBubble
                                    key={message.id}
                                    message={message}
                                    onRegenerate={
                                        message.role === 'assistant' && !message.isStreaming
                                            ? () => handleRegenerate(message.id)
                                            : undefined
                                    }
                                />
                            ))}
                            <div ref={messagesEndRef} />
                        </div>
                    </div>
                )}

                {/* Guest limit warning */}
                {isGuest && guestSession && guestSession.messagesRemaining <= 5 && guestSession.messagesRemaining > 0 && (
                    <div className="mx-4 mb-2">
                        <div className="max-w-3xl mx-auto">
                            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg px-4 py-2 text-sm text-yellow-400 flex items-center justify-between">
                                <span>
                                    {guestSession.messagesRemaining} messages remaining. Sign in for unlimited access.
                                </span>
                                <button
                                    onClick={() =>
                                        useGuestStore.getState().triggerAuth({
                                            type: 'low_messages',
                                            message: 'Sign in for unlimited messages',
                                        })
                                    }
                                    className="text-yellow-300 hover:text-yellow-200 font-medium"
                                >
                                    Sign in →
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Input Area */}
                <div className="px-4 py-4 border-t border-gray-800/50">
                    <div className="max-w-3xl mx-auto">
                        <ChatComposer
                            onSend={handleSend}
                            isLoading={isLoading}
                            disabled={isGuest && guestSession?.messagesRemaining === 0}
                        />
                        <p className="text-xs text-gray-500 text-center mt-3">
                            WaqediAI can make mistakes. Verify important information with original sources.
                        </p>
                    </div>
                </div>
            </div>

            {/* Auth Modal */}
            <AuthModal />
        </div>
    );
}
