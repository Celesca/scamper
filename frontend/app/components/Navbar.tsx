"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
    const pathname = usePathname();

    const links = [
        { href: "/", label: "Home" },
        { href: "/scanner", label: "Scanner" },
        { href: "/watchtower", label: "Watchtower" },
        { href: "/extension", label: "Extension" },
    ];

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 border-b border-slate-800/50 bg-slate-950/80 backdrop-blur-xl">
            <div className="max-w-7xl mx-auto px-6">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-3 group">
                        <div className="relative">
                            <img
                                src="/scamper_icon.jpg"
                                alt="Scamper"
                                className="w-10 h-10 rounded-xl shadow-lg shadow-cyan-500/30 group-hover:shadow-cyan-500/50 transition-shadow object-cover"
                            />
                            <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                        </div>
                        <div>
                            <span className="text-lg font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                                Scamper
                            </span>
                            <p className="text-[10px] text-slate-500 -mt-1">AI-Powered Protection</p>
                        </div>
                    </Link>

                    {/* Navigation Links */}
                    <div className="hidden md:flex items-center gap-1">
                        {links.map((link) => {
                            const isActive = pathname === link.href;
                            return (
                                <Link
                                    key={link.href}
                                    href={link.href}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${isActive
                                        ? "bg-cyan-500/20 text-cyan-400 shadow-lg shadow-cyan-500/10"
                                        : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                                        }`}
                                >
                                    {link.label}
                                </Link>
                            );
                        })}
                    </div>

                    {/* CTA Button */}
                    <Link
                        href="/scanner"
                        className="hidden md:flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-semibold shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 hover:scale-105 transition-all duration-300"
                    >
                        <span>🔍</span>
                        Scan Now
                    </Link>

                    {/* Mobile Menu Button */}
                    <button className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/50">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                </div>
            </div>
        </nav>
    );
}
