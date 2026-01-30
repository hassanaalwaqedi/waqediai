/**
 * Authentication Hook
 * 
 * Provides reactive auth state and actions.
 */

'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import {
    login as authLogin,
    logout as authLogout,
    getCurrentUser,
    isAuthenticated,
    refreshSession,
    User,
    LoginCredentials,
} from '@/services/auth';

export interface UseAuthReturn {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    error: string | null;
    login: (credentials: LoginCredentials) => Promise<void>;
    logout: () => Promise<void>;
    refreshUser: () => void;
}

export function useAuth(): UseAuthReturn {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();
    const pathname = usePathname();

    // Initialize auth state
    useEffect(() => {
        const currentUser = getCurrentUser();
        setUser(currentUser);
        setIsLoading(false);
    }, []);

    // Login
    const login = useCallback(async (credentials: LoginCredentials) => {
        setIsLoading(true);
        setError(null);

        try {
            const loggedInUser = await authLogin(credentials);
            setUser(loggedInUser);

            // Redirect to dashboard or previous page
            const redirectUrl = new URLSearchParams(window.location.search).get('redirect');
            router.push(redirectUrl || '/dashboard');
        } catch (err: any) {
            const message = err.response?.data?.detail || 'Login failed';
            setError(message);
            throw new Error(message);
        } finally {
            setIsLoading(false);
        }
    }, [router]);

    // Logout
    const logout = useCallback(async () => {
        setIsLoading(true);
        try {
            await authLogout();
            setUser(null);
            router.push('/login');
        } finally {
            setIsLoading(false);
        }
    }, [router]);

    // Refresh user state
    const refreshUser = useCallback(() => {
        const currentUser = getCurrentUser();
        setUser(currentUser);
    }, []);

    return {
        user,
        isLoading,
        isAuthenticated: user !== null,
        error,
        login,
        logout,
        refreshUser,
    };
}
