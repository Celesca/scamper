console.log("Phishing Hunter Content Script Loaded");

function bouncerCheck() {
    const features = {
        url: window.location.href,
        title: document.title,
        text: document.body.innerText.substring(0, 2000),
        hostname: window.location.hostname
    };

    let score = 0;
    let reasons = [];

    // 1. Whitelist (Cheap check)
    const whitelist = ['google.com', 'kbank.com', 'kasikornbank.com', 'scb.co.th', 'github.com'];
    if (whitelist.some(domain => features.hostname.endsWith(domain))) {
        return { action: "ignore", score: 0, status: "Safe", reasons: ["Known trusted domain"] };
    }

    // 2. Thai Keyword Detection (The "Trigger")
    const thaiKeywords = ["ยืนยันตัวตน", "OTP", "ระงับบัญชี", "ล็อกอิน", "ความปลอดภัย", "อัปเดตข้อมูล"];
    const foundKeywords = thaiKeywords.filter(word => features.text.includes(word));
    if (foundKeywords.length > 0) {
        score += 30;
        reasons.push(`Thai phishing keywords detected: ${foundKeywords.join(", ")}`);
    }

    // 3. Sensitive Input Detection
    const hasPassword = !!document.querySelector('input[type="password"]');
    if (hasPassword) {
        score += 20;
        reasons.push("Login form detected");
    }

    // 4. Suspicious TLD
    const suspiciousTLDs = ['.xyz', '.top', '.loan', '.click', '.app', '.icu', '.site'];
    if (suspiciousTLDs.some(tld => features.url.endsWith(tld))) {
        score += 25;
        reasons.push("Suspicious TLD detected");
    }

    return {
        action: score > 20 ? "escalate" : "safe",
        score,
        reasons,
        data: features
    };
}

// Automatically trigger analysis on load
setTimeout(() => {
    const result = bouncerCheck();
    if (result.action === "escalate") {
        console.log("Layer 1 (Bouncer): Escalating to Backend", result);
        chrome.runtime.sendMessage({ action: "analyzePage", data: result });
    } else {
        console.log("Layer 1 (Bouncer): Site appears safe locally.");
        chrome.storage.local.set({
            lastResult: {
                status: "Safe",
                score: result.score,
                reasons: result.reasons.length > 0 ? result.reasons : ["Local checks passed"]
            }
        });
        chrome.action.setBadgeText({ text: "OK" });
        chrome.action.setBadgeBackgroundColor({ color: "#00FF00" });
    }
}, 1500);

// Also allow manual trigger
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getFeatures") {
        sendResponse(extractPageFeatures());
    }
});
