/**
 * Signup Page
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { publicAuthApi } from '@/core/api-client';

export default function SignupPage() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        displayName: '',
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const handleEmailSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            await publicAuthApi.post('/auth/signup', {
                email: formData.email,
                password: formData.password,
                display_name: formData.displayName,
            });
            setSuccess(true);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Unable to create account');
        } finally {
            setIsLoading(false);
        }
    };

    const handleGoogleSignup = () => {
        // Redirect to Google OAuth
        const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
        const redirectUri = `${window.location.origin}/auth/callback/google`;
        const scope = 'email profile';

        const url = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=id_token&scope=${scope}&nonce=${Date.now()}`;
        window.location.href = url;
    };

    if (success) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-dark-950 px-4">
                <div className="w-full max-w-md text-center">
                    <div className="bg-green-500/10 border border-green-500/50 rounded-xl p-8">
                        <div className="text-4xl mb-4">✉️</div>
                        <h2 className="text-xl font-semibold text-white mb-2">Check Your Email</h2>
                        <p className="text-gray-400">
                            We've sent a verification link to <strong>{formData.email}</strong>
                        </p>
                        <p className="text-gray-500 text-sm mt-4">
                            Please verify your email to complete registration.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-dark-950 px-4">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">WaqediAI</h1>
                    <p className="text-gray-400">Enterprise Knowledge Platform</p>
                </div>

                <div className="bg-dark-900 rounded-xl p-8 shadow-xl border border-gray-800">
                    <h2 className="text-xl font-semibold text-white mb-6">Create Account</h2>

                    {error && (
                        <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mb-4">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleEmailSignup} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Full Name
                            </label>
                            <input
                                type="text"
                                name="displayName"
                                value={formData.displayName}
                                onChange={handleChange}
                                className="w-full px-4 py-3 bg-dark-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 transition"
                                placeholder="John Doe"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Work Email
                            </label>
                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                className="w-full px-4 py-3 bg-dark-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 transition"
                                placeholder="you@company.com"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Password
                            </label>
                            <input
                                type="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                className="w-full px-4 py-3 bg-dark-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 transition"
                                placeholder="••••••••"
                                minLength={8}
                                required
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                Min 8 characters, 1 uppercase, 1 number
                            </p>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 disabled:cursor-not-allowed text-white font-medium rounded-lg transition mt-2"
                        >
                            {isLoading ? 'Creating Account...' : 'Create Account'}
                        </button>
                    </form>

                    <div className="relative my-6">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-gray-700"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-2 bg-dark-900 text-gray-500">or</span>
                        </div>
                    </div>

                    <button
                        onClick={handleGoogleSignup}
                        className="w-full py-3 px-4 bg-white hover:bg-gray-100 text-gray-900 font-medium rounded-lg transition flex items-center justify-center gap-3"
                    >
                        <svg className="w-5 h-5" viewBox="0 0 24 24">
                            <path
                                fill="currentColor"
                                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            />
                            <path
                                fill="currentColor"
                                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            />
                            <path
                                fill="currentColor"
                                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                            />
                            <path
                                fill="currentColor"
                                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            />
                        </svg>
                        Continue with Google
                    </button>

                    <p className="text-xs text-gray-500 text-center mt-6">
                        By signing up, you agree to our Terms of Service and Privacy Policy.
                        Your data is processed in accordance with enterprise security standards.
                    </p>
                </div>

                <p className="text-center text-gray-400 text-sm mt-6">
                    Already have an account?{' '}
                    <Link href="/login" className="text-primary-500 hover:text-primary-400">
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    );
}
