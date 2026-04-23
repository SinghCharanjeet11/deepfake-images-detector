// Dashboard functionality
const statTotal = document.getElementById('statTotal');
const statReal = document.getElementById('statReal');
const statFake = document.getElementById('statFake');
const statConf = document.getElementById('statConf');
const statRealPct = document.getElementById('statRealPct');
const statFakePct = document.getElementById('statFakePct');
const statusComplete = document.getElementById('statusComplete');
const statusProcessing = document.getElementById('statusProcessing');
const statusFailed = document.getElementById('statusFailed');
const recentList = document.getElementById('recentList');
const errorSection = document.getElementById('errorSection');
const errorText = document.getElementById('errorText');
const splitCard = document.getElementById('splitCard');
const splitReal = document.getElementById('splitReal');
const splitFake = document.getElementById('splitFake');
const splitRealLabel = document.getElementById('splitRealLabel');
const splitFakeLabel = document.getElementById('splitFakeLabel');

// Load stats on page load
loadStats();

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        
        if (!response.ok) {
            throw new Error('Failed to load statistics');
        }

        const data = await response.json();
        displayStats(data);
        displayRecent(data.recent);

    } catch (error) {
        console.error('Error loading stats:', error);
        showError(error.message || 'Unable to load dashboard data.');
    }
}

function displayStats(data) {
    // Main stats
    statTotal.textContent = data.total.toLocaleString();
    statReal.textContent = data.real.toLocaleString();
    statFake.textContent = data.fake.toLocaleString();
    statConf.textContent = `${data.avg_confidence}%`;

    // Percentages
    const complete = data.complete || 1; // avoid division by zero
    const realPct = Math.round((data.real / complete) * 100);
    const fakePct = Math.round((data.fake / complete) * 100);
    
    statRealPct.textContent = `${realPct}% of completed`;
    statFakePct.textContent = `${fakePct}% of completed`;

    // Status breakdown
    statusComplete.textContent = data.complete.toLocaleString();
    statusProcessing.textContent = data.processing.toLocaleString();
    statusFailed.textContent = data.failed.toLocaleString();

    // Real vs Fake split bar
    if (data.complete > 0) {
        splitCard.style.display = 'block';
        
        // Animate after a brief delay
        setTimeout(() => {
            splitReal.style.width = `${realPct}%`;
            splitFake.style.width = `${fakePct}%`;
        }, 200);

        splitRealLabel.textContent = `Real — ${realPct}%`;
        splitFakeLabel.textContent = `Fake — ${fakePct}%`;
    }
}

function displayRecent(recent) {
    if (!recent || recent.length === 0) {
        recentList.innerHTML = '<div class="empty-recent">No completed analyses yet.</div>';
        return;
    }

    recentList.innerHTML = '';

    recent.forEach(item => {
        const row = document.createElement('div');
        row.className = 'recent-item';
        row.onclick = () => {
            window.location.href = `/static/results.html?job_id=${item.job_id}`;
        };

        const label = item.label.toLowerCase();
        const confidence = Math.round(item.confidence * 100);
        const date = new Date(item.created_at);

        row.innerHTML = `
            <div class="recent-info">
                <div class="recent-filename">${escapeHtml(item.filename)}</div>
                <div class="recent-time">${formatTimeAgo(date)}</div>
            </div>
            <div class="recent-badge">
                <span class="badge ${label}">${label.charAt(0).toUpperCase() + label.slice(1)}</span>
                <span class="recent-conf">${confidence}%</span>
            </div>
        `;

        recentList.appendChild(row);
    });
}

function showError(message) {
    errorText.textContent = message;
    errorSection.style.display = 'block';
    document.getElementById('statGrid').style.display = 'none';
    splitCard.style.display = 'none';
    document.querySelector('.dash-two-col').style.display = 'none';
}

function formatTimeAgo(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
