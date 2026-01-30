/**
 * Next.js Middleware for Authentication and RBAC
 * 
 * Enforces:
 * - JWT presence on protected routes
 * - Role-based access control
 * - Tenant context propagation
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Public routes that don't require authentication (guest-accessible)
const PUBLIC_ROUTES = ['/', '/login', '/signup', '/logout', '/forgot-password', '/reset-password'];

// API routes handled separately
const API_ROUTES = ['/api'];

// Route-role requirements
const ROUTE_ROLES: Record<string, string[]> = {
    '/tenants': ['super_admin'],
    '/users': ['super_admin', 'tenant_admin'],
    '/audit': ['super_admin', 'tenant_admin', 'analyst'],
    '/settings': ['super_admin', 'tenant_admin'],
    '/documents': ['super_admin', 'tenant_admin', 'analyst', 'viewer'],
    '/knowledge': ['super_admin', 'tenant_admin', 'analyst', 'viewer', 'user'],
    '/dashboard': ['super_admin', 'tenant_admin', 'analyst', 'viewer', 'user'],
};

/**
 * Decode JWT payload (no verification - backend handles that)
 */
function decodeJWTPayload(token: string): {
    sub: string;
    tenant_id: string;
    roles: string[];
    exp: number;
} | null {
    try {
        const parts = token.split('.');
        if (parts.length !== 3) return null;
        const decoded = Buffer.from(parts[1], 'base64').toString('utf-8');
        return JSON.parse(decoded);
    } catch {
        return null;
    }
}

/**
 * Check if token is expired
 */
function isExpired(payload: { exp: number }): boolean {
    const now = Math.floor(Date.now() / 1000);
    return payload.exp <= now;
}

/**
 * Check if user has required role for route
 */
function hasRequiredRole(userRoles: string[], routePath: string): boolean {
    // Find matching route
    const route = Object.keys(ROUTE_ROLES).find((r) => routePath.startsWith(r));
    if (!route) return true; // No restriction

    const requiredRoles = ROUTE_ROLES[route];

    // Super admin has access to everything
    if (userRoles.includes('super_admin')) return true;

    return requiredRoles.some((role) => userRoles.includes(role));
}

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Skip API routes
    if (API_ROUTES.some((route) => pathname.startsWith(route))) {
        return NextResponse.next();
    }

    // Allow public routes
    if (PUBLIC_ROUTES.some((route) => pathname.startsWith(route))) {
        return NextResponse.next();
    }

    // Get access token from cookie
    const accessToken = request.cookies.get('access_token')?.value;

    // No token - redirect to login
    if (!accessToken) {
        const loginUrl = new URL('/login', request.url);
        loginUrl.searchParams.set('redirect', pathname);
        return NextResponse.redirect(loginUrl);
    }

    // Decode and validate token
    const payload = decodeJWTPayload(accessToken);
    if (!payload) {
        const loginUrl = new URL('/login', request.url);
        loginUrl.searchParams.set('error', 'invalid_token');
        return NextResponse.redirect(loginUrl);
    }

    // Check expiration
    if (isExpired(payload)) {
        const loginUrl = new URL('/login', request.url);
        loginUrl.searchParams.set('error', 'session_expired');
        return NextResponse.redirect(loginUrl);
    }

    // Check role-based access
    if (!hasRequiredRole(payload.roles, pathname)) {
        return NextResponse.redirect(new URL('/dashboard?error=unauthorized', request.url));
    }

    // Add tenant context to response headers
    const response = NextResponse.next();
    response.headers.set('X-Tenant-ID', payload.tenant_id);
    response.headers.set('X-User-ID', payload.sub);

    return response;
}

export const config = {
    matcher: [
        /*
         * Match all paths except:
         * - _next/static (static files)
         * - _next/image (image optimization)
         * - favicon.ico
         * - public assets
         */
        '/((?!_next/static|_next/image|favicon.ico|public|assets).*)',
    ],
};
