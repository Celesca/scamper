import Link from "next/link";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import AnimatedBackground from "./components/AnimatedBackground";
import FeatureCard from "./components/FeatureCard";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <AnimatedBackground />
      <Navbar />

      <main className="relative z-10 pt-16">
        {/* Hero Section */}
        <section className="min-h-[90vh] flex items-center justify-center px-6">
          <div className="max-w-5xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-sm font-medium mb-8 animate-pulse">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              Real-time Protection Active
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                Protect Your Brand From
              </span>
              <br />
              <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                Phishing Attacks
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
              AI-powered domain monitoring, computer vision detection, and active defense
              system designed specifically for Thai banks and enterprises.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <Link
                href="/scanner"
                className="group flex items-center gap-3 px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-lg shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 hover:scale-105 transition-all duration-300"
              >
                <span>🔍</span>
                Scan Your Domain
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              <Link
                href="/watchtower"
                className="flex items-center gap-3 px-8 py-4 rounded-full border border-slate-600 text-slate-300 font-semibold text-lg hover:border-slate-400 hover:text-white hover:bg-slate-800/50 transition-all duration-300"
              >
                <span>🗼</span>
                Live Dashboard
              </Link>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-3xl mx-auto">
              {[
                { value: "100K+", label: "Certificates Scanned" },
                { value: "50+", label: "Thai Brands Protected" },
                { value: "< 1min", label: "Detection Time" },
                { value: "24/7", label: "Monitoring" },
              ].map((stat, i) => (
                <div key={i} className="text-center">
                  <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                    {stat.value}
                  </div>
                  <div className="text-sm text-slate-500">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-24 px-6" id="features">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">
                <span className="bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                  Complete Protection Suite
                </span>
              </h2>
              <p className="text-slate-400 max-w-2xl mx-auto">
                Enterprise-grade security features to detect and defend against sophisticated phishing attacks targeting Thai brands.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <FeatureCard
                icon="🗼"
                title="Watchtower"
                description="Real-time Certificate Transparency log monitoring with DNSTwist-style fuzzing."
                color="cyan"
                features={[
                  "CT log monitoring",
                  "Typosquatting detection",
                  "Homoglyph analysis",
                  "Thai brand focus"
                ]}
              />
              <FeatureCard
                icon="👁️"
                title="AI Vision"
                description="Computer vision detects unauthorized use of your brand's logos and UI patterns."
                color="purple"
                features={[
                  "Logo detection",
                  "Visual similarity scoring",
                  "Zero-day catch rate",
                  "PromptPay pattern recognition"
                ]}
              />
              <FeatureCard
                icon="🤖"
                title="Active Defense"
                description="Fight back with automated poisoning bots that pollute phishing databases."
                color="red"
                features={[
                  "Fake credential injection",
                  "Form field detection",
                  "Database pollution",
                  "Scammer disruption"
                ]}
              />
              <FeatureCard
                icon="🔍"
                title="Domain Scanner"
                description="On-demand scanning with comprehensive vulnerability analysis."
                color="amber"
                features={[
                  "Permutation generation",
                  "DNS resolution check",
                  "Risk scoring",
                  "CSV/PDF export"
                ]}
              />
              <FeatureCard
                icon="📧"
                title="Auto Takedown"
                description="Streamlined reporting with evidence packages for hosting providers."
                color="green"
                features={[
                  "Evidence screenshots",
                  "Provider templates",
                  "Status tracking",
                  "Legal compliance"
                ]}
              />
              <FeatureCard
                icon="🔌"
                title="Chrome Extension"
                description="Browser-based protection with 3-layer detection architecture."
                color="cyan"
                features={[
                  "Layer 1: Local bouncer",
                  "Layer 2: Backend detective",
                  "Layer 3: AI judge",
                  "Thai keyword detection"
                ]}
              />
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="py-24 px-6 bg-gradient-to-b from-transparent to-slate-900/50">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">
                <span className="bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                  How It Works
                </span>
              </h2>
              <p className="text-slate-400 max-w-2xl mx-auto">
                Our multi-layer defense system catches phishing sites in real-time
              </p>
            </div>

            <div className="relative">
              {/* Connection line */}
              <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-500 via-purple-500 to-red-500 -translate-y-1/2" />

              <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {[
                  {
                    step: "01",
                    icon: "📡",
                    title: "Monitor",
                    description: "Continuously monitor Certificate Transparency logs for new domains",
                    color: "cyan"
                  },
                  {
                    step: "02",
                    icon: "🔬",
                    title: "Analyze",
                    description: "DNSTwist fuzzing detects typosquatting and lookalike domains",
                    color: "blue"
                  },
                  {
                    step: "03",
                    icon: "👁️",
                    title: "Verify",
                    description: "AI Vision compares screenshots against legitimate brand assets",
                    color: "purple"
                  },
                  {
                    step: "04",
                    icon: "⚔️",
                    title: "Defend",
                    description: "Auto-generate takedown requests and deploy poisoning bots",
                    color: "red"
                  }
                ].map((item, i) => (
                  <div key={i} className="relative">
                    <div className="bg-slate-900/80 border border-slate-700/50 rounded-2xl p-6 text-center backdrop-blur-sm">
                      {/* Step indicator */}
                      <div className="w-12 h-12 rounded-full bg-slate-800 border-2 border-slate-600 flex items-center justify-center text-lg font-bold text-slate-400 mx-auto mb-4 relative z-10">
                        {item.step}
                      </div>
                      <div className="text-4xl mb-4">{item.icon}</div>
                      <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                      <p className="text-slate-400 text-sm">{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Thai Focus Section */}
        <section className="py-24 px-6">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-sm font-medium mb-6">
                  🇹🇭 Made for Thailand
                </div>
                <h2 className="text-4xl font-bold mb-6">
                  <span className="bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                    Built for Thai Brands
                  </span>
                </h2>
                <p className="text-slate-400 mb-8">
                  Global solutions miss Thai-specific phishing patterns. We understand local nuances,
                  LINE-based redirects, and Thai banking UI flows.
                </p>
                <ul className="space-y-4">
                  {[
                    "Thai bank monitoring: KBank, SCB, Bangkok Bank, and more",
                    "Thai keyword detection: ยืนยันตัวตน, OTP, ระงับบัญชี",
                    "PromptPay/Thai QR Payment pattern recognition",
                    "LINE-to-phishing redirect detection"
                  ].map((item, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <span className="text-cyan-400 mt-1">✓</span>
                      <span className="text-slate-300">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="relative">
                <div className="bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-slate-700/50 rounded-2xl p-8 backdrop-blur-sm">
                  <div className="grid grid-cols-3 gap-4">
                    {["🏦 KBank", "🏛️ SCB", "🏢 BBL", "💳 KTB", "🏪 Krungsri", "📱 LINE", "🛍️ Lazada", "🛒 Shopee", "💰 PromptPay"].map((brand, i) => (
                      <div key={i} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center text-sm text-slate-300 hover:border-cyan-500/50 hover:bg-cyan-500/5 transition-all cursor-default">
                        {brand}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-gradient-to-br from-cyan-500/10 via-blue-500/10 to-purple-500/10 border border-slate-700/50 rounded-3xl p-12 backdrop-blur-sm">
              <h2 className="text-4xl font-bold mb-4">
                <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                  Ready to Protect Your Brand?
                </span>
              </h2>
              <p className="text-slate-400 mb-8 max-w-xl mx-auto">
                Start scanning your domain for potential phishing threats now.
                No sign-up required for basic scans.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link
                  href="/scanner"
                  className="group flex items-center gap-3 px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-lg shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 hover:scale-105 transition-all duration-300"
                >
                  Start Free Scan
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Link>
                <Link
                  href="/extension"
                  className="flex items-center gap-3 px-8 py-4 rounded-full border border-slate-600 text-slate-300 font-semibold text-lg hover:border-slate-400 hover:text-white hover:bg-slate-800/50 transition-all duration-300"
                >
                  Get Extension
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
