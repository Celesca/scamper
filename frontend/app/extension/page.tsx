"use client";

import Link from "next/link";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import AnimatedBackground from "../components/AnimatedBackground";
import FeatureCard from "../components/FeatureCard";

export default function ExtensionPage() {
    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <AnimatedBackground />
            <Navbar />

            <main className="relative z-10 pt-24 pb-16 px-6">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-16">
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-sm font-medium mb-8">
                            🔌 Browser Extension
                        </div>
                        <h1 className="text-4xl md:text-5xl font-bold mb-4">
                            <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                                Phishing Hunter Extension
                            </span>
                        </h1>
                        <p className="text-slate-400 max-w-2xl mx-auto">
                            Real-time protection while you browse. Our Chrome extension uses a 3-layer
                            defense system to detect and block phishing sites instantly.
                        </p>
                    </div>

                    {/* Extension Preview */}
                    <div className="max-w-4xl mx-auto mb-16">
                        <div className="relative">
                            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-3xl blur-2xl opacity-20" />
                            <div className="relative bg-slate-900/80 border border-slate-700/50 rounded-3xl p-8 md:p-12 backdrop-blur-sm">
                                <div className="grid md:grid-cols-2 gap-8 items-center">
                                    {/* Extension Mockup */}
                                    <div className="relative">
                                        <div className="bg-slate-800 rounded-xl shadow-2xl overflow-hidden border border-slate-700">
                                            {/* Chrome Extension Header */}
                                            <div className="bg-slate-900 px-4 py-3 flex items-center gap-3 border-b border-slate-700">
                                                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-sm font-bold">
                                                    🛡️
                                                </div>
                                                <span className="font-semibold text-white">Phishing Hunter</span>
                                            </div>
                                            {/* Extension Content */}
                                            <div className="p-6 text-center">
                                                <div className="text-5xl mb-4">✅</div>
                                                <div className="text-xl font-bold text-green-400 mb-2">Site is Safe</div>
                                                <div className="text-sm text-slate-400 mb-4">Threat Score: 0/100</div>
                                                <div className="space-y-2 text-left">
                                                    <div className="flex items-center gap-2 text-sm text-slate-300">
                                                        <span className="text-green-400">✓</span>
                                                        <span>Known trusted domain</span>
                                                    </div>
                                                    <div className="flex items-center gap-2 text-sm text-slate-300">
                                                        <span className="text-green-400">✓</span>
                                                        <span>Valid SSL certificate</span>
                                                    </div>
                                                    <div className="flex items-center gap-2 text-sm text-slate-300">
                                                        <span className="text-green-400">✓</span>
                                                        <span>No phishing keywords detected</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Danger State Preview */}
                                        <div className="absolute -bottom-8 -right-8 w-48 bg-slate-800 rounded-xl shadow-2xl overflow-hidden border border-red-500/50 transform rotate-6">
                                            <div className="bg-red-500/20 px-3 py-2 flex items-center gap-2 border-b border-red-500/30">
                                                <div className="w-6 h-6 rounded bg-red-500/30 flex items-center justify-center text-xs">
                                                    🛡️
                                                </div>
                                                <span className="text-xs font-semibold text-red-400">Warning</span>
                                            </div>
                                            <div className="p-4 text-center">
                                                <div className="text-2xl mb-1">⚠️</div>
                                                <div className="text-xs font-bold text-red-400">Phishing Detected</div>
                                                <div className="text-[10px] text-slate-500">Score: 85/100</div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Install CTA */}
                                    <div>
                                        <h2 className="text-2xl font-bold mb-4 text-white">
                                            Protect Yourself Now
                                        </h2>
                                        <p className="text-slate-400 mb-6">
                                            Install our free browser extension to get real-time protection
                                            against phishing attacks targeting Thai users.
                                        </p>
                                        <div className="space-y-4">
                                            <button className="w-full flex items-center justify-center gap-3 px-6 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 hover:scale-105 transition-all duration-300">
                                                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                                                    <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm-.044 4.158l6.612.001.083.001c.162.014.32.04.466.091a1.33 1.33 0 01.724.609l.045.095.002.005.007.015a1.27 1.27 0 01.027 1.095l-.044.097-4.204 8.32-.019.037a1.388 1.388 0 01-.5.499 1.302 1.302 0 01-.638.169H8.43l-.095-.002a1.27 1.27 0 01-.764-.322 1.26 1.26 0 01-.38-.666l-.016-.098-.016-.098-.887-5.54a1.283 1.283 0 01.126-.767l.057-.107 3.8-6.062.056-.082c.12-.159.268-.29.442-.393a1.305 1.305 0 01.596-.168l.106-.001z" />
                                                </svg>
                                                Add to Chrome - Free
                                            </button>
                                            <div className="flex items-center justify-center gap-4 text-sm text-slate-500">
                                                <span className="flex items-center gap-1">
                                                    <span className="text-amber-400">★★★★★</span>
                                                    <span>5.0 rating</span>
                                                </span>
                                                <span>•</span>
                                                <span>10K+ users</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* 3-Layer Architecture */}
                    <section className="mb-20">
                        <div className="text-center mb-12">
                            <h2 className="text-3xl font-bold mb-4">
                                <span className="bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                                    3-Layer Defense Architecture
                                </span>
                            </h2>
                            <p className="text-slate-400 max-w-xl mx-auto">
                                Our intelligent detection system balances speed and accuracy with a cascading
                                approach that gets smarter at each layer.
                            </p>
                        </div>

                        <div className="relative">
                            {/* Connection lines */}
                            <div className="hidden lg:block absolute top-1/2 left-[16%] right-[16%] h-0.5 bg-gradient-to-r from-green-500 via-amber-500 to-red-500 -translate-y-1/2" />

                            <div className="grid lg:grid-cols-3 gap-8">
                                {/* Layer 1 */}
                                <div className="relative bg-slate-900/80 border border-green-500/30 rounded-2xl p-8 backdrop-blur-sm">
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-green-500/20 border border-green-500/50 text-green-400 text-sm font-bold">
                                        Layer 1
                                    </div>
                                    <div className="text-center mt-4">
                                        <div className="text-5xl mb-4">🚪</div>
                                        <h3 className="text-xl font-bold text-white mb-2">The Bouncer</h3>
                                        <p className="text-slate-400 text-sm mb-6">
                                            Lightning-fast local checks that run entirely in your browser.
                                        </p>
                                        <ul className="text-left space-y-3">
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-green-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">Whitelist verification</span>
                                            </li>
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-green-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">Thai keyword detection</span>
                                            </li>
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-green-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">Login form analysis</span>
                                            </li>
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-green-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">Suspicious TLD check</span>
                                            </li>
                                        </ul>
                                        <div className="mt-6 text-xs text-green-400 font-medium">
                                            ⚡ &lt;10ms response time
                                        </div>
                                    </div>
                                </div>

                                {/* Layer 2 */}
                                <div className="relative bg-slate-900/80 border border-amber-500/30 rounded-2xl p-8 backdrop-blur-sm">
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-amber-500/20 border border-amber-500/50 text-amber-400 text-sm font-bold">
                                        Layer 2
                                    </div>
                                    <div className="text-center mt-4">
                                        <div className="text-5xl mb-4">🔍</div>
                                        <h3 className="text-xl font-bold text-white mb-2">The Detective</h3>
                                        <p className="text-slate-400 text-sm mb-6">
                                            Cloud-based API analysis for suspicious domains.
                                        </p>
                                        <ul className="text-left space-y-3">
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-amber-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">DNSTwist typosquatting</span>
                                            </li>
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-amber-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">Homoglyph detection</span>
                                            </li>
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-amber-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">URL entropy analysis</span>
                                            </li>
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-amber-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">Brand impersonation check</span>
                                            </li>
                                        </ul>
                                        <div className="mt-6 text-xs text-amber-400 font-medium">
                                            ⚡ 100-500ms response time
                                        </div>
                                    </div>
                                </div>

                                {/* Layer 3 */}
                                <div className="relative bg-slate-900/80 border border-red-500/30 rounded-2xl p-8 backdrop-blur-sm">
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-red-500/20 border border-red-500/50 text-red-400 text-sm font-bold">
                                        Layer 3
                                    </div>
                                    <div className="text-center mt-4">
                                        <div className="text-5xl mb-4">⚖️</div>
                                        <h3 className="text-xl font-bold text-white mb-2">The Judge</h3>
                                        <p className="text-slate-400 text-sm mb-6">
                                            AI-powered intent analysis for edge cases.
                                        </p>
                                        <ul className="text-left space-y-3">
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-red-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">LLM intent analysis</span>
                                            </li>
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-red-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">Computer vision verification</span>
                                            </li>
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-red-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">Visual similarity scoring</span>
                                            </li>
                                            <li className="flex items-start gap-2 text-sm">
                                                <span className="text-red-400 mt-0.5">✓</span>
                                                <span className="text-slate-300">Human review escalation</span>
                                            </li>
                                        </ul>
                                        <div className="mt-6 text-xs text-red-400 font-medium">
                                            ⚡ 1-3s for complex analysis
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* Thai Detection Features */}
                    <section className="mb-20">
                        <div className="text-center mb-12">
                            <h2 className="text-3xl font-bold mb-4">
                                <span className="bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                                    Thai-Specific Detection
                                </span>
                            </h2>
                            <p className="text-slate-400 max-w-xl mx-auto">
                                Built specifically to catch phishing attacks targeting Thai users with local context.
                            </p>
                        </div>

                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                            <FeatureCard
                                icon="🇹🇭"
                                title="Thai Keywords"
                                description="Detects common Thai phishing phrases like ยืนยันตัวตน, OTP, and ระงับบัญชี"
                                color="amber"
                            />
                            <FeatureCard
                                icon="🏦"
                                title="Bank Recognition"
                                description="Identifies attempts to impersonate Thai banks like KBank, SCB, and Bangkok Bank"
                                color="cyan"
                            />
                            <FeatureCard
                                icon="💳"
                                title="PromptPay Detection"
                                description="Catches fake Thai QR Payment interfaces and PromptPay scams"
                                color="green"
                            />
                        </div>
                    </section>

                    {/* Installation Steps */}
                    <section>
                        <div className="text-center mb-12">
                            <h2 className="text-3xl font-bold mb-4">
                                <span className="bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                                    Easy Installation
                                </span>
                            </h2>
                        </div>

                        <div className="max-w-3xl mx-auto">
                            <div className="space-y-6">
                                {[
                                    {
                                        step: "1",
                                        title: "Download the Extension",
                                        description: "Click 'Add to Chrome' button above or visit the Chrome Web Store"
                                    },
                                    {
                                        step: "2",
                                        title: "Confirm Installation",
                                        description: "Click 'Add extension' when prompted by Chrome"
                                    },
                                    {
                                        step: "3",
                                        title: "Start Browsing Safely",
                                        description: "The extension will automatically protect you on every page"
                                    }
                                ].map((item, i) => (
                                    <div key={i} className="flex items-start gap-6 bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-xl font-bold flex-shrink-0">
                                            {item.step}
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-bold text-white mb-1">{item.title}</h3>
                                            <p className="text-slate-400">{item.description}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>
                </div>
            </main>

            <Footer />
        </div>
    );
}
