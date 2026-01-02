import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Scamper - AI-Powered Phishing Protection",
  description: "Protect your brand from phishing attacks with real-time CT log monitoring, AI vision detection, and active defense systems.",
  keywords: ["phishing protection", "brand security", "Thai cybersecurity", "domain monitoring", "typosquatting detection", "scamper"],
  icons: {
    icon: "/scamper_icon.jpg",
    apple: "/scamper_icon.jpg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-slate-950 text-white`}>
        {children}
      </body>
    </html>
  );
}
