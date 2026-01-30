/**
 * Root layout for WaqediAI Web Console
 */

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/core/auth-provider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'WaqediAI Console',
    description: 'Enterprise AI Knowledge Management Platform',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className={`${inter.className} bg-gray-950 text-white min-h-screen`}>
                <AuthProvider>{children}</AuthProvider>
            </body>
        </html>
    );
}

