# 🛡️ Thai Brand Guardian

**AI-Powered Phishing Detection & Active Defense System for Thai Brands**

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-16+-black.svg)

*Protect Thai banks, e-commerce platforms, and enterprises from phishing attacks with real-time monitoring, computer vision detection, and active defense capabilities.*

</div>

---

## 🚀 Features

### 🗼 Watchtower - Real-time CT Log Monitoring
Monitor Certificate Transparency logs in real-time to detect suspicious domain registrations targeting Thai brands.

- **DNSTwist-style fuzzing**: Detects typosquatting, homoglyphs, and lookalike domains
- **Thai brand focus**: Monitors KBTG, KBank, SCB, Lazada, Shopee, LINE, and more
- **Instant alerts**: WebSocket-powered real-time notifications

### 🔍 Domain Scanner
On-demand scanning of domains with comprehensive vulnerability analysis.

- **Permutation generation**: Creates thousands of potential phishing variants
- **DNS resolution**: Checks which domains are actually registered
- **Risk scoring**: AI-powered threat assessment

### 👁️ Computer Vision Detection
AI-powered visual analysis catches zero-day phishing sites that bypass blacklists.

- **Logo detection**: Identifies unauthorized use of brand logos
- **Visual similarity**: Compares screenshots against legitimate sites
- **Thai UI patterns**: Recognizes PromptPay/Thai QR Payment impersonation

### 🤖 Active Defense - Poisoning Bot
Fight back against phishers by polluting their captured data.

- **Fake credential generation**: Creates realistic-looking fake data
- **Form detection**: Automatically identifies phishing input fields
- **Demo mode**: Safe testing without actual submission

### 📧 Automated Takedown
Streamlined reporting to hosting providers.

- **Evidence packages**: Auto-generated screenshots and logs
- **Provider templates**: Pre-formatted emails for major hosts
- **Status tracking**: Monitor takedown progress

### 🔌 Chrome Extension
Browser-based protection with 3-layer detection.

- **Layer 1 (Bouncer)**: Fast local checks in content script
- **Layer 2 (Detective)**: Backend typosquatting analysis
- **Layer 3 (Judge)**: AI intent analysis for edge cases

---

## 📦 Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- Chrome browser (for extension)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for screenshot service)
playwright install chromium

# Start the server
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit `http://localhost:3000` to access the dashboard.

### Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension/` folder

---

## 🎯 API Endpoints

### Watchtower API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/watchtower/status` | GET | Get monitoring status |
| `/api/watchtower/start` | POST | Start CT log monitoring |
| `/api/watchtower/stop` | POST | Stop monitoring |
| `/api/watchtower/detections` | GET | Get detected threats |

### Scanner API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scanner/scan` | POST | Scan a domain for threats |
| `/api/scanner/permutations` | POST | Get domain permutations |
| `/api/scanner/screenshot` | POST | Capture site screenshot |

### Analysis API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Analyze page for phishing |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Landing Page │  │   Scanner    │  │  Extension   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend (Flask)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Watchtower  │  │   Scanner    │  │  CV Detector │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ Poisoning Bot│  │   Takedown   │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     External Services                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Certstream  │  │ DNS Servers  │  │   Hosting    │       │
│  │  (CT Logs)   │  │              │  │  Providers   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🇹🇭 Thai-Specific Features

- **Thai bank monitoring**: KBank, SCB, Bangkok Bank, KTB, Krungsri, TTB, GSB
- **Thai keyword detection**: ยืนยันตัวตน, OTP, ระงับบัญชี, อัปเดตข้อมูล
- **PromptPay pattern recognition**: Detects fake Thai QR Payment interfaces
- **LINE-based redirect detection**: Catches LINE-to-phishing redirects

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 16, React 19, Tailwind CSS 4 |
| Backend | Flask, Flask-SocketIO |
| CT Monitoring | Certstream |
| Domain Fuzzing | DNSTwist-style algorithms |
| Screenshots | Playwright |
| CV Analysis | CLIP / Image Similarity |

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.

---

<div align="center">
<strong>Built for Samsung x KBTG Hackathon 2026</strong>
<br>
Protecting Thai digital citizens from online fraud
</div>
