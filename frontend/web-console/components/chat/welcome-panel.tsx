/**
 * Welcome Panel
 * 
 * Shown when chat is empty with:
 * - Logo
 * - Value proposition
 * - Example prompts
 */

'use client';

interface WelcomePanelProps {
    onPromptClick: (prompt: string) => void;
}

const EXAMPLE_PROMPTS = [
    {
        icon: '📄',
        title: 'Analyze a document',
        prompt: 'Help me understand the key points in my document',
    },
    {
        icon: '📋',
        title: 'Summarize a PDF',
        prompt: 'Can you summarize this PDF for me?',
    },
    {
        icon: '🔍',
        title: 'Search knowledge base',
        prompt: 'What do we know about our company policies?',
    },
    {
        icon: '💡',
        title: 'Get insights',
        prompt: 'What are the main takeaways from our latest reports?',
    },
];

export function WelcomePanel({ onPromptClick }: WelcomePanelProps) {
    return (
        <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
            {/* Logo & Title */}
            <div className="mb-8 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                    <span className="text-3xl">🧠</span>
                </div>
                <h1 className="text-2xl font-semibold text-white mb-2">
                    Welcome to WaqediAI
                </h1>
                <p className="text-gray-400 max-w-md">
                    Your enterprise AI knowledge assistant. Ask questions, analyze documents,
                    and get insights from your organization's knowledge.
                </p>
            </div>

            {/* Example Prompts */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full">
                {EXAMPLE_PROMPTS.map((item, index) => (
                    <button
                        key={index}
                        onClick={() => onPromptClick(item.prompt)}
                        className="flex items-start gap-3 p-4 bg-gray-800/50 hover:bg-gray-800 border border-gray-700 rounded-xl text-left transition group"
                    >
                        <span className="text-xl">{item.icon}</span>
                        <div>
                            <div className="text-white font-medium group-hover:text-blue-400 transition">
                                {item.title}
                            </div>
                            <div className="text-sm text-gray-500 line-clamp-1">
                                {item.prompt}
                            </div>
                        </div>
                    </button>
                ))}
            </div>

            {/* Capabilities */}
            <div className="mt-12 flex gap-6 text-sm text-gray-500">
                <div className="flex items-center gap-2">
                    <CheckIcon className="w-4 h-4 text-green-500" />
                    Document analysis
                </div>
                <div className="flex items-center gap-2">
                    <CheckIcon className="w-4 h-4 text-green-500" />
                    Citation-backed answers
                </div>
                <div className="flex items-center gap-2">
                    <CheckIcon className="w-4 h-4 text-green-500" />
                    Enterprise security
                </div>
            </div>
        </div>
    );
}

function CheckIcon({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
    );
}
