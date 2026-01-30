/**
 * Authentication Service
 * 
 * Handles login, logout, refresh, and session management.
 */

import { publicAuthApi, authApi, tokenManager } from '@/core/api-client';
import { getUserFromToken } from '@/core/jwt';

export interface LoginCredentials {
    email: string;
    password: string;
    tenant_slug?: string;
}

export interface AuthTokens {
    access_token: string;
    token_type: string;
    expires_in: number;
}

export interface User {
    id: string;
    email: string;
    displayName: string;
    tenantId: string;
    roles: string[];
    permissions: string[];
}

export interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}

/**
 * Login with credentials
 */
export async function login(credentials: LoginCredentials): Promise<User> {
    const response = await publicAuthApi.post<AuthTokens>('/auth/login', credentials);
    const { access_token } = response.data;

    // Store access token in memory
    tokenManager.setAccessToken(access_token);

    // Extract user from token
    const tokenUser = getUserFromToken(access_token);
    if (!tokenUser) {
        throw new Error('Invalid token received');
    }

    return {
        id: tokenUser.userId,
        email: tokenUser.email,
        displayName: tokenUser.email.split('@')[0],
        tenantId: tokenUser.tenantId,
        roles: tokenUser.roles,
        permissions: tokenUser.permissions,
    };
}

/**
 * Logout - revoke tokens
 */
export async function logout(): Promise<void> {
    try {
        await authApi.post('/auth/logout');
    } finally {
        tokenManager.clearTokens();
    }
}

/**
 * Get current user from access token
 */
export function getCurrentUser(): User | null {
    const token = tokenManager.getAccessToken();
    if (!token) return null;

    const tokenUser = getUserFromToken(token);
    if (!tokenUser) return null;

    return {
        id: tokenUser.userId,
        email: tokenUser.email,
        displayName: tokenUser.email.split('@')[0],
        tenantId: tokenUser.tenantId,
        roles: tokenUser.roles,
        permissions: tokenUser.permissions,
    };
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
    return tokenManager.isAuthenticated();
}

/**
 * Get current tenant ID
 */
export function getTenantId(): string | null {
    return tokenManager.getTenantId();
}

/**
 * Refresh authentication session
 */
export async function refreshSession(): Promise<boolean> {
    const newToken = await tokenManager.performRefresh();
    return newToken !== null;
}
