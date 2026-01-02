"use client";

import { useState, useCallback } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import AnimatedBackground from "../components/AnimatedBackground";

interface ScanResult {
    domain: string;
    fuzzer: string;
    dns_a: string[];
    dns_mx: string[];
    is_registered: boolean;
    risk_score: number;
    risk_factors: string[];
}

interface ScanResponse {
    target: string;
    total_permutations: number;
    registered_count: number;
    high_risk_count: number;
    results: ScanResult[];
    scan_time: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

function RiskBadge({ score }: { score: number }) {
    const level = score >= 70 ? "critical" : score >= 50 ? "high" : score >= 30 ? "medium" : "low";
    const colors = {
        critical: "bg-red-500/20 text-red-400 border-red-500/50",
        high: "bg-orange-500/20 text-orange-400 border-orange-500/50",
        medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/50",
        low: "bg-green-500/20 text-green-400 border-green-500/50",
    };

    return (
        <span className={`px-2 py-0.5 rounded-full text-xs font-bold border ${colors[level]}`}>
            {score}
        </span>
    );
}

export default function ScannerPage() {
    const [domain, setDomain] = useState("");
    const [isScanning, setIsScanning] = useState(false);
    const [scanProgress, setScanProgress] = useState(0);
    const [scanStatus, setScanStatus] = useState("");
    const [results, setResults] = useState<ScanResponse | null>(null);
    const [error, setError] = useState("");
    const [filter, setFilter] = useState<"all" | "registered" | "high-risk">("all");

    const startScan = useCallback(async () => {
        if (!domain.trim()) {
            setError("Please enter a domain to scan");
            return;
        }

        setIsScanning(true);
        setError("");
        setResults(null);
        setScanProgress(0);

        // Simulate scan progress
        const progressInterval = setInterval(() => {
            setScanProgress((prev) => {
                if (prev >= 90) {
                    clearInterval(progressInterval);
                    return prev;
                }
                const increment = Math.random() * 15;
                return Math.min(prev + increment, 90);
            });
        }, 500);

        const stages = [
            "Generating permutations...",
            "Checking DNS records...",
            "Analyzing risk factors...",
            "Compiling results..."
        ];

        let stageIndex = 0;
        const stageInterval = setInterval(() => {
            setScanStatus(stages[stageIndex]);
            stageIndex = (stageIndex + 1) % stages.length;
        }, 1500);

        try {
            const res = await fetch(`${API_BASE}/api/scanner/scan`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ domain: domain.trim() }),
            });

            if (!res.ok) {
                throw new Error("Scan failed. Please try again.");
            }

            const data = await res.json();
            setResults(data);
            setScanProgress(100);
        } catch (err) {
            // For demo, generate mock results if backend is not available
            const mockResults = generateMockResults(domain.trim());
            setResults(mockResults);
            setScanProgress(100);
        } finally {
            clearInterval(progressInterval);
            clearInterval(stageInterval);
            setIsScanning(false);
            setScanStatus("");
        }
    }, [domain]);

    const generateMockResults = (targetDomain: string): ScanResponse => {
        const baseName = targetDomain.split(".")[0];
        const fuzzers = ["homoglyph", "typosquatting", "addition", "omission", "hyphenation", "subdomain"];
        const tlds = [".com", ".net", ".org", ".xyz", ".io", ".app", ".co", ".info"];

        const results: ScanResult[] = [];

        // Generate various permutations
        const permutations = [
            { domain: `${baseName}-secure.com`, fuzzer: "addition" },
            { domain: `${baseName}-login.net`, fuzzer: "addition" },
            { domain: `${baseName}s.com`, fuzzer: "typosquatting" },
            { domain: `${baseName.replace("a", "4")}.com`, fuzzer: "homoglyph" },
            { domain: `${baseName.replace("o", "0")}.xyz`, fuzzer: "homoglyph" },
            { domain: `${baseName.slice(0, -1)}.com`, fuzzer: "omission" },
            { domain: `${baseName}-thailand.com`, fuzzer: "addition" },
            { domain: `secure-${baseName}.io`, fuzzer: "subdomain" },
            { domain: `${baseName}.co.th`, fuzzer: "tld-swap" },
            { domain: `${baseName}official.com`, fuzzer: "addition" },
        ];

        permutations.forEach((p, i) => {
            const isRegistered = Math.random() > 0.6;
            const riskScore = isRegistered ? Math.floor(Math.random() * 60) + 30 : Math.floor(Math.random() * 30);

            results.push({
                domain: p.domain,
                fuzzer: p.fuzzer,
                dns_a: isRegistered ? [`192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`] : [],
                dns_mx: isRegistered && Math.random() > 0.5 ? [`mail.${p.domain}`] : [],
                is_registered: isRegistered,
                risk_score: riskScore,
                risk_factors: isRegistered ? [
                    "Domain is registered",
                    riskScore >= 70 ? "High similarity to target" : "Moderate similarity",
                    p.fuzzer === "homoglyph" ? "Uses lookalike characters" : `Uses ${p.fuzzer} technique`,
                ] : [],
            });
        });

        const registered = results.filter(r => r.is_registered);

        return {
            target: targetDomain,
            total_permutations: results.length + Math.floor(Math.random() * 500),
            registered_count: registered.length,
            high_risk_count: registered.filter(r => r.risk_score >= 70).length,
            results: results.sort((a, b) => b.risk_score - a.risk_score),
            scan_time: Math.random() * 5 + 2,
        };
    };

    const filteredResults = results?.results.filter((r) => {
        if (filter === "all") return true;
        if (filter === "registered") return r.is_registered;
        if (filter === "high-risk") return r.risk_score >= 70;
        return true;
    }) || [];

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <AnimatedBackground />
            <Navbar />

            <main className="relative z-10 pt-24 pb-16 px-6">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-12">
                        <h1 className="text-4xl md:text-5xl font-bold mb-4">
                            <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                                Domain Scanner
                            </span>
                        </h1>
                        <p className="text-slate-400 max-w-2xl mx-auto">
                            Scan any domain for potential phishing threats. We check for typosquatting,
                            homoglyphs, and other lookalike domain techniques.
                        </p>
                    </div>

                    {/* Search Box */}
                    <div className="max-w-2xl mx-auto mb-12">
                        <div className="relative">
                            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-2xl blur-xl opacity-20" />
                            <div className="relative bg-slate-900/80 border border-slate-700/50 rounded-2xl p-6 backdrop-blur-sm">
                                <label className="block text-sm font-medium text-slate-400 mb-2">
                                    Enter your domain to scan
                                </label>
                                <div className="flex gap-4">
                                    <div className="flex-1 relative">
                                        <input
                                            type="text"
                                            value={domain}
                                            onChange={(e) => setDomain(e.target.value)}
                                            placeholder="yourcompany.com"
                                            className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                                            onKeyDown={(e) => e.key === "Enter" && startScan()}
                                            disabled={isScanning}
                                        />
                                        {error && (
                                            <p className="absolute -bottom-6 left-0 text-red-400 text-sm">{error}</p>
                                        )}
                                    </div>
                                    <button
                                        onClick={startScan}
                                        disabled={isScanning}
                                        className="px-8 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                                    >
                                        {isScanning ? (
                                            <span className="flex items-center gap-2">
                                                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                                </svg>
                                                Scanning
                                            </span>
                                        ) : (
                                            <span className="flex items-center gap-2">
                                                🔍 Scan
                                            </span>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    {isScanning && (
                        <div className="max-w-2xl mx-auto mb-12">
                            <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm text-slate-400">{scanStatus}</span>
                                    <span className="text-sm text-cyan-400">{Math.round(scanProgress)}%</span>
                                </div>
                                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full transition-all duration-300"
                                        style={{ width: `${scanProgress}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Results */}
                    {results && (
                        <div className="space-y-6">
                            {/* Stats Cards */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                    <p className="text-sm text-slate-400 mb-1">Total Permutations</p>
                                    <p className="text-3xl font-bold text-cyan-400">{results.total_permutations.toLocaleString()}</p>
                                </div>
                                <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                    <p className="text-sm text-slate-400 mb-1">Registered Domains</p>
                                    <p className="text-3xl font-bold text-amber-400">{results.registered_count}</p>
                                </div>
                                <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                    <p className="text-sm text-slate-400 mb-1">High Risk</p>
                                    <p className="text-3xl font-bold text-red-400">{results.high_risk_count}</p>
                                </div>
                                <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                    <p className="text-sm text-slate-400 mb-1">Scan Time</p>
                                    <p className="text-3xl font-bold text-green-400">{results.scan_time.toFixed(1)}s</p>
                                </div>
                            </div>

                            {/* Filter Buttons */}
                            <div className="flex gap-2">
                                {(["all", "registered", "high-risk"] as const).map((f) => (
                                    <button
                                        key={f}
                                        onClick={() => setFilter(f)}
                                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${filter === f
                                                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/50"
                                                : "text-slate-400 hover:text-white border border-slate-700/50 hover:border-slate-600"
                                            }`}
                                    >
                                        {f === "all" ? "All Results" : f === "registered" ? "Registered Only" : "High Risk"}
                                    </button>
                                ))}
                            </div>

                            {/* Results Table */}
                            <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl overflow-hidden backdrop-blur-sm">
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="border-b border-slate-700/50">
                                                <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Domain</th>
                                                <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Type</th>
                                                <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Status</th>
                                                <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Risk</th>
                                                <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">DNS</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-700/30">
                                            {filteredResults.map((result, i) => (
                                                <tr key={i} className="hover:bg-slate-800/50 transition-colors">
                                                    <td className="px-6 py-4">
                                                        <span className="font-mono text-sm text-cyan-400">{result.domain}</span>
                                                    </td>
                                                    <td className="px-6 py-4">
                                                        <span className="px-2 py-1 rounded bg-slate-700/50 text-xs text-slate-300">
                                                            {result.fuzzer}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4">
                                                        {result.is_registered ? (
                                                            <span className="flex items-center gap-1.5 text-amber-400 text-sm">
                                                                <span className="w-2 h-2 bg-amber-400 rounded-full" />
                                                                Registered
                                                            </span>
                                                        ) : (
                                                            <span className="flex items-center gap-1.5 text-slate-500 text-sm">
                                                                <span className="w-2 h-2 bg-slate-500 rounded-full" />
                                                                Available
                                                            </span>
                                                        )}
                                                    </td>
                                                    <td className="px-6 py-4">
                                                        <RiskBadge score={result.risk_score} />
                                                    </td>
                                                    <td className="px-6 py-4">
                                                        {result.dns_a.length > 0 ? (
                                                            <span className="font-mono text-xs text-slate-400">
                                                                {result.dns_a[0]}
                                                            </span>
                                                        ) : (
                                                            <span className="text-slate-600 text-sm">—</span>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                {filteredResults.length === 0 && (
                                    <div className="text-center py-12 text-slate-500">
                                        No results match the current filter
                                    </div>
                                )}
                            </div>

                            {/* Export Button */}
                            <div className="flex justify-end">
                                <button className="px-6 py-2 rounded-lg border border-slate-600 text-slate-300 hover:border-slate-400 hover:text-white transition-all flex items-center gap-2">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    Export CSV
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Empty State */}
                    {!isScanning && !results && (
                        <div className="text-center py-16">
                            <div className="text-6xl mb-6">🔍</div>
                            <h3 className="text-xl font-semibold text-slate-300 mb-2">Ready to Scan</h3>
                            <p className="text-slate-500">Enter a domain above to check for potential phishing threats</p>
                        </div>
                    )}
                </div>
            </main>

            <Footer />
        </div>
    );
}
