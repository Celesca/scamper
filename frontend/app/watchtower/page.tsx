"use client";

import { useEffect, useState, useRef, useCallback } from "react";

// Types
interface Detection {
    domain: string;
    target: string;
    fuzzer_type: string;
    risk_score: number;
    risk_factors: string[];
    detection_time: string;
    certificate_issuer: string;
}

interface Stats {
    runtime_seconds: number;
    certs_processed: number;
    domains_checked: number;
    detections_count: number;
    high_risk_count: number;
    processing_rate: number;
    by_target: Record<string, number>;
    by_fuzzer: Record<string, number>;
}

interface Status {
    is_running: boolean;
    stats: Stats;
    targets_count: number;
    permutations_count: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// Risk badge component
function RiskBadge({ score }: { score: number }) {
    const level =
        score >= 70 ? "critical" : score >= 50 ? "high" : score >= 30 ? "medium" : "low";
    const colors = {
        critical: "bg-red-500/20 text-red-400 border-red-500/50 shadow-red-500/20",
        high: "bg-orange-500/20 text-orange-400 border-orange-500/50 shadow-orange-500/20",
        medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/50 shadow-yellow-500/20",
        low: "bg-green-500/20 text-green-400 border-green-500/50 shadow-green-500/20",
    };

    return (
        <span
            className={`px-3 py-1 rounded-full text-xs font-bold border shadow-lg ${colors[level]}`}
        >
            {score}/100
        </span>
    );
}

// Stats card component
function StatsCard({
    title,
    value,
    subtitle,
    icon,
    color,
}: {
    title: string;
    value: string | number;
    subtitle?: string;
    icon: string;
    color: string;
}) {
    return (
        <div
            className={`relative overflow-hidden rounded-xl border border-slate-700/50 bg-slate-800/50 p-6 backdrop-blur-sm`}
        >
            <div className={`absolute -right-4 -top-4 text-6xl opacity-10 ${color}`}>
                {icon}
            </div>
            <div className="relative">
                <p className="text-sm font-medium text-slate-400">{title}</p>
                <p className={`mt-2 text-3xl font-bold ${color}`}>
                    {typeof value === "number" ? value.toLocaleString() : value}
                </p>
                {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
            </div>
        </div>
    );
}

// Live feed item
function FeedItem({ detection, isNew }: { detection: Detection; isNew: boolean }) {
    const time = new Date(detection.detection_time).toLocaleTimeString();
    const severity = detection.risk_score >= 70 ? "critical" : "normal";

    return (
        <div
            className={`border-l-4 pl-4 py-3 transition-all duration-500 ${isNew ? "animate-pulse bg-cyan-500/10" : ""
                } ${severity === "critical"
                    ? "border-red-500 bg-red-500/5"
                    : "border-cyan-500 bg-slate-800/30"
                }`}
        >
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-500 font-mono">{time}</span>
                    <RiskBadge score={detection.risk_score} />
                </div>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300">
                    {detection.fuzzer_type}
                </span>
            </div>
            <p className="mt-2 font-mono text-sm text-cyan-400 break-all">
                {detection.domain}
            </p>
            <p className="mt-1 text-xs text-slate-500">
                Targeting: <span className="text-amber-400 font-semibold">{detection.target}</span>
            </p>
        </div>
    );
}

// Connection status indicator
function ConnectionStatus({ connected, running }: { connected: boolean; running: boolean }) {
    return (
        <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
                <div
                    className={`w-2 h-2 rounded-full ${connected ? "bg-green-500 animate-pulse" : "bg-red-500"
                        }`}
                />
                <span className="text-xs text-slate-400">
                    {connected ? "Connected" : "Disconnected"}
                </span>
            </div>
            <div className="flex items-center gap-2">
                <div
                    className={`w-2 h-2 rounded-full ${running ? "bg-cyan-500 animate-pulse" : "bg-slate-500"
                        }`}
                />
                <span className="text-xs text-slate-400">
                    {running ? "Monitoring" : "Stopped"}
                </span>
            </div>
        </div>
    );
}

export default function WatchtowerPage() {
    const [status, setStatus] = useState<Status | null>(null);
    const [detections, setDetections] = useState<Detection[]>([]);
    const [connected, setConnected] = useState(false);
    const [newDetectionIds, setNewDetectionIds] = useState<Set<string>>(new Set());
    const [filter, setFilter] = useState<string>("all");
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Fetch initial data
    const fetchData = useCallback(async () => {
        try {
            const [statusRes, detectionsRes] = await Promise.all([
                fetch(`${API_BASE}/api/watchtower/status`),
                fetch(`${API_BASE}/api/watchtower/detections?limit=50`),
            ]);

            if (statusRes.ok) {
                setStatus(await statusRes.json());
            }
            if (detectionsRes.ok) {
                const data = await detectionsRes.json();
                setDetections(data.detections || []);
            }
        } catch (error) {
            console.error("Failed to fetch data:", error);
        }
    }, []);

    // Connect to WebSocket using Socket.IO protocol
    const connectWebSocket = useCallback(() => {
        // For Socket.IO, we'll use polling fallback via REST API
        // Full WebSocket would require socket.io-client
        const pollInterval = setInterval(async () => {
            if (!connected) return;
            try {
                const res = await fetch(`${API_BASE}/api/watchtower/status`);
                if (res.ok) {
                    const data = await res.json();
                    setStatus(data);
                }
            } catch {
                // Ignore polling errors
            }
        }, 2000);

        setConnected(true);
        return () => clearInterval(pollInterval);
    }, [connected]);

    // Start/stop monitoring
    const toggleMonitoring = async () => {
        const endpoint = status?.is_running ? "stop" : "start";
        try {
            const res = await fetch(`${API_BASE}/api/watchtower/${endpoint}`, {
                method: "POST",
            });
            if (res.ok) {
                await fetchData();
            }
        } catch (error) {
            console.error("Failed to toggle monitoring:", error);
        }
    };

    // Initial load and polling
    useEffect(() => {
        fetchData();
        setConnected(true);

        // Poll for updates
        const pollInterval = setInterval(() => {
            fetchData();
        }, 3000);

        return () => {
            clearInterval(pollInterval);
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [fetchData]);

    // Filter detections
    const filteredDetections = detections.filter((d) => {
        if (filter === "all") return true;
        if (filter === "critical") return d.risk_score >= 70;
        if (filter === "high") return d.risk_score >= 50 && d.risk_score < 70;
        return true;
    });

    // Format runtime
    const formatRuntime = (seconds: number) => {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s
            .toString()
            .padStart(2, "0")}`;
    };

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            {/* Animated background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -inset-[10px] opacity-20">
                    <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500 rounded-full blur-[128px] animate-pulse" />
                    <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500 rounded-full blur-[128px] animate-pulse delay-1000" />
                </div>
            </div>

            <div className="relative z-10">
                {/* Header */}
                <header className="border-b border-slate-800/50 bg-slate-900/80 backdrop-blur-xl sticky top-0 z-50">
                    <div className="max-w-7xl mx-auto px-6 py-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="relative">
                                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-2xl shadow-lg shadow-cyan-500/30">
                                        🗼
                                    </div>
                                    {status?.is_running && (
                                        <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-ping" />
                                    )}
                                </div>
                                <div>
                                    <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                                        WATCHTOWER
                                    </h1>
                                    <p className="text-sm text-slate-400">
                                        Real-time Certificate Transparency Monitor
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center gap-6">
                                <ConnectionStatus connected={connected} running={status?.is_running || false} />

                                <button
                                    onClick={toggleMonitoring}
                                    className={`px-6 py-2 rounded-lg font-semibold transition-all duration-300 ${status?.is_running
                                            ? "bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30"
                                            : "bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 hover:bg-cyan-500/30"
                                        }`}
                                >
                                    {status?.is_running ? "⏹ Stop" : "▶ Start"} Monitoring
                                </button>
                            </div>
                        </div>
                    </div>
                </header>

                <main className="max-w-7xl mx-auto px-6 py-8">
                    {/* Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                        <StatsCard
                            title="Certificates Scanned"
                            value={status?.stats.certs_processed || 0}
                            subtitle={`${(status?.stats.processing_rate || 0).toFixed(1)}/sec`}
                            icon="📜"
                            color="text-cyan-400"
                        />
                        <StatsCard
                            title="Domains Checked"
                            value={status?.stats.domains_checked || 0}
                            subtitle={`Runtime: ${formatRuntime(status?.stats.runtime_seconds || 0)}`}
                            icon="🔍"
                            color="text-blue-400"
                        />
                        <StatsCard
                            title="Detections"
                            value={status?.stats.detections_count || 0}
                            subtitle={`${status?.permutations_count?.toLocaleString() || 0} patterns loaded`}
                            icon="🎯"
                            color="text-amber-400"
                        />
                        <StatsCard
                            title="High Risk"
                            value={status?.stats.high_risk_count || 0}
                            subtitle="Score ≥ 70"
                            icon="⚠️"
                            color="text-red-400"
                        />
                    </div>

                    {/* Main Content Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Live Feed */}
                        <div className="lg:col-span-2 bg-slate-900/50 rounded-xl border border-slate-800/50 overflow-hidden">
                            <div className="px-6 py-4 border-b border-slate-800/50 flex items-center justify-between">
                                <h2 className="font-semibold text-lg flex items-center gap-2">
                                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                    Live Detection Feed
                                </h2>
                                <div className="flex gap-2">
                                    {["all", "critical", "high"].map((f) => (
                                        <button
                                            key={f}
                                            onClick={() => setFilter(f)}
                                            className={`px-3 py-1 rounded text-xs font-medium transition-all ${filter === f
                                                    ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/50"
                                                    : "text-slate-400 hover:text-white"
                                                }`}
                                        >
                                            {f.charAt(0).toUpperCase() + f.slice(1)}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="h-[500px] overflow-y-auto custom-scrollbar">
                                {filteredDetections.length === 0 ? (
                                    <div className="flex flex-col items-center justify-center h-full text-slate-500">
                                        <span className="text-4xl mb-4">🔭</span>
                                        <p>No detections yet</p>
                                        <p className="text-sm mt-2">
                                            {status?.is_running
                                                ? "Monitoring CT logs for suspicious domains..."
                                                : "Start monitoring to detect phishing domains"}
                                        </p>
                                    </div>
                                ) : (
                                    <div className="divide-y divide-slate-800/30">
                                        {filteredDetections.map((d, i) => (
                                            <FeedItem
                                                key={`${d.domain}-${d.detection_time}`}
                                                detection={d}
                                                isNew={newDetectionIds.has(d.domain)}
                                            />
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Sidebar Stats */}
                        <div className="space-y-6">
                            {/* Targets by Brand */}
                            <div className="bg-slate-900/50 rounded-xl border border-slate-800/50 p-6">
                                <h3 className="font-semibold mb-4 flex items-center gap-2">
                                    <span className="text-amber-400">🏦</span> Targeted Brands
                                </h3>
                                <div className="space-y-3">
                                    {Object.entries(status?.stats.by_target || {})
                                        .sort(([, a], [, b]) => b - a)
                                        .slice(0, 8)
                                        .map(([target, count]) => (
                                            <div key={target} className="flex items-center justify-between">
                                                <span className="text-sm text-slate-300">{target}</span>
                                                <div className="flex items-center gap-2">
                                                    <div
                                                        className="h-2 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full"
                                                        style={{
                                                            width: `${Math.min(
                                                                100,
                                                                (count /
                                                                    Math.max(
                                                                        ...Object.values(status?.stats.by_target || { a: 1 })
                                                                    )) *
                                                                80
                                                            )}px`,
                                                        }}
                                                    />
                                                    <span className="text-xs text-slate-500 w-8 text-right">
                                                        {count}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    {Object.keys(status?.stats.by_target || {}).length === 0 && (
                                        <p className="text-sm text-slate-500">No targets detected yet</p>
                                    )}
                                </div>
                            </div>

                            {/* Attack Types */}
                            <div className="bg-slate-900/50 rounded-xl border border-slate-800/50 p-6">
                                <h3 className="font-semibold mb-4 flex items-center gap-2">
                                    <span className="text-purple-400">🔧</span> Attack Types
                                </h3>
                                <div className="space-y-3">
                                    {Object.entries(status?.stats.by_fuzzer || {})
                                        .sort(([, a], [, b]) => b - a)
                                        .map(([fuzzer, count]) => (
                                            <div key={fuzzer} className="flex items-center justify-between">
                                                <span className="text-sm text-slate-300 font-mono">{fuzzer}</span>
                                                <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-400">
                                                    {count}
                                                </span>
                                            </div>
                                        ))}
                                    {Object.keys(status?.stats.by_fuzzer || {}).length === 0 && (
                                        <p className="text-sm text-slate-500">No attacks detected yet</p>
                                    )}
                                </div>
                            </div>

                            {/* System Info */}
                            <div className="bg-slate-900/50 rounded-xl border border-slate-800/50 p-6">
                                <h3 className="font-semibold mb-4 flex items-center gap-2">
                                    <span className="text-cyan-400">⚙️</span> System Info
                                </h3>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Targets Monitored</span>
                                        <span className="text-white font-mono">
                                            {status?.targets_count || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Patterns Loaded</span>
                                        <span className="text-white font-mono">
                                            {(status?.permutations_count || 0).toLocaleString()}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Status</span>
                                        <span
                                            className={`font-semibold ${status?.is_running ? "text-green-400" : "text-slate-500"
                                                }`}
                                        >
                                            {status?.is_running ? "ACTIVE" : "IDLE"}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>

            {/* Custom scrollbar styles */}
            <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgb(15 23 42 / 0.5);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgb(71 85 105 / 0.5);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgb(71 85 105 / 0.8);
        }
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
      `}</style>
        </div>
    );
}
