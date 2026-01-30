/**
 * Secure API Client with Token Management
 * 
 * Features:
 * - Access token in memory only
 * - Automatic refresh before expiry
 * - Retry failed requests after refresh
 * - Tenant header injection
 */

import axios, {
    AxiosInstance,
    AxiosError,
    InternalAxiosRequestConfig,
    AxiosResponse,
} from 'axios';
import { isTokenExpired, getUserFromToken, getTokenTimeRemaining } from './jwt';

const AUTH_API = process.env.NEXT_PUBLIC_AUTH_API || 'http://localhost:8001';
const RAG_API = process.env.NEXT_PUBLIC_RAG_API || 'http://localhost:8009';
const PIPELINE_API = process.env.NEXT_PUBLIC_PIPELINE_API || 'http://localhost:8008';
const INGESTION_API = process.env.NEXT_PUBLIC_INGESTION_API || 'http://localhost:8002';

// Export API endpoints for use in services
export const API_ENDPOINTS = {
    auth: AUTH_API,
    rag: RAG_API,
    pipeline: PIPELINE_API,
    ingestion: INGESTION_API,
};

/**
 * Token storage (memory only - no localStorage for security)
 */
class TokenManager {
    private accessToken: string | null = null;
    private refreshPromise: Promise<string | null> | null = null;
    private refreshTimer: NodeJS.Timeout | null = null;

    setAccessToken(token: string): void {
        this.accessToken = token;
        this.scheduleRefresh(token);
    }

    getAccessToken(): string | null {
        return this.accessToken;
    }

    clearTokens(): void {
        this.accessToken = null;
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    getTenantId(): string | null {
        if (!this.accessToken) return null;
        const user = getUserFromToken(this.accessToken);
        return user?.tenantId || null;
    }

    isAuthenticated(): boolean {
        return this.accessToken !== null && !isTokenExpired(this.accessToken);
    }

    private scheduleRefresh(token: string): void {
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
        }

        const remaining = getTokenTimeRemaining(token);
        // Refresh 60 seconds before expiry
        const refreshIn = Math.max(0, (remaining - 60) * 1000);

        this.refreshTimer = setTimeout(() => {
            this.performRefresh();
        }, refreshIn);
    }

    async performRefresh(): Promise<string | null> {
        // Prevent concurrent refresh attempts
        if (this.refreshPromise) {
            return this.refreshPromise;
        }

        this.refreshPromise = this.doRefresh();
        const result = await this.refreshPromise;
        this.refreshPromise = null;
        return result;
    }

    private async doRefresh(): Promise<string | null> {
        try {
            const response = await axios.post(
                `${AUTH_API}/auth/refresh`,
                {},
                { withCredentials: true }
            );

            const newToken = response.data.access_token;
            if (newToken) {
                this.setAccessToken(newToken);
                return newToken;
            }
        } catch (error) {
            this.clearTokens();
        }
        return null;
    }
}

export const tokenManager = new TokenManager();

/**
 * Create authenticated API client
 */
function createAuthenticatedClient(baseURL: string): AxiosInstance {
    const client = axios.create({
        baseURL,
        timeout: 30000,
        withCredentials: true,
        headers: {
            'Content-Type': 'application/json',
        },
    });

    // Request interceptor - inject tokens
    client.interceptors.request.use(
        async (config: InternalAxiosRequestConfig) => {
            let token = tokenManager.getAccessToken();

            // Check if token needs refresh
            if (token && isTokenExpired(token, 60)) {
                token = await tokenManager.performRefresh();
            }

            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }

            const tenantId = tokenManager.getTenantId();
            if (tenantId) {
                config.headers['X-Tenant-ID'] = tenantId;
            }

            return config;
        },
        (error) => Promise.reject(error)
    );

    // Response interceptor - handle 401 and retry
    client.interceptors.response.use(
        (response: AxiosResponse) => response,
        async (error: AxiosError) => {
            const originalRequest = error.config as InternalAxiosRequestConfig & {
                _retry?: boolean;
            };

            if (error.response?.status === 401 && !originalRequest._retry) {
                originalRequest._retry = true;

                const newToken = await tokenManager.performRefresh();
                if (newToken) {
                    originalRequest.headers.Authorization = `Bearer ${newToken}`;
                    return client(originalRequest);
                }

                // Refresh failed - redirect to login
                if (typeof window !== 'undefined') {
                    window.location.href = '/login?session_expired=true';
                }
            }

            return Promise.reject(error);
        }
    );

    return client;
}

// Export configured clients
export const authApi = createAuthenticatedClient(AUTH_API);
export const ragApi = createAuthenticatedClient(RAG_API);
export const pipelineApi = createAuthenticatedClient(PIPELINE_API);

// Public client for login (no auth required)
export const publicAuthApi = axios.create({
    baseURL: AUTH_API,
    timeout: 30000,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});
