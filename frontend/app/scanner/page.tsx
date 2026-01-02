"use client";

import { useState, useCallback } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import AnimatedBackground from "../components/AnimatedBackground";

// Types
interface ScanResult {
    domain: string;
    fuzzer: string;
    dns_a: string[];
    dns_mx: string[];
    is_registered: boolean;
    risk_score: number;
    risk_factors: string[];
}

interface DOMAnalysis {
    has_login_form: boolean;
    has_password_field: boolean;
    form_count: number;
    form_actions: string[];
    input_fields: { type: string; name: string; placeholder: string }[];
    suspicious_elements: string[];
    thai_keywords_found: string[];
    meta_title: string;
}

interface LayerResult {
    score: number;
    factors: string[];
}

interface Layer3Result extends LayerResult {
    verdict: string;
    confidence: number;
    reasoning: string;
    recommendation: string;
}

interface DeepAnalysis {
    domain: string;
    target_domain: string;
    analysis_time: string;
    layer1: LayerResult & { fuzzer_type: string; is_registered: boolean; dns_a: string[] };
    layer2: LayerResult & {
        screenshot_b64?: string;
        favicon_url?: string;
        dom_analysis?: DOMAnalysis;
        page_accessible: boolean;
    };
    layer3: Layer3Result;
    final_score: number;
    recommendation: string;
}

interface ScanResponse {
    target: string;
    total_permutations: number;
    registered_count: number;
    high_risk_count: number;
    basic_results?: ScanResult[];
    results?: ScanResult[];
    deep_analysis?: DeepAnalysis[];
    scan_time: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// Risk level badge
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

// Recommendation badge
function RecommendationBadge({ recommendation }: { recommendation: string }) {
    const colors: Record<string, string> = {
        takedown: "bg-red-500/20 text-red-400 border-red-500/50",
        investigate: "bg-orange-500/20 text-orange-400 border-orange-500/50",
        monitor: "bg-yellow-500/20 text-yellow-400 border-yellow-500/50",
        safe: "bg-green-500/20 text-green-400 border-green-500/50",
    };

    const icons: Record<string, string> = {
        takedown: "⚠️",
        investigate: "🔍",
        monitor: "👁️",
        safe: "✅",
    };

    return (
        <span className={`px-3 py-1 rounded-full text-sm font-bold border flex items-center gap-1.5 ${colors[recommendation] || colors.monitor}`}>
            {icons[recommendation] || "📋"} {recommendation.charAt(0).toUpperCase() + recommendation.slice(1)}
        </span>
    );
}

// Layer progress indicator
function LayerProgress({ current, layers }: { current: number; layers: string[] }) {
    return (
        <div className="flex items-center gap-2 mb-6">
            {layers.map((layer, i) => (
                <div key={layer} className="flex items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${i < current
                        ? "bg-green-500 text-white"
                        : i === current
                            ? "bg-cyan-500 text-white animate-pulse"
                            : "bg-slate-700 text-slate-400"
                        }`}>
                        {i < current ? "✓" : i + 1}
                    </div>
                    {i < layers.length - 1 && (
                        <div className={`w-12 h-0.5 mx-1 ${i < current ? "bg-green-500" : "bg-slate-700"}`} />
                    )}
                </div>
            ))}
        </div>
    );
}

// Result card component
function ResultCard({
    result,
    onAnalyze,
    isAnalyzing,
    deepAnalysis,
}: {
    result: ScanResult;
    onAnalyze: () => void;
    isAnalyzing: boolean;
    deepAnalysis?: DeepAnalysis;
}) {
    const [expanded, setExpanded] = useState(false);

    const riskLevel = result.risk_score >= 70 ? "critical" : result.risk_score >= 50 ? "high" : result.risk_score >= 30 ? "medium" : "low";
    const borderColor = {
        critical: "border-red-500/50 hover:border-red-500",
        high: "border-orange-500/50 hover:border-orange-500",
        medium: "border-yellow-500/50 hover:border-yellow-500",
        low: "border-slate-600/50 hover:border-slate-500",
    };

    return (
        <div className={`bg-slate-900/80 border-2 rounded-xl overflow-hidden transition-all duration-300 ${borderColor[riskLevel]} ${expanded ? "ring-2 ring-cyan-500/30" : ""}`}>
            {/* Header - Always visible */}
            <div
                className="p-4 cursor-pointer flex items-center justify-between"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="flex items-center gap-4 flex-1">
                    {/* Status indicator */}
                    <div className={`w-3 h-3 rounded-full ${result.is_registered ? "bg-amber-400 animate-pulse" : "bg-slate-500"}`} />

                    {/* Domain */}
                    <div className="flex-1">
                        <span className="font-mono text-sm text-cyan-400">{result.domain}</span>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="px-2 py-0.5 rounded bg-slate-700/50 text-xs text-slate-300">
                                {result.fuzzer}
                            </span>
                            {result.is_registered && (
                                <span className="text-xs text-amber-400">● Registered</span>
                            )}
                        </div>
                    </div>

                    {/* Risk score */}
                    <RiskBadge score={result.risk_score} />

                    {/* Deep analysis status */}
                    {deepAnalysis && (
                        <RecommendationBadge recommendation={deepAnalysis.recommendation} />
                    )}
                </div>

                {/* Expand icon */}
                <svg
                    className={`w-5 h-5 text-slate-400 transition-transform ${expanded ? "rotate-180" : ""}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </div>

            {/* Expanded content */}
            {expanded && (
                <div className="border-t border-slate-700/50 p-4 space-y-4">
                    {/* Risk factors */}
                    {result.risk_factors.length > 0 && (
                        <div>
                            <h4 className="text-sm font-medium text-slate-400 mb-2">Risk Factors</h4>
                            <div className="flex flex-wrap gap-2">
                                {result.risk_factors.map((factor, i) => (
                                    <span key={i} className="px-2 py-1 bg-slate-800 rounded text-xs text-slate-300">
                                        {factor}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* DNS Info */}
                    {result.dns_a.length > 0 && (
                        <div>
                            <h4 className="text-sm font-medium text-slate-400 mb-2">DNS Records</h4>
                            <div className="font-mono text-xs text-slate-300">
                                A: {result.dns_a.join(", ")}
                            </div>
                        </div>
                    )}

                    {/* Deep Analysis Results */}
                    {deepAnalysis && (
                        <div className="space-y-4 pt-4 border-t border-slate-700/50">
                            <h4 className="text-sm font-medium text-cyan-400 flex items-center gap-2">
                                <span>🔬</span> Deep Analysis Results
                            </h4>

                            {/* 3-Layer Summary */}
                            <div className="grid grid-cols-3 gap-4">
                                {/* Layer 1 */}
                                <div className="bg-slate-800/50 rounded-lg p-3">
                                    <div className="text-xs text-slate-400 mb-1">Layer 1: Bouncer</div>
                                    <div className="text-2xl font-bold text-cyan-400">{deepAnalysis.layer1.score}</div>
                                    <div className="text-xs text-slate-500 mt-1">{deepAnalysis.layer1.factors.length} factors</div>
                                </div>

                                {/* Layer 2 */}
                                <div className="bg-slate-800/50 rounded-lg p-3">
                                    <div className="text-xs text-slate-400 mb-1">Layer 2: Detective</div>
                                    <div className="text-2xl font-bold text-purple-400">{deepAnalysis.layer2.score}</div>
                                    <div className="text-xs text-slate-500 mt-1">
                                        {deepAnalysis.layer2.page_accessible ? "Page analyzed" : "Not accessible"}
                                    </div>
                                </div>

                                {/* Layer 3 */}
                                <div className="bg-slate-800/50 rounded-lg p-3">
                                    <div className="text-xs text-slate-400 mb-1">Layer 3: Judge</div>
                                    <div className="text-2xl font-bold text-amber-400">{deepAnalysis.layer3.score}</div>
                                    <div className="text-xs text-slate-500 mt-1">
                                        {Math.round(deepAnalysis.layer3.confidence * 100)}% confidence
                                    </div>
                                </div>
                            </div>

                            {/* Verdict */}
                            <div className="bg-slate-800/30 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm font-medium text-white">Verdict: {deepAnalysis.layer3.verdict}</span>
                                    <span className="text-3xl font-bold text-cyan-400">{deepAnalysis.final_score}/100</span>
                                </div>
                                <p className="text-sm text-slate-400">{deepAnalysis.layer3.reasoning}</p>
                            </div>

                            {/* DOM Analysis */}
                            {deepAnalysis.layer2.dom_analysis && (
                                <div className="bg-slate-800/30 rounded-lg p-4">
                                    <h5 className="text-sm font-medium text-white mb-3">DOM Analysis</h5>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                        <div className="text-center">
                                            <div className={`text-2xl ${deepAnalysis.layer2.dom_analysis.has_login_form ? "text-red-400" : "text-green-400"}`}>
                                                {deepAnalysis.layer2.dom_analysis.has_login_form ? "⚠️" : "✓"}
                                            </div>
                                            <div className="text-xs text-slate-400 mt-1">Login Form</div>
                                        </div>
                                        <div className="text-center">
                                            <div className={`text-2xl ${deepAnalysis.layer2.dom_analysis.has_password_field ? "text-red-400" : "text-green-400"}`}>
                                                {deepAnalysis.layer2.dom_analysis.has_password_field ? "⚠️" : "✓"}
                                            </div>
                                            <div className="text-xs text-slate-400 mt-1">Password Field</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl text-slate-300">{deepAnalysis.layer2.dom_analysis.form_count}</div>
                                            <div className="text-xs text-slate-400 mt-1">Forms</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl text-slate-300">{deepAnalysis.layer2.dom_analysis.thai_keywords_found?.length || 0}</div>
                                            <div className="text-xs text-slate-400 mt-1">Thai Keywords</div>
                                        </div>
                                    </div>

                                    {/* Thai keywords found */}
                                    {deepAnalysis.layer2.dom_analysis.thai_keywords_found?.length > 0 && (
                                        <div className="mt-3 pt-3 border-t border-slate-700/50">
                                            <div className="text-xs text-slate-400 mb-2">Thai Phishing Keywords Detected:</div>
                                            <div className="flex flex-wrap gap-1">
                                                {deepAnalysis.layer2.dom_analysis.thai_keywords_found.map((kw, i) => (
                                                    <span key={i} className="px-2 py-0.5 bg-red-500/20 text-red-400 rounded text-xs">
                                                        {kw}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Input fields */}
                                    {deepAnalysis.layer2.dom_analysis.input_fields?.length > 0 && (
                                        <div className="mt-3 pt-3 border-t border-slate-700/50">
                                            <div className="text-xs text-slate-400 mb-2">Form Inputs Detected:</div>
                                            <div className="space-y-1">
                                                {deepAnalysis.layer2.dom_analysis.input_fields.slice(0, 5).map((field, i) => (
                                                    <div key={i} className="flex items-center gap-2 text-xs">
                                                        <span className={`px-1.5 py-0.5 rounded ${field.type === 'password' ? 'bg-red-500/20 text-red-400' : 'bg-slate-700 text-slate-300'}`}>
                                                            {field.type}
                                                        </span>
                                                        <span className="text-slate-400">{field.name || field.placeholder || '(unnamed)'}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Screenshot */}
                            {deepAnalysis.layer2.screenshot_b64 && (
                                <div className="bg-slate-800/30 rounded-lg p-4">
                                    <h5 className="text-sm font-medium text-white mb-3">Page Screenshot</h5>
                                    <img
                                        src={`data:image/png;base64,${deepAnalysis.layer2.screenshot_b64}`}
                                        alt="Page screenshot"
                                        className="w-full rounded-lg border border-slate-700"
                                    />
                                </div>
                            )}
                        </div>
                    )}

                    {/* Action buttons */}
                    <div className="flex gap-2 pt-4">
                        {result.is_registered && !deepAnalysis && (
                            <button
                                onClick={(e) => { e.stopPropagation(); onAnalyze(); }}
                                disabled={isAnalyzing}
                                className="px-4 py-2 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 hover:bg-cyan-500/30 transition-all text-sm font-medium disabled:opacity-50 flex items-center gap-2"
                            >
                                {isAnalyzing ? (
                                    <>
                                        <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                        </svg>
                                        Analyzing...
                                    </>
                                ) : (
                                    <>🔬 Deep Analyze</>
                                )}
                            </button>
                        )}

                        {deepAnalysis && deepAnalysis.recommendation === 'takedown' && (
                            <button
                                onClick={(e) => { e.stopPropagation(); window.open(`/takedown?domain=${result.domain}`, '_blank'); }}
                                className="px-4 py-2 rounded-lg bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30 transition-all text-sm font-medium flex items-center gap-2"
                            >
                                ⚠️ Request Takedown
                            </button>
                        )}

                        <a
                            href={`https://${result.domain}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="px-4 py-2 rounded-lg border border-slate-600 text-slate-300 hover:border-slate-400 hover:text-white transition-all text-sm flex items-center gap-2"
                        >
                            🔗 Visit
                        </a>
                    </div>
                </div>
            )}
        </div>
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
    const [deepAnalyses, setDeepAnalyses] = useState<Record<string, DeepAnalysis>>({});
    const [analyzingDomains, setAnalyzingDomains] = useState<Set<string>>(new Set());
    const [useDeepScan, setUseDeepScan] = useState(true);

    const startScan = useCallback(async () => {
        if (!domain.trim()) {
            setError("Please enter a domain to scan");
            return;
        }

        setIsScanning(true);
        setError("");
        setResults(null);
        setDeepAnalyses({});
        setScanProgress(0);

        const progressInterval = setInterval(() => {
            setScanProgress((prev) => {
                if (prev >= 90) return prev;
                return Math.min(prev + Math.random() * 15, 90);
            });
        }, 500);

        const stages = useDeepScan
            ? ["Generating permutations...", "Checking DNS records...", "Running deep analysis...", "Analyzing DOM structure...", "Compiling results..."]
            : ["Generating permutations...", "Checking DNS records...", "Analyzing risk factors...", "Compiling results..."];

        let stageIndex = 0;
        const stageInterval = setInterval(() => {
            setScanStatus(stages[stageIndex]);
            stageIndex = (stageIndex + 1) % stages.length;
        }, 1500);

        try {
            const endpoint = useDeepScan ? "/api/scanner/deep-scan" : "/api/scanner/scan";
            const res = await fetch(`${API_BASE}${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    domain: domain.trim(),
                    include_screenshots: true,
                    include_dom: true,
                    analyze_registered_only: true
                }),
            });

            if (!res.ok) {
                throw new Error("Scan failed. Please try again.");
            }

            const data = await res.json();

            // Normalize results
            if (data.basic_results && !data.results) {
                data.results = data.basic_results;
            }

            setResults(data);
            setScanProgress(100);

            // Store deep analysis results
            if (data.deep_analysis) {
                const analyses: Record<string, DeepAnalysis> = {};
                data.deep_analysis.forEach((a: DeepAnalysis) => {
                    analyses[a.domain] = a;
                });
                setDeepAnalyses(analyses);
            }
        } catch (err) {
            setError("Scan failed. Make sure the backend is running.");
            console.error(err);
        } finally {
            clearInterval(progressInterval);
            clearInterval(stageInterval);
            setIsScanning(false);
            setScanStatus("");
        }
    }, [domain, useDeepScan]);

    const analyzeSingleDomain = async (targetDomain: string) => {
        setAnalyzingDomains((prev) => new Set(prev).add(targetDomain));

        try {
            const res = await fetch(`${API_BASE}/api/scanner/analyze-single`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    domain: targetDomain,
                    target_domain: domain,
                    include_screenshot: true,
                    include_dom: true
                }),
            });

            if (res.ok) {
                const analysis = await res.json();
                setDeepAnalyses((prev) => ({
                    ...prev,
                    [targetDomain]: analysis
                }));
            }
        } catch (err) {
            console.error("Deep analysis failed:", err);
        } finally {
            setAnalyzingDomains((prev) => {
                const next = new Set(prev);
                next.delete(targetDomain);
                return next;
            });
        }
    };

    const filteredResults = results?.results?.filter((r) => {
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
                            Advanced 3-layer analysis with DOM inspection, screenshot capture, and Thai phishing detection.
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
                                            placeholder="kbank.com"
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
                                            <span className="flex items-center gap-2">🔍 Scan</span>
                                        )}
                                    </button>
                                </div>

                                {/* Deep scan toggle */}
                                <div className="mt-4 flex items-center gap-3">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={useDeepScan}
                                            onChange={(e) => setUseDeepScan(e.target.checked)}
                                            className="w-4 h-4 rounded border-slate-600 bg-slate-700 text-cyan-500 focus:ring-cyan-500"
                                        />
                                        <span className="text-sm text-slate-400">
                                            Deep Scan (3-layer analysis with DOM & screenshots)
                                        </span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    {isScanning && (
                        <div className="max-w-2xl mx-auto mb-12">
                            <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                <LayerProgress
                                    current={scanProgress < 30 ? 0 : scanProgress < 60 ? 1 : scanProgress < 90 ? 2 : 3}
                                    layers={["Bouncer", "Detective", "Judge"]}
                                />
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
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                    <p className="text-sm text-slate-400 mb-1">Permutations</p>
                                    <p className="text-3xl font-bold text-cyan-400">{results.total_permutations?.toLocaleString()}</p>
                                </div>
                                <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                    <p className="text-sm text-slate-400 mb-1">Registered</p>
                                    <p className="text-3xl font-bold text-amber-400">{results.registered_count}</p>
                                </div>
                                <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                    <p className="text-sm text-slate-400 mb-1">High Risk</p>
                                    <p className="text-3xl font-bold text-red-400">{results.high_risk_count}</p>
                                </div>
                                <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                    <p className="text-sm text-slate-400 mb-1">Deep Analyzed</p>
                                    <p className="text-3xl font-bold text-purple-400">{Object.keys(deepAnalyses).length}</p>
                                </div>
                                <div className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                                    <p className="text-sm text-slate-400 mb-1">Scan Time</p>
                                    <p className="text-3xl font-bold text-green-400">{results.scan_time?.toFixed(1)}s</p>
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

                            {/* Results Cards */}
                            <div className="space-y-3">
                                {filteredResults.map((result, i) => (
                                    <ResultCard
                                        key={`${result.domain}-${i}`}
                                        result={result}
                                        onAnalyze={() => analyzeSingleDomain(result.domain)}
                                        isAnalyzing={analyzingDomains.has(result.domain)}
                                        deepAnalysis={deepAnalyses[result.domain]}
                                    />
                                ))}
                            </div>

                            {filteredResults.length === 0 && (
                                <div className="text-center py-12 text-slate-500 bg-slate-900/50 rounded-xl">
                                    No results match the current filter
                                </div>
                            )}

                            {/* Export Button */}
                            <div className="flex justify-end gap-2">
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
                            <p className="text-slate-500 max-w-md mx-auto">
                                Enter a domain to check for typosquatting, homoglyphs, and phishing domains.
                                Our 3-layer system will analyze each threat.
                            </p>
                        </div>
                    )}
                </div>
            </main>

            <Footer />
        </div>
    );
}
