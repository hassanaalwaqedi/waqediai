/**
 * NextAuth Configuration
 * 
 * Enterprise OAuth setup with Google provider.
 * Extensible for future providers (GitHub, Microsoft).
 */

import { AuthOptions } from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

if (!process.env.GOOGLE_CLIENT_ID) {
    throw new Error('Missing GOOGLE_CLIENT_ID environment variable');
}

if (!process.env.GOOGLE_CLIENT_SECRET) {
    throw new Error('Missing GOOGLE_CLIENT_SECRET environment variable');
}

if (!process.env.NEXTAUTH_SECRET) {
    throw new Error('Missing NEXTAUTH_SECRET environment variable');
}

const AUTH_API = process.env.NEXT_PUBLIC_AUTH_API || 'http://localhost:8001';

export const authOptions: AuthOptions = {
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET,
            authorization: {
                params: {
                    prompt: 'consent',
                    access_type: 'offline',
                    response_type: 'code',
                },
            },
        }),
        // Future providers can be added here:
        // GitHubProvider({ ... }),
        // AzureADProvider({ ... }),
    ],

    callbacks: {
        async signIn({ user, account, profile }) {
            if (!account || !profile) return false;

            // Only allow verified Google emails
            if (account.provider === 'google') {
                const googleProfile = profile as { email_verified?: boolean };
                if (!googleProfile.email_verified) {
                    return '/login?error=email_not_verified';
                }
            }

            try {
                // Send ID token to backend for verification and JWT issuance
                const response = await fetch(`${AUTH_API}/auth/oauth/google`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id_token: account.id_token,
                    }),
                });

                if (!response.ok) {
                    const error = await response.json();
                    console.error('Backend auth failed:', error);
                    return `/login?error=${error.detail || 'auth_failed'}`;
                }

                const data = await response.json();

                // Store backend tokens in account for session callback
                account.backendAccessToken = data.access_token;
                account.backendUserId = data.user_id;
                account.isNewUser = data.is_new_user;

                return true;
            } catch (error) {
                console.error('Auth error:', error);
                return '/login?error=server_error';
            }
        },

        async jwt({ token, account, user }) {
            // On initial sign in, add backend tokens to JWT
            if (account?.backendAccessToken) {
                token.accessToken = account.backendAccessToken;
                token.userId = account.backendUserId;
                token.isNewUser = account.isNewUser;
                token.provider = account.provider;
            }
            return token;
        },

        async session({ session, token }) {
            // Add backend tokens to session
            return {
                ...session,
                accessToken: token.accessToken as string,
                userId: token.userId as string,
                isNewUser: token.isNewUser as boolean,
                provider: token.provider as string,
            };
        },

        async redirect({ url, baseUrl }) {
            // Redirect to dashboard after login
            if (url.startsWith('/')) return `${baseUrl}${url}`;
            if (new URL(url).origin === baseUrl) return url;
            return baseUrl;
        },
    },

    pages: {
        signIn: '/login',
        error: '/login',
    },

    session: {
        strategy: 'jwt',
        maxAge: 24 * 60 * 60, // 24 hours
    },

    secret: process.env.NEXTAUTH_SECRET,

    debug: process.env.NODE_ENV === 'development',
};
