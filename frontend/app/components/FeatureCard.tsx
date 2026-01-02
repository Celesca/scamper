interface FeatureCardProps {
    icon: string;
    title: string;
    description: string;
    color: "cyan" | "purple" | "amber" | "green" | "red";
    features?: string[];
}

const colorClasses = {
    cyan: {
        bg: "from-cyan-500/20 to-blue-500/20",
        border: "border-cyan-500/30",
        icon: "from-cyan-500 to-blue-600",
        shadow: "shadow-cyan-500/20",
        text: "text-cyan-400",
    },
    purple: {
        bg: "from-purple-500/20 to-pink-500/20",
        border: "border-purple-500/30",
        icon: "from-purple-500 to-pink-600",
        shadow: "shadow-purple-500/20",
        text: "text-purple-400",
    },
    amber: {
        bg: "from-amber-500/20 to-orange-500/20",
        border: "border-amber-500/30",
        icon: "from-amber-500 to-orange-600",
        shadow: "shadow-amber-500/20",
        text: "text-amber-400",
    },
    green: {
        bg: "from-green-500/20 to-emerald-500/20",
        border: "border-green-500/30",
        icon: "from-green-500 to-emerald-600",
        shadow: "shadow-green-500/20",
        text: "text-green-400",
    },
    red: {
        bg: "from-red-500/20 to-rose-500/20",
        border: "border-red-500/30",
        icon: "from-red-500 to-rose-600",
        shadow: "shadow-red-500/20",
        text: "text-red-400",
    },
};

export default function FeatureCard({ icon, title, description, color, features }: FeatureCardProps) {
    const classes = colorClasses[color];

    return (
        <div className={`relative group rounded-2xl border ${classes.border} bg-gradient-to-br ${classes.bg} backdrop-blur-sm p-6 hover:scale-[1.02] transition-all duration-300 overflow-hidden`}>
            {/* Glow effect on hover */}
            <div className={`absolute inset-0 bg-gradient-to-br ${classes.bg} opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-xl`} />

            <div className="relative z-10">
                {/* Icon */}
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${classes.icon} flex items-center justify-center text-2xl shadow-lg ${classes.shadow} mb-4`}>
                    {icon}
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold text-white mb-2">{title}</h3>

                {/* Description */}
                <p className="text-slate-400 text-sm mb-4">{description}</p>

                {/* Feature list */}
                {features && (
                    <ul className="space-y-2">
                        {features.map((feature, i) => (
                            <li key={i} className="flex items-center gap-2 text-sm">
                                <span className={classes.text}>✓</span>
                                <span className="text-slate-300">{feature}</span>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}
