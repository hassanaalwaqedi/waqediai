/**
 * Guest Session Manager
 * 
 * Manages anonymous guest sessions with progressive auth.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type AuthState = 'guest' | 'authenticated' | 'loading';

export interface GuestSession {
    guestId: string | null;
    messagesRemaining: number;
    sessionValid: boolean;
    createdAt: string | null;
}

export interface AuthTrigger {
    type: string;
    message: string;
    action?: () => void;
}

interface GuestStore {
    // State
    authState: AuthState;
    guestSession: GuestSession | null;
    pendingAuthTrigger: AuthTrigger | null;
    showAuthModal: boolean;

    // Actions
    initGuestSession: () => Promise<void>;
    setAuthState: (state: AuthState) => void;
    decrementMessages: () => void;
    triggerAuth: (trigger: AuthTrigger) => void;
    dismissAuthModal: () => void;
    upgradeToUser: (userId: string) => Promise<void>;
    clearGuestSession: () => void;
}

const AUTH_API = process.env.NEXT_PUBLIC_AUTH_API || 'http://localhost:8001';

export const useGuestStore = create<GuestStore>()(
    persist(
        (set, get) => ({
            authState: 'loading',
            guestSession: null,
            pendingAuthTrigger: null,
            showAuthModal: false,

            initGuestSession: async () => {
                try {
                    const response = await fetch(`${AUTH_API}/guest/session`, {
                        method: 'POST',
                        credentials: 'include',
                    });

                    if (response.ok) {
                        const data = await response.json();
                        set({
                            authState: 'guest',
                            guestSession: {
                                guestId: data.guest_id,
                                messagesRemaining: data.messages_remaining,
                                sessionValid: data.session_valid,
                                createdAt: new Date().toISOString(),
                            },
                        });
                    } else {
                        // Create local guest session
                        set({
                            authState: 'guest',
                            guestSession: {
                                guestId: `local_${Date.now()}`,
                                messagesRemaining: 20,
                                sessionValid: true,
                                createdAt: new Date().toISOString(),
                            },
                        });
                    }
                } catch (error) {
                    console.warn('Failed to create guest session:', error);
                    // Fallback to local session
                    set({
                        authState: 'guest',
                        guestSession: {
                            guestId: `local_${Date.now()}`,
                            messagesRemaining: 20,
                            sessionValid: true,
                            createdAt: new Date().toISOString(),
                        },
                    });
                }
            },

            setAuthState: (state) => set({ authState: state }),

            decrementMessages: () => {
                const { guestSession } = get();
                if (guestSession) {
                    const remaining = Math.max(0, guestSession.messagesRemaining - 1);
                    set({
                        guestSession: {
                            ...guestSession,
                            messagesRemaining: remaining,
                        },
                    });

                    // Trigger auth if running low
                    if (remaining <= 3 && remaining > 0) {
                        get().triggerAuth({
                            type: 'low_messages',
                            message: `${remaining} messages remaining. Sign in to continue.`,
                        });
                    } else if (remaining === 0) {
                        get().triggerAuth({
                            type: 'message_limit',
                            message: 'Sign in to continue chatting',
                        });
                    }
                }
            },

            triggerAuth: (trigger) => {
                set({
                    pendingAuthTrigger: trigger,
                    showAuthModal: true,
                });
            },

            dismissAuthModal: () => {
                set({
                    showAuthModal: false,
                    pendingAuthTrigger: null,
                });
            },

            upgradeToUser: async (userId: string) => {
                const { guestSession } = get();

                if (guestSession?.guestId) {
                    try {
                        // Migrate guest data to user
                        await fetch(`${AUTH_API}/guest/upgrade`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            credentials: 'include',
                            body: JSON.stringify({
                                guest_id: guestSession.guestId,
                                user_id: userId,
                            }),
                        });
                    } catch (error) {
                        console.warn('Failed to migrate guest session:', error);
                    }
                }

                set({
                    authState: 'authenticated',
                    guestSession: null,
                    showAuthModal: false,
                    pendingAuthTrigger: null,
                });
            },

            clearGuestSession: () => {
                set({
                    authState: 'guest',
                    guestSession: null,
                });
            },
        }),
        {
            name: 'waqedi-guest',
            partialize: (state) => ({
                guestSession: state.guestSession,
            }),
        }
    )
);

// Auth trigger messages
export const AUTH_TRIGGER_MESSAGES: Record<string, string> = {
    save_conversation: 'Sign in to save this conversation',
    upload_document: 'Sign in to upload documents',
    access_knowledge: "Sign in to access your organization's knowledge",
    create_workspace: 'Sign in to create a workspace',
    message_limit: 'Sign in to continue chatting',
    low_messages: 'Sign in to get unlimited messages',
};
