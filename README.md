# 🦊 SCAMPER: Thai Brand Guardian

**AI-Powered Phishing Detection & Active Defense System for Thai Enterprise**

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-15+-black.svg)
![React](https://img.shields.io/badge/React-19-blue.svg)

*Protecting Thai banks, e-commerce platforms, and digital citizens from online fraud with real-time CT monitoring, computer vision, and active defense.*

</div>

---

## 🚀 The SCAMPER Suite

SCAMPER is an enterprise-grade security platform designed exclusively to combat the unique phishing landscape in Thailand. From lookalike domains to fake PromptPay interfaces, SCAMPER provides a complete defense lifecycle.

### 🗼 Watchtower - Real-time CT Log Monitoring
Monitor the global Certificate Transparency logs as they are generated.
- **DNSTwist-style fuzzing**: Detects typosquatting, homoglyphs, and lookalike domains before they go live.
- **Thai brand focus**: Specialized monitoring for KBank, SCB, BBL, Lazada, Shopee, and LINE.
- **Instant alerts**: WebSocket-powered dashboard for immediate threat visibility.

### 🔍 Domain Scanner & Permutation Engine
Analyze existing infrastructures and proactively hunt for malicious variants.
- **Mass Permutation**: Generates thousands of potential phishing variants (bitsquatting, transposition, etc.).
- **DNS/WHOIS Intelligence**: Identifies which variants are registered and active.
- **Risk Scoring**: Multi-factor AI scoring for tactical threat assessment.

### 👁️ AI Vision Detection (The Judge)
Caught what blacklists miss. Our computer vision engine identifies zero-day phishing sites by their visual signature.
- **Logo Detection**: Detects unauthorized brand assets with high precision.
- **Visual Similarity**: CLIP-based analysis compares site layout against legitimate brand gold standards.
- **Thai UI Patterns**: Specialized recognition for fake PromptPay and Thai QR Payment interfaces.

---

## 🛡️ 3-Layer Detection Architecture

SCAMPER utilizes a sophisticated 3-layer approach to ensure both speed and accuracy in detecting sophisticated attacks.

### Layer 1: The Bouncer (Local Analysis)
*Fast, privacy-conscious local heuristics running directly in the browser.*
- **DOM Feature Extraction**: Analyzes link-to-content ratios and form submission targets.
- **Sensitive Field Audit**: Flags login forms or password fields sending data to external domains.
- **Thai Keyword Engine**: High-weight detection for local phishing terms like *ระงับบัญชี*, *ยืนยันตัวตน*, and *OTP*.

### Layer 2: The Detective (Backend Heuristics)
*Escalated analysis using global threat intelligence and permutation logic.*
- **TLD Reputation**: High-risk checks for `.xyz`, `.top`, `.loan`, and other suspicious extensions.
- **Fuzzing Correlation**: Matches the domain against millions of generated permutations of protected Thai brands.
- **Historical Analysis**: Checks domain age and previous SSL certificate history.

### Layer 3: The Judge (AI Computer Vision)
*The final verdict using deep learning to analyze the visual intent of a page.*
- **OCR Analysis**: Extracts text from images to catch phishing messages hidden in banners.
- **Logo Fingerprinting**: Identifies brand logos even when modified or obscured.
- **Structural Mapping**: Compares the visual structure of the page against known banking UI layouts.

---

## 🔌 SCAMPER Hunter: Chrome Extension

The **SCAMPER Hunter** extension is the frontline defense for end-users, bringing enterprise-grade protection to every tab.

### Features
- **Modern Glassmorphic UI**: A sleek, premium dashboard featuring a real-time risk meter.
- **Three-Layer Integration**: Seamlessly switches between local checks and backend escalating for high-confidence verdicts.
- **Real-time Notifications**: Instant desktop alerts if a user visits a confirmed phishing domain.
- **Risk Score Gauge**: Visual representation of the threat level with detailed breakdown of indicators.

### Installation
1.  Open Chrome and navigate to `chrome://extensions/`
2.  Enable **Developer mode** (toggle in the top right).
3.  Click **Load unpacked** and select the `extension/` folder in this repository.

---

## 🏗️ Technical Implementation

### Tech Stack
| Component | Technology |
|-----------|------------|
| **Frontend** | Next.js 15, React 19, Tailwind CSS 4, Framer Motion |
| **Backend** | Flask (Python 3.9+), Flask-SocketIO |
| **Storage/Cache** | Qdrant (Vector DB), Redis |
| **Analysis** | Playwright (Screenshots), CLIP / Computer Vision |
| **Data Feed** | Certstream (Global CT Logs) |

### Quick Start

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt
playwright install chromium
python app.py
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📄 License
MIT License - See [LICENSE](LICENSE) for details.

---

<div align="center">
<strong>Built for Samsung x KBTG Hackathon 2026</strong><br>
Protecting the Digital Future of Thailand 🇹🇭
</div>
