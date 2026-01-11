from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import re
from urllib.parse import urlparse

from fuzzer import analyze_domain_advanced
from watchtower_api import watchtower_bp, init_watchtower_api
from scanner_api import scanner_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Register blueprints
app.register_blueprint(watchtower_bp)
app.register_blueprint(scanner_bp)

# Initialize Watchtower service
init_watchtower_api(socketio)

# Tier 1 Thai targets for typosquatting analysis
THAI_TARGETS = [
    'kbank', 'kasikornbank', 'scb', 'bangkokbank', 'ktb', 'krungsri', 'ttb', 'gsb',
    'lazada', 'shopee', 'line', 'facebook', 'google', 'netflix', 'apple', 'microsoft'
]

def layer2_detective(data):
    """
    Layer 2: Lightweight Cloud API (The Detective)
    Checks URL structure, keyword density, and pre-calculated DOM features.
    """
    url = data.get('url', '')
    local_score = data.get('score', 0)
    reasons = data.get('reasons', [])
    dom_data = data.get('data', {})
    
    score = local_score
    domain = urlparse(url).netloc.lower()
    
    # 1. Advanced Typosquatting Analysis
    fuzzer_results = analyze_domain_advanced(domain, THAI_TARGETS)
    for res in fuzzer_results:
        score += 45
        reasons.append(f"Typosquatting Detected: '{domain}' mimics '{res['target']}' via {res['reason']}")

    # 2. URL Entropy / Complexity
    if len(url) > 100:
        score += 10
        reasons.append("Excessively long URL")

    # 3. Enhanced Feature Weighting
    links = dom_data.get('links', {})
    if links.get('externalRatio', 0) > 0.8:
        score += 15
        reasons.append("High ratio of external links (>80%)")

    # Escalate to Layer 3 if score is significant
    if score > 50:
        return layer3_judge(data, score, reasons)
    
    status = "Safe"
    if score >= 60: status = "Phishing"
    elif score >= 25: status = "Suspicious"

    return {
        "status": status,
        "score": min(score, 100),
        "reasons": list(set(reasons)),
        "layer": "Detective"
    }

def layer3_judge(data, current_score, current_reasons):
    """
    Layer 3: The Judge (Logic-based)
    Verifies intent by cross-referencing brand presence with interactive elements.
    """
    dom_data = data.get('data', {})
    final_score = current_score
    
    # Logic-based confirmation
    forms = dom_data.get('forms', [])
    has_external_form = any(f.get('isExternal') for f in forms)
    has_brand = len(dom_data.get('brandVisuals', [])) > 0
    
    if has_external_form and has_brand:
        final_score += 30
        current_reasons.append("Judge Verdict: High Confidence Phishing (Brand impersonation with external data submission)")
    elif len(forms) > 0 and has_brand:
        final_score += 20
        current_reasons.append("Judge Verdict: Suspicious Brand Usage (Brand elements found near data entry forms)")
    
    status = "Safe"
    if final_score >= 60:
        status = "Phishing"
    elif final_score >= 25:
        status = "Suspicious"
    
    return {
        "status": status,
        "score": min(final_score, 100),
        "reasons": list(set(current_reasons)),
        "layer": "Judge"
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    result = layer2_detective(data)
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Scamper Hunter API", "version": "1.1.0"})

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
