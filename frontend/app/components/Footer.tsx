import Link from "next/link";

export default function Footer() {
    return (
        <footer className="border-t border-slate-800/50 bg-slate-950/80 backdrop-blur-xl">
            <div className="max-w-7xl mx-auto px-6 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* Brand */}
                    <div className="md:col-span-2">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600 flex items-center justify-center text-xl shadow-lg shadow-cyan-500/30">
                                🛡️
                            </div>
                            <span className="text-lg font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                                Thai Brand Guardian
                            </span>
                        </div>
                        <p className="text-slate-400 text-sm max-w-md mb-4">
                            AI-powered phishing detection and active defense system designed specifically for Thai brands.
                            Protect your business from typosquatting, lookalike domains, and sophisticated phishing attacks.
                        </p>
                        <p className="text-slate-500 text-xs">
                            Built for Samsung × KBTG Hackathon 2026
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h3 className="text-white font-semibold mb-4">Product</h3>
                        <ul className="space-y-2">
                            <li>
                                <Link href="/scanner" className="text-slate-400 hover:text-cyan-400 text-sm transition-colors">
                                    Domain Scanner
                                </Link>
                            </li>
                            <li>
                                <Link href="/watchtower" className="text-slate-400 hover:text-cyan-400 text-sm transition-colors">
                                    Watchtower
                                </Link>
                            </li>
                            <li>
                                <Link href="/extension" className="text-slate-400 hover:text-cyan-400 text-sm transition-colors">
                                    Chrome Extension
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Resources */}
                    <div>
                        <h3 className="text-white font-semibold mb-4">Resources</h3>
                        <ul className="space-y-2">
                            <li>
                                <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-cyan-400 text-sm transition-colors">
                                    GitHub
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-slate-400 hover:text-cyan-400 text-sm transition-colors">
                                    Documentation
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-slate-400 hover:text-cyan-400 text-sm transition-colors">
                                    API Reference
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-slate-800/50 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-slate-500 text-sm">
                        © 2026 Thai Brand Guardian. All rights reserved.
                    </p>
                    <div className="flex items-center gap-6">
                        <a href="#" className="text-slate-400 hover:text-white transition-colors">
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                            </svg>
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
