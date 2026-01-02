import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Thai Brand Guardian - AI-Powered Phishing Protection",
  description: "Protect Thai brands from phishing attacks with real-time CT log monitoring, AI vision detection, and active defense systems.",
  keywords: ["phishing protection", "brand security", "Thai cybersecurity", "domain monitoring", "typosquatting detection"],
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
