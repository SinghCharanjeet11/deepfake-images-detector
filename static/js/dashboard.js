// Dashboard functionality
const loading = document.getElementById('loading');
const dashboardContent = document.getElementById('dashboardContent');
const errorSection = document.getElementById('errorSection');
const errorText = document.getElementById('errorText');

// Load dashboard data on page load
loadDashboard();

async function loadDashboard() {
    try {
        loading.style.display = 'block';
        dashboardContent.style.display = 'none';
        errorSection.style.display = 'none';

        // Fetch history data
        const response = await fetch('/api/history?page=1&page_size=100');
        
        if (!response.ok) {
            throw new Error('Failed to load dashboard data');
        }

        const data = await response.json();
        const results = data.results || [];

        // Calculate statistics
        const stats = calculateStats(results);
        
        // Update UI
        updateStats(stats);
        updateDonutChart(stats);
        updateRecentActivity(results.slice(0, 7));
        updateRecentDetections(results.slice(0, 6));

        loading.style.display = 'none';
        dashboardContent.style.display = 'block';

    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError(error.message || 'Unable to load dashboard. Please try again.');
    }
}

function calculateStats(results) {
    const total = results.length;
    const realCount = results.filter(r => r.label.toLowerCase() === 'real').length;
    const fakeCount = results.filter(r => r.label.toLowerCase() === 'fake').length;
    
    const realPercentage = total > 0 ? Math.round((realCount / total) * 100) : 0;
    const fakePercentage = total > 0 ? Math.round((fakeCount / total) * 100) : 0;
    
    const avgConfidence = total > 0 
        ? Math.round(results.reduce((sum, r) => sum + r.confidence, 0) / total * 100)
        : 0;

    // Calculate this week's count (last 7 days)
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    const thisWeekCount = results.filter(r => new Date(r.created_at) >= oneWeekAgo).length;

    return {
        total,
        realCount,
        fakeCount,
        realPercentage,
        fakePercentage,
        avgConfidence,
        thisWeekCount
    };
}

function updateStats(stats) {
    // Total analyses
    document.getElementById('totalAnalyses').textContent = stats.total.toLocaleString();
    document.getElementById('totalChange').textContent = `+${stats.thisWeekCount} this week`;
    
    // Real images
    document.getElementById('realCount').textContent = stats.realCount.toLocaleString();
    document.getElementById('realPercentage').textContent = `${stats.realPercentage}%`;
    
    // Fake images
    document.getElementById('fakeCount').textContent = stats.fakeCount.toLocaleString();
    document.getElementById('fakePercentage').textContent = `${stats.fakePercentage}%`;
    
    // Average confidence
    document.getElementById('avgConfidence').textContent = `${stats.avgConfidence}%`;
}

function updateDonutChart(stats) {
    const total = stats.total;
    const realCount = stats.realCount;
    const fakeCount = stats.fakeCount;

    // Update center text
    document.getElementById('donutTotal').textContent = total.toLocaleString();

    // Update legend
    document.getElementById('legendReal').textContent = realCount.toLocaleString();
    document.getElementById('legendFake').textContent = fakeCount.toLocaleString();

    if (total === 0) return;

    // Calculate arc lengths (circumference = 2πr = 2π*80 ≈ 502)
    const circumference = 502;
    const realArcLength = (realCount / total) * circumference;
    const fakeArcLength = (fakeCount / total) * circumference;

    // Update real arc
    const realArc = document.getElementById('realArc');
    realArc.setAttribute('stroke-dasharray', `${realArcLength} ${circumference}`);
    realArc.setAttribute('stroke-dashoffset', '125'); // Start at top

    // Update fake arc (starts where real ends)
    const fakeArc = document.getElementById('fakeArc');
    fakeArc.setAttribute('stroke-dasharray', `${fakeArcLength} ${circumference}`);
    fakeArc.setAttribute('stroke-dashoffset', `${125 - realArcLength}`);
}

function updateRecentActivity(results) {
    const activityList = document.getElementById('activityList');
    activityList.innerHTML = '';

    if (results.length === 0) {
        activityList.innerHTML = '<div class="empty-activity">No recent activity</div>';
        return;
    }

    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'activity-item';
        
        const label = result.label.toLowerCase();
        const confidence = Math.round(result.confidence * 100);
        const date = new Date(result.created_at);
        const timeAgo = formatTimeAgo(date);

        item.innerHTML = `
            <div class="activity-icon ${label}">
                ${label === 'real' 
                    ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
                    : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
                }
            </div>
            <div class="activity-details">
                <div class="activity-title">${escapeHtml(result.filename)}</div>
                <div class="activity-meta">${timeAgo} · ${confidence}% confidence</div>
            </div>
            <span class="activity-badge ${label}">${label}</span>
        `;

        item.onclick = () => {
            window.location.href = `/static/results.html?job_id=${result.job_id}`;
        };

        activityList.appendChild(item);
    });
}

function updateRecentDetections(results) {
    const recentGrid = document.getElementById('recentGrid');
    recentGrid.innerHTML = '';

    if (results.length === 0) {
        recentGrid.innerHTML = '<div class="empty-recent">No detections yet. <a href="/static/index.html">Analyze your first image →</a></div>';
        return;
    }

    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'recent-card';
        
        const label = result.label.toLowerCase();
        const confidence = Math.round(result.confidence * 100);
        const date = new Date(result.created_at);

        item.innerHTML = `
            <div class="recent-image">
                <img src="/api/thumbnails/${result.job_id}" alt="${escapeHtml(result.filename)}" onerror="this.style.opacity='0.3'">
                <div class="recent-overlay">
                    <span class="recent-badge ${label}">${label}</span>
                </div>
            </div>
            <div class="recent-info">
                <div class="recent-filename">${escapeHtml(result.filename)}</div>
                <div class="recent-meta">
                    <span>${confidence}% confidence</span>
                    <span>·</span>
                    <span>${formatDate(date)}</span>
                </div>
            </div>
        `;

        item.onclick = () => {
            window.location.href = `/static/results.html?job_id=${result.job_id}`;
        };

        recentGrid.appendChild(item);
    });
}

function showError(message) {
    errorText.textContent = message;
    loading.style.display = 'none';
    errorSection.style.display = 'block';
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

function formatDate(date) {
    const options = { month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
