// Upload page functionality
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const selectedFile = document.getElementById('selectedFile');
const previewImage = document.getElementById('previewImage');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const uploadBtn = document.getElementById('uploadBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const errorMessage = document.getElementById('errorMessage');

let selectedFileData = null;

// Supported file types
const SUPPORTED_TYPES = ['image/jpeg', 'image/png', 'image/jpg'];
const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB

// Drag and drop events
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Remove file
removeFile.addEventListener('click', () => {
    resetUpload();
});

// Upload button
uploadBtn.addEventListener('click', () => {
    if (selectedFileData && !uploadBtn.disabled) {
        uploadBtn.disabled = true; // Prevent double-click
        uploadFile(selectedFileData);
    }
});

// Handle file selection
function handleFileSelect(file) {
    // Validate file type
    if (!SUPPORTED_TYPES.includes(file.type)) {
        showError('Please select a valid image file (JPEG or PNG)');
        return;
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
        showError('File size must be less than 500MB');
        return;
    }

    selectedFileData = file;
    hideError();

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        dropZone.style.display = 'none';
        selectedFile.style.display = 'flex';
        uploadBtn.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// Upload file
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Hide upload button and show progress
        uploadBtn.style.display = 'none';
        progressContainer.style.display = 'block';
        progressText.textContent = 'Uploading...';
        hideError();

        // Upload file
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();
        const jobId = data.job_id;

        // Poll for results
        progressText.textContent = 'Analyzing image...';
        await pollJobStatus(jobId);

    } catch (error) {
        console.error('Upload error:', error);
        showError(error.message || 'Failed to upload file. Please try again.');
        progressContainer.style.display = 'none';
        uploadBtn.style.display = 'block';
    }
}

// Poll job status
async function pollJobStatus(jobId) {
    const maxAttempts = 120; // 120 attempts = 2 minutes
    let attempts = 0;

    const poll = async () => {
        try {
            const response = await fetch(`/api/jobs/${jobId}`);
            
            if (!response.ok) {
                throw new Error('Failed to check status');
            }

            const data = await response.json();

            if (data.status === 'completed' || data.status === 'complete') {
                // Redirect to results page
                window.location.href = `/static/results.html?job_id=${jobId}`;
                return;
            }

            if (data.status === 'failed') {
                throw new Error(data.error || 'Analysis failed');
            }

            // Update progress
            const progress = Math.min((attempts / maxAttempts) * 100, 95);
            progressFill.style.width = `${progress}%`;

            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(poll, 1000); // Poll every second
            } else {
                throw new Error('Analysis is taking longer than expected. Please check history later.');
            }

        } catch (error) {
            console.error('Polling error:', error);
            showError(error.message || 'Failed to get results. Please try again.');
            progressContainer.style.display = 'none';
            uploadBtn.style.display = 'block';
            uploadBtn.disabled = false; // Re-enable button
        }
    };

    poll();
}

// Reset upload
function resetUpload() {
    selectedFileData = null;
    fileInput.value = '';
    previewImage.src = '';
    fileName.textContent = '';
    fileSize.textContent = '';
    
    dropZone.style.display = 'block';
    selectedFile.style.display = 'none';
    uploadBtn.style.display = 'none';
    uploadBtn.disabled = false; // Re-enable button
    progressContainer.style.display = 'none';
    progressFill.style.width = '0%';
    hideError();
}

// Show error
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

// Hide error
function hideError() {
    errorMessage.style.display = 'none';
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
