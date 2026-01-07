console.log("Scamper Hunter: Enhanced Content Script Loaded");

/**
 * Robust Local DOM Analysis Engine
 */
function calculateDOMFeatures() {
    const bodyText = document.body.innerText.toLowerCase();

    const features = {
        url: window.location.href,
        hostname: window.location.hostname,
        title: document.title,
        forms: [],
        links: {
            total: 0,
            external: 0,
            externalRatio: 0
        },
        sensitiveInputs: 0,
        thaiKeywords: [],
        brandVisuals: [],
        score: 0,
        reasons: []
    };

    // 1. Link Anatomy Analysis
    const allLinks = document.getElementsByTagName('a');
    features.links.total = allLinks.length;
    let externalCount = 0;
    for (let link of allLinks) {
        try {
            const url = new URL(link.href);
            if (url.hostname && url.hostname !== features.hostname && !url.hostname.includes('javascript:')) {
                externalCount++;
            }
        } catch (e) { }
    }
    features.links.external = externalCount;
    features.links.externalRatio = features.links.total > 0 ? (externalCount / features.links.total) : 0;

    // 2. Form & Input Safety
    const forms = document.getElementsByTagName('form');
    for (let form of forms) {
        const action = form.getAttribute('action') || '';
        const isExternalAction = action.startsWith('http') && !action.includes(features.hostname);
        const hasPassword = form.querySelector('input[type="password"]');

        features.forms.push({
            action: action,
            isExternal: isExternalAction,
            hasPassword: !!hasPassword
        });

        if (isExternalAction && hasPassword) {
            features.score += 40;
            features.reasons.push("Login form sends data to an external domain");
        }
    }

    const passwordInputs = document.querySelectorAll('input[type="password"]');
    if (passwordInputs.length > 0) {
        features.sensitiveInputs += passwordInputs.length;
        features.score += 15;
        features.reasons.push("Password input field detected");
    }

    // 3. Thai Phishing Keywords (Weighted)
    const keywords = {
        "ยืนยันตัวตน": 10,
        "OTP": 15,
        "ระงับบัญชี": 15,
        "ล็อกอิน": 5,
        "ความปลอดภัย": 5,
        "ธนาคาร": 10,
        "กสิกร": 10,
        "ไทยพาณิชย์": 10,
        "กรุงไทย": 10,
        "กรุงเทพ": 10
    };

    for (const [word, weight] of Object.entries(keywords)) {
        if (bodyText.includes(word.toLowerCase())) {
            features.thaiKeywords.push(word);
            features.score += weight;
            features.reasons.push(`Thai phishing keyword detected: ${word}`);
        }
    }

    // 4. Brand Visual Check (Alt tags)
    const brands = ["kbank", "scb", "kasikorn", "shopee", "lazada"];
    const images = document.getElementsByTagName('img');
    for (let img of images) {
        const alt = (img.getAttribute('alt') || '').toLowerCase();
        for (let brand of brands) {
            if (alt.includes(brand)) {
                features.brandVisuals.push(brand);
                break;
            }
        }
    }

    // 5. URL & TLD Heuristics
    const suspiciousTLDs = ['.xyz', '.top', '.loan', '.click', '.app', '.icu', '.site', '.info'];
    if (suspiciousTLDs.some(tld => features.url.toLowerCase().endsWith(tld))) {
        features.score += 20;
        features.reasons.push("Suspicious Top-Level Domain (TLD)");
    }

    if (features.hostname.split('-').length > 2) {
        features.score += 10;
        features.reasons.push("Excessive hyphens in domain name");
    }

    // Whitelist (Cheap check to reset)
    const whitelist = ['google.com', 'kbank.com', 'kasikornbank.com', 'scb.co.th', 'github.com', 'microsoft.com'];
    if (whitelist.some(domain => features.hostname.endsWith(domain))) {
        return {
            status: "Safe",
            score: 0,
            reasons: ["Known trusted domain"],
            data: features
        };
    }

    // Calculate final status
    let status = "Safe";
    if (features.score >= 60) {
        status = "Phishing";
    } else if (features.score >= 25) {
        status = "Suspicious";
    }

    return {
        status: status,
        score: Math.min(features.score, 100),
        reasons: features.reasons.length > 0 ? features.reasons : ["Local checks passed"],
        data: features
    };
}

// Automatically trigger analysis on load
setTimeout(() => {
    const result = calculateDOMFeatures();
    console.log("Scamper Hunter Result:", result);

    // Save to storage for popup
    chrome.storage.local.set({ lastResult: result });

    // Update Badge via background script
    chrome.runtime.sendMessage({
        action: "updateBadge",
        text: result.status === "Phishing" ? "!" : (result.status === "Suspicious" ? "?" : "OK"),
        color: result.status === "Phishing" ? "#EF4444" : (result.status === "Suspicious" ? "#F59E0B" : "#10B981")
    });

    // If suspicious or phishing, escalate to backend for deeper check
    if (result.status !== "Safe") {
        chrome.runtime.sendMessage({ action: "analyzePage", data: result });
    }
}, 1500);

// Allow manual trigger
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "refreshAnalysis") {
        const result = calculateDOMFeatures();
        chrome.storage.local.set({ lastResult: result });
        sendResponse(result);
    }
});
