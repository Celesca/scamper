from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

def analyze_phishing(data):
    url = data.get('url', '')
    title = data.get('title', '')
    text_content = data.get('text', '')
    
    score = 0
    reasons = []
    
    # 1. Check for suspicious keywords in the text
    phishing_keywords = ['login', 'verify', 'account', 'security', 'suspended', 'update', 'billing', 'bank', 'paypal', 'amazon', 'microsoft', 'google']
    found_keywords = [word for word in phishing_keywords if word in text_content.lower()]
    if found_keywords:
        score += 20
        reasons.append(f"Suspicious keywords found: {', '.join(found_keywords)}")

    # 2. Check for URL/Title mismatch (Brand hijacking)
    domain = urlparse(url).netloc.lower()
    common_brands = ['google', 'paypal', 'amazon', 'microsoft', 'apple', 'netflix', 'facebook']
    for brand in common_brands:
        if brand in title.lower() and brand not in domain:
            score += 50
            reasons.append(f"Mismatched Brand: Title mentions '{brand}' but the domain is '{domain}'")

    # 3. Check for suspicious TLDs or long subdomains
    if domain.count('.') > 3:
        score += 15
        reasons.append("Highly nested subdomains detected")
    
    risky_tlds = ['.xyz', '.top', '.loan', '.click', '.app', '.icu']
    if any(url.endswith(tld) for tld in risky_tlds):
        score += 10
        reasons.append("URL uses a high-risk TLD")

    # Final Classification
    status = "Safe"
    if score >= 60:
        status = "Phishing"
    elif score >= 20:
        status = "Suspicious"
        
    return {
        "status": status,
        "score": score,
        "reasons": reasons
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    result = analyze_phishing(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
