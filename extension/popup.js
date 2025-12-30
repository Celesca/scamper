document.addEventListener('DOMContentLoaded', async () => {
    const loading = document.getElementById('loading');
    const content = document.getElementById('content');
    const statusCard = document.getElementById('status-card');
    const statusIcon = document.getElementById('status-icon');
    const statusText = document.getElementById('status-text');
    const statusScore = document.getElementById('status-score');
    const reasonsContainer = document.getElementById('reasons');

    // Get last result from storage
    chrome.storage.local.get(['lastResult'], (result) => {
        if (result.lastResult) {
            displayResult(result.lastResult);
        } else {
            statusText.innerText = "No data yet";
            loading.style.display = 'none';
            content.style.display = 'block';
        }
    });

    function displayResult(data) {
        loading.style.display = 'none';
        content.style.display = 'block';

        statusText.innerText = data.status;
        statusScore.innerText = `Threat Score: ${data.score}/100`;

        reasonsContainer.innerHTML = '';
        data.reasons.forEach(reason => {
            const div = document.createElement('div');
            div.className = 'reason-item';
            div.innerHTML = `<span class="reason-bullet">•</span> <span>${reason}</span>`;
            reasonsContainer.appendChild(div);
        });

        statusCard.className = 'status-card';
        if (data.status === "Safe") {
            statusCard.classList.add('safe');
            statusIcon.innerText = '🛡️';
        } else if (data.status === "Suspicious") {
            statusCard.classList.add('suspicious');
            statusIcon.innerText = '⚠️';
        } else if (data.status === "Phishing") {
            statusCard.classList.add('danger');
            statusIcon.innerText = '🚨';
        }
    }
});
