/**
 * JWT Utilities for WaqediAI Web Console
 * 
 * Handles JWT parsing and validation WITHOUT verifying signature
 * (signature verification happens on backend).
 */

export interface JWTPayload {
    sub: string;           // User ID
    email: string;
    tenant_id: string;
    roles: string[];
    permissions: string[];
    exp: number;           // Expiration timestamp
    iat: number;           // Issued at
    jti: string;           // JWT ID
}

/**
 * Decode JWT payload without verification
 * (Backend verifies signature, frontend just reads claims)
 */
export function decodeJWT(token: string): JWTPayload | null {
    try {
        const parts = token.split('.');
        if (parts.length !== 3) return null;

        const payload = parts[1];
        const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
        return JSON.parse(decoded) as JWTPayload;
    } catch {
        return null;
    }
}

/**
 * Check if token is expired
 */
export function isTokenExpired(token: string, bufferSeconds: number = 30): boolean {
    const payload = decodeJWT(token);
    if (!payload) return true;

    const now = Math.floor(Date.now() / 1000);
    return payload.exp <= now + bufferSeconds;
}

/**
 * Get time until token expires (in seconds)
 */
export function getTokenTimeRemaining(token: string): number {
    const payload = decodeJWT(token);
    if (!payload) return 0;

    const now = Math.floor(Date.now() / 1000);
    return Math.max(0, payload.exp - now);
}

/**
 * Extract user info from token
 */
export function getUserFromToken(token: string): {
    userId: string;
    email: string;
    tenantId: string;
    roles: string[];
    permissions: string[];
} | null {
    const payload = decodeJWT(token);
    if (!payload) return null;

    return {
        userId: payload.sub,
        email: payload.email,
        tenantId: payload.tenant_id,
        roles: payload.roles,
        permissions: payload.permissions,
    };
}
