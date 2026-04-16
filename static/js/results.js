// Results page functionality
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const resultLabel = document.getElementById('resultLabel');
const confidenceValue = document.getElementById('confidenceValue');
const thumbnail = document.getElementById('thumbnail');
const filename = document.getElementById('filename');
const timestamp = document.getElementById('timestamp');
const downloadPdf = document.getElementById('downloadPdf');
const downloadJson = document.getElementById('downloadJson');
const errorText = document.getElementById('errorText');

// Get job ID from URL
const urlParams = new URLSearchParams(window.location.search);
const jobId = urlParams.get('job_id');

if (!jobId) {
    showError('No job ID provided');
} else {
    loadResults(jobId);
}

// Load results
async function loadResults(jobId) {
    try {
        // Fetch job details
        const response = await fetch(`/api/jobs/${jobId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load results');
        }

        const data = await response.json();

        if (data.status === 'pending' || data.status === 'processing') {
            // Still processing, poll again
            setTimeout(() => loadResults(jobId), 1000);
            return;
        }

        if (data.status === 'failed') {
            throw new Error(data.error || 'Analysis failed');
        }

        if (data.status === 'completed' || data.status === 'complete') {
            displayResults(data);
        }

    } catch (error) {
        console.error('Error loading results:', error);
        showError(error.message || 'Unable to load results. Please try again.');
    }
}

// Display results
function displayResults(data) {
    // Handle both direct data and nested result object
    const result = data.result || data;
    
    // Set label
    const label = (result.label || data.label || '').toLowerCase();
    resultLabel.textContent = label.charAt(0).toUpperCase() + label.slice(1);
    resultLabel.className = `result-label ${label}`;

    // Set confidence
    const confidence = Math.round((result.confidence || data.confidence || 0) * 100);
    confidenceValue.textContent = `${confidence}%`;

    // Set filename
    filename.textContent = result.filename || data.filename || 'Unknown';

    // Set timestamp
    const dateStr = result.timestamp || result.created_at || data.created_at;
    if (dateStr) {
        const date = new Date(dateStr);
        timestamp.textContent = formatDate(date);
    }

    // Load thumbnail
    const jobId = data.job_id || urlParams.get('job_id');
    thumbnail.src = `/api/thumbnails/${jobId}`;
    thumbnail.alt = `Thumbnail for ${result.filename || data.filename}`;

    // Setup download buttons
    downloadPdf.addEventListener('click', () => {
        window.location.href = `/api/reports/${jobId}/pdf`;
    });

    downloadJson.addEventListener('click', () => {
        window.location.href = `/api/reports/${jobId}/json`;
    });

    // Show results
    loading.style.display = 'none';
    resultsSection.style.display = 'block';
}

// Show error
function showError(message) {
    errorText.textContent = message;
    loading.style.display = 'none';
    errorSection.style.display = 'block';
}

// Format date
function formatDate(date) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}
