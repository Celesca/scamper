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

# Add optional routes to blueprints BEFORE registering them
# (Flask requires all routes to be added before blueprint registration)
try:
    from screenshot_service import create_screenshot_routes
    create_screenshot_routes(scanner_bp)
except ImportError:
    pass

# Register API blueprints (after all routes are added)
app.register_blueprint(watchtower_bp)
app.register_blueprint(scanner_bp)

# Initialize Watchtower service
init_watchtower_api(socketio)

try:
    from poisoning_bot import create_poisoning_routes
    # Create a separate blueprint for poisoning (demo only)
    from flask import Blueprint
    poison_bp = Blueprint('poison', __name__, url_prefix='/api/poison')
    create_poisoning_routes(poison_bp)
    app.register_blueprint(poison_bp)
except ImportError:
    pass

try:
    from cv_detector import create_cv_routes
    # Create a separate blueprint for CV detection
    from flask import Blueprint
    cv_bp = Blueprint('cv', __name__, url_prefix='/api/cv')
    create_cv_routes(cv_bp)
    app.register_blueprint(cv_bp)
except ImportError:
    pass

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

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Thai Brand Guardian API",
        "version": "1.0.0"
    })

@app.route('/', methods=['GET'])
def index():
    """API root endpoint."""
    return jsonify({
        "name": "Thai Brand Guardian API",
        "version": "1.0.0",
        "endpoints": {
            "watchtower": "/api/watchtower/*",
            "scanner": "/api/scanner/*",
            "cv_detector": "/api/cv/*",
            "poisoning": "/api/poison/*",
            "analyze": "/analyze"
        }
    })

if __name__ == '__main__':
    # Disable reloader to prevent restarts when Playwright modifies its files
    socketio.run(app, port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
