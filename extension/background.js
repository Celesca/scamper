chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyzePage") {
        analyzeWithBackend(request.data);
    } else if (request.action === "updateBadge") {
        chrome.action.setBadgeText({ text: request.text });
        chrome.action.setBadgeBackgroundColor({ color: request.color });
    }
});

async function analyzeWithBackend(data) {
    try {
        console.log("Escalating to Backend:", data);
        const response = await fetch("http://localhost:5000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error("Backend unavailable");

        const result = await response.json();

        // Cache result for popup
        chrome.storage.local.set({ lastResult: result });

        // Update badge based on backend verdict
        if (result.status === "Phishing") {
            chrome.action.setBadgeText({ text: "!" });
            chrome.action.setBadgeBackgroundColor({ color: "#EF4444" });

            chrome.notifications.create({
                type: "basic",
                iconUrl: "icon.png",
                title: "Phishing Warning!",
                message: `Escalated check: This site is confirmed as phishing. Reason: ${result.reasons[0]}`
            });
        } else if (result.status === "Suspicious") {
            chrome.action.setBadgeText({ text: "?" });
            chrome.action.setBadgeBackgroundColor({ color: "#F59E0B" });
        } else {
            chrome.action.setBadgeText({ text: "OK" });
            chrome.action.setBadgeBackgroundColor({ color: "#10B981" });
        }
    } catch (error) {
        console.error("Error communicating with backend:", error);
    }
}
