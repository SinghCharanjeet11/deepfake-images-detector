// History page functionality
const loading = document.getElementById('loading');
const historySection = document.getElementById('historySection');
const historyGrid = document.getElementById('historyGrid');
const emptyState = document.getElementById('emptyState');
const errorSection = document.getElementById('errorSection');
const errorText = document.getElementById('errorText');
const pagination = document.getElementById('pagination');
const prevPage = document.getElementById('prevPage');
const nextPage = document.getElementById('nextPage');
const pageInfo = document.getElementById('pageInfo');

let currentPage = 1;
const pageSize = 10;
let totalPages = 1;

// Load history on page load
loadHistory(currentPage);

// Pagination event listeners
prevPage.addEventListener('click', () => {
    if (currentPage > 1) {
        loadHistory(currentPage - 1);
    }
});

nextPage.addEventListener('click', () => {
    if (currentPage < totalPages) {
        loadHistory(currentPage + 1);
    }
});

// Load history
async function loadHistory(page) {
    try {
        loading.style.display = 'block';
        historySection.style.display = 'none';
        emptyState.style.display = 'none';
        errorSection.style.display = 'none';

        const response = await fetch(`/api/history?page=${page}&page_size=${pageSize}`);
        
        if (!response.ok) {
            throw new Error('Failed to load history');
        }

        const data = await response.json();

        if (data.results.length === 0 && page === 1) {
            // No results at all
            loading.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }

        displayHistory(data.results);
        updatePagination(data.page, data.total_pages);

        loading.style.display = 'none';
        historySection.style.display = 'block';

    } catch (error) {
        console.error('Error loading history:', error);
        showError(error.message || 'Unable to load history. Please try again.');
    }
}

// Display history
function displayHistory(results) {
    historyGrid.innerHTML = '';

    results.forEach(result => {
        const item = createHistoryItem(result);
        historyGrid.appendChild(item);
    });
}

// Create history item
function createHistoryItem(result) {
    const item = document.createElement('div');
    item.className = 'history-item';
    item.onclick = () => {
        window.location.href = `/static/results.html?job_id=${result.job_id}`;
    };

    const label = result.label.toLowerCase();
    const confidence = Math.round(result.confidence * 100);
    const date = new Date(result.created_at);

    item.innerHTML = `
        <div class="history-thumbnail">
            <img src="/api/thumbnails/${result.job_id}" alt="Thumbnail for ${result.filename}">
        </div>
        <div class="history-info">
            <div class="history-filename">${escapeHtml(result.filename)}</div>
            <div class="history-timestamp">${formatDate(date)}</div>
        </div>
        <div class="history-result">
            <div class="history-label ${label}">${label.charAt(0).toUpperCase() + label.slice(1)}</div>
            <div class="history-confidence">${confidence}% confidence</div>
        </div>
    `;

    return item;
}

// Update pagination
function updatePagination(page, total) {
    currentPage = page;
    totalPages = total;

    pageInfo.textContent = `Page ${page} of ${total}`;

    prevPage.disabled = page === 1;
    nextPage.disabled = page === total;

    pagination.style.display = total > 1 ? 'flex' : 'none';
}

// Show error
function showError(message) {
    errorText.textContent = message;
    loading.style.display = 'none';
    errorSection.style.display = 'block';
}

// Format date
function formatDate(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 7) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    } else if (days > 0) {
        return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (minutes > 0) {
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else {
        return 'Just now';
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
