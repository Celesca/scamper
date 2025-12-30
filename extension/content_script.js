console.log("Phishing Hunter Content Script Loaded");

function extractPageFeatures() {
    return {
        url: window.location.href,
        title: document.title,
        text: document.body.innerText.substring(0, 2000), // First 2000 chars for analysis
        forms: document.querySelectorAll("form").length,
        inputs: document.querySelectorAll("input").length
    };
}

// Automatically trigger analysis on load (throttled)
setTimeout(() => {
    const features = extractPageFeatures();
    chrome.runtime.sendMessage({ action: "analyzePage", data: features });
}, 1000);

// Also allow manual trigger
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getFeatures") {
        sendResponse(extractPageFeatures());
    }
});
