chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyzePage") {
        analyzeWithBackend(request.data);
    }
});

async function analyzeWithBackend(data) {
    try {
        const response = await fetch("http://localhost:5000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        const result = await response.json();

        // Cache result for popup or update badge
        chrome.storage.local.set({ lastResult: result });

        if (result.status === "Phishing") {
            chrome.action.setBadgeText({ text: "!" });
            chrome.action.setBadgeBackgroundColor({ color: "#FF0000" });

            // Optional: Show notification
            chrome.notifications.create({
                type: "basic",
                iconUrl: "icon.png",
                title: "Phishing Warning!",
                message: `This site looks like a phishing page. Reason: ${result.reasons[0]}`
            });
        } else if (result.status === "Suspicious") {
            chrome.action.setBadgeText({ text: "?" });
            chrome.action.setBadgeBackgroundColor({ color: "#FFA500" });
        } else {
            chrome.action.setBadgeText({ text: "OK" });
            chrome.action.setBadgeBackgroundColor({ color: "#00FF00" });
        }
    } catch (error) {
        console.error("Error communicating with backend:", error);
    }
}
