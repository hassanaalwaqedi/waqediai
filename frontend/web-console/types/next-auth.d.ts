/**
 * NextAuth Type Extensions
 */

import 'next-auth';
import { JWT } from 'next-auth/jwt';

declare module 'next-auth' {
    interface Session {
        accessToken: string;
        userId: string;
        tenantId: string;  // For tenant-scoped RAG queries
        isNewUser: boolean;
        provider: string;
    }

    interface Account {
        backendAccessToken?: string;
        backendUserId?: string;
        isNewUser?: boolean;
    }
}

declare module 'next-auth/jwt' {
    interface JWT {
        accessToken?: string;
        userId?: string;
        isNewUser?: boolean;
        provider?: string;
    }
}
