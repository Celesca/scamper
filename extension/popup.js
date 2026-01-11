document.addEventListener('DOMContentLoaded', async () => {
    const loader = document.getElementById('loader');
    const meterFill = document.getElementById('meter-fill');
    const scoreValue = document.getElementById('score-value');
    const statusBadge = document.getElementById('status-badge');
    const reasonList = document.getElementById('reason-list');

    // Get last result from storage
    chrome.storage.local.get(['lastResult'], (result) => {
        if (result.lastResult) {
            updateUI(result.lastResult);
        } else {
            if (statusBadge) statusBadge.innerText = "No data yet";
            if (loader) {
                loader.style.opacity = '0';
                setTimeout(() => loader.style.display = 'none', 500);
            }
        }
    });

    function updateUI(data) {
        // Hide loader
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => loader.style.display = 'none', 500);
        }

        // Update Score Text with counting animation
        if (scoreValue) animateValue(scoreValue, 0, data.score, 1000);

        // Update Meter Fill
        // Circumference is 2 * PI * 70 = 440
        if (meterFill) {
            const circumference = 440;
            const offset = circumference - (data.score / 100) * circumference;
            meterFill.style.strokeDashoffset = offset;
        }

        // Update Status Badge and Colors
        if (statusBadge) {
            statusBadge.innerText = data.status;
            statusBadge.className = 'status-badge';

            if (data.status === "Safe") {
                statusBadge.classList.add('status-safe');
                if (meterFill) meterFill.style.stroke = 'var(--success)';
            } else if (data.status === "Suspicious") {
                statusBadge.classList.add('status-warning');
                if (meterFill) meterFill.style.stroke = 'var(--warning)';
            } else {
                statusBadge.classList.add('status-danger');
                if (meterFill) meterFill.style.stroke = 'var(--danger)';
            }
        }

        // Update Reasons
        if (reasonList) {
            reasonList.innerHTML = '';
            if (data.reasons && data.reasons.length > 0) {
                data.reasons.forEach((reason, index) => {
                    const li = document.createElement('li');
                    li.className = 'reason-item';
                    li.style.animationDelay = `${index * 0.1}s`;
                    li.innerHTML = `<div class="reason-dot"></div><span>${reason}</span>`;
                    reasonList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.className = 'reason-item';
                li.innerHTML = `<div class="reason-dot"></div><span>Local checks passed</span>`;
                reasonList.appendChild(li);
            }
        }
    }

    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
});
