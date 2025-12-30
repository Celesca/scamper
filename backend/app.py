from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from urllib.parse import urlparse

from fuzzer import analyze_domain_advanced

app = Flask(__name__)
CORS(app)

# Comprehensive list of Tier 1 Thai websites
THAI_TARGETS = [
    'kbank', 'kasikornbank', 'scb', 'bangkokbank', 'ktb', 'krungsri', 'ttb', 'gsb',
    'lazada', 'shopee', 'line', 'facebook', 'google', 'netflix', 'apple', 'microsoft'
]

def layer2_detective(data):
    """
    Layer 2: Lightweight Cloud API (The Detective)
    Checks URL structure, keyword density, and local report.
    """
    url = data.get('url', '')
    local_score = data.get('localScore', 0)
    
    score = local_score
    reasons = data.get('localReasons', [])
    
    domain = urlparse(url).netloc.lower()
    
    # 1. Advanced Typosquatting Analysis (DNSTwist-style)
    fuzzer_results = analyze_domain_advanced(domain, THAI_TARGETS)
    for res in fuzzer_results:
        score += 45
        reasons.append(f"Typosquatting Detected: '{domain}' mimics '{res['target']}' via {res['reason']}")

    # 2. URL Entropy / Complexity
    if len(url) > 100:
        score += 10
        reasons.append("Excessively long URL")

    status = "Suspicious"
    if score > 70:
        # Escalate to Layer 3
        return layer3_judge(data, score, reasons)
    
    return {
        "status": status,
        "score": score,
        "reasons": reasons,
        "layer": "Detective"
    }

def layer3_judge(data, current_score, current_reasons):
    """
    Layer 3: The Judge (Expensive AI)
    Uses LLM to analyze the intent and context.
    """
    # For this example, we simulate the 'Judge' confirming the phishing intent.
    # In a real app, you'd call Gemini/GPT-4 here.
    
    final_score = current_score + 15
    current_reasons.append("AI Judge: Intent analysis confirms phishing pattern (High Risk)")
    
    return {
        "status": "Phishing",
        "score": min(final_score, 100),
        "reasons": current_reasons,
        "layer": "Judge"
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Extension only calls if Layer 1 (Bouncer) is suspicious
    result = layer2_detective(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
