// History page — with search, label filter, and pagination
const loading         = document.getElementById('loading');
const historySection  = document.getElementById('historySection');
const historyGrid     = document.getElementById('historyGrid');
const historyCount    = document.getElementById('historyCount');
const emptyState      = document.getElementById('emptyState');
const emptyTitle      = document.getElementById('emptyTitle');
const emptyMsg        = document.getElementById('emptyMsg');
const emptyAction     = document.getElementById('emptyAction');
const errorSection    = document.getElementById('errorSection');
const errorText       = document.getElementById('errorText');
const pagination      = document.getElementById('pagination');
const prevPage        = document.getElementById('prevPage');
const nextPage        = document.getElementById('nextPage');
const pageInfo        = document.getElementById('pageInfo');
const searchInput     = document.getElementById('searchInput');
const searchClear     = document.getElementById('searchClear');
const filterTabs      = document.getElementById('filterTabs');

let currentPage  = 1;
const pageSize   = 10;
let totalPages   = 1;
let activeLabel  = 'all';   // 'all' | 'real' | 'fake'
let searchQuery  = '';
let searchTimer  = null;

// ── Initial load ──────────────────────────────────────────────
loadHistory(1);

// ── Search input ──────────────────────────────────────────────
searchInput.addEventListener('input', () => {
    searchQuery = searchInput.value.trim();
    searchClear.style.display = searchQuery ? 'flex' : 'none';

    // Debounce: wait 350ms after user stops typing
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => loadHistory(1), 350);
});

searchClear.addEventListener('click', () => {
    searchInput.value = '';
    searchQuery = '';
    searchClear.style.display = 'none';
    loadHistory(1);
});

// ── Filter tabs ───────────────────────────────────────────────
filterTabs.addEventListener('click', (e) => {
    const tab = e.target.closest('.filter-tab');
    if (!tab) return;

    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    activeLabel = tab.dataset.label;
    loadHistory(1);
});

// ── Pagination ────────────────────────────────────────────────
prevPage.addEventListener('click', () => {
    if (currentPage > 1) loadHistory(currentPage - 1);
});

nextPage.addEventListener('click', () => {
    if (currentPage < totalPages) loadHistory(currentPage + 1);
});

// ── Core fetch ────────────────────────────────────────────────
async function loadHistory(page) {
    try {
        showLoading();

        const params = new URLSearchParams({
            page,
            page_size: pageSize,
        });

        if (activeLabel !== 'all') params.set('label', activeLabel);
        if (searchQuery)           params.set('search', searchQuery);

        const response = await fetch(`/api/history?${params}`);

        if (!response.ok) throw new Error('Failed to load history');

        const data = await response.json();

        if (data.results.length === 0) {
            showEmpty();
            return;
        }

        displayHistory(data.results, data.total);
        updatePagination(data.page, data.pages);

        loading.style.display       = 'none';
        historySection.style.display = 'block';

    } catch (error) {
        console.error('Error loading history:', error);
        showError(error.message || 'Unable to load history. Please try again.');
    }
}

// ── Render list ───────────────────────────────────────────────
function displayHistory(results, total) {
    historyGrid.innerHTML = '';

    const filterLabel = activeLabel !== 'all' ? ` (${activeLabel})` : '';
    const searchLabel = searchQuery ? ` matching "${searchQuery}"` : '';
    historyCount.textContent = `${total} record${total !== 1 ? 's' : ''}${filterLabel}${searchLabel}`;

    results.forEach(result => historyGrid.appendChild(createHistoryItem(result)));
}

function createHistoryItem(result) {
    const item = document.createElement('div');
    item.className = 'history-item';
    item.onclick = () => {
        window.location.href = `/static/results.html?job_id=${result.job_id}`;
    };

    const label      = result.label.toLowerCase();
    const confidence = Math.round(result.confidence * 100);
    const date       = new Date(result.created_at);

    item.innerHTML = `
        <img
            class="history-thumb"
            src="/api/thumbnails/${result.job_id}"
            alt="Thumbnail"
            onerror="this.style.opacity='0.2'"
        >
        <div class="history-info">
            <div class="history-filename">${escapeHtml(result.filename)}</div>
            <div class="history-timestamp">${formatDate(date)}</div>
        </div>
        <div class="history-badge">
            <span class="badge ${label}">${label.charAt(0).toUpperCase() + label.slice(1)}</span>
            <span class="history-conf">${confidence}%</span>
        </div>
        <svg class="history-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
        </svg>
    `;

    return item;
}

// ── Pagination ────────────────────────────────────────────────
function updatePagination(page, total) {
    currentPage = page;
    totalPages  = total;

    pageInfo.textContent  = `Page ${page} of ${total}`;
    prevPage.disabled     = page === 1;
    nextPage.disabled     = page === total;
    pagination.style.display = total > 1 ? 'flex' : 'none';
}

// ── UI state helpers ──────────────────────────────────────────
function showLoading() {
    loading.style.display        = 'block';
    historySection.style.display = 'none';
    emptyState.style.display     = 'none';
    errorSection.style.display   = 'none';
}

function showEmpty() {
    loading.style.display        = 'none';
    historySection.style.display = 'none';
    errorSection.style.display   = 'none';
    emptyState.style.display     = 'block';

    const isFiltered = activeLabel !== 'all' || searchQuery;
    if (isFiltered) {
        emptyTitle.textContent  = 'No results found';
        emptyMsg.textContent    = 'Try a different search term or filter.';
        emptyAction.textContent = 'Clear filters';
        emptyAction.href        = '#';
        emptyAction.onclick     = (e) => {
            e.preventDefault();
            searchInput.value = '';
            searchQuery       = '';
            searchClear.style.display = 'none';
            activeLabel       = 'all';
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            document.querySelector('.filter-tab[data-label="all"]').classList.add('active');
            loadHistory(1);
        };
    } else {
        emptyTitle.textContent  = 'No records yet';
        emptyMsg.textContent    = 'Upload an image to start building your detection history.';
        emptyAction.textContent = 'Analyze an Image';
        emptyAction.href        = '/static/index.html';
        emptyAction.onclick     = null;
    }
}

function showError(message) {
    errorText.textContent        = message;
    loading.style.display        = 'none';
    historySection.style.display = 'none';
    errorSection.style.display   = 'block';
}

// ── Utilities ─────────────────────────────────────────────────
function formatDate(date) {
    const now     = new Date();
    const diff    = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours   = Math.floor(minutes / 60);
    const days    = Math.floor(hours / 24);

    if (days > 7)    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    if (days > 0)    return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0)   return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
