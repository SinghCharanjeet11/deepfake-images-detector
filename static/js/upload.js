const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const selectedFile = document.getElementById('selectedFile');
const previewImage = document.getElementById('previewImage');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const uploadBtn = document.getElementById('uploadBtn');
const dropZoneContent = document.getElementById('dropZoneContent');
const progressContainer = document.getElementById('progressContainer');
const errorMessage = document.getElementById('errorMessage');


let selectedFileData = null;
const SUPPORTED_TYPES = ['image/jpeg', 'image/png', 'image/jpg'];
const MAX_FILE_SIZE = 500 * 1024 * 1024;

['click', 'dragover', 'dragleave', 'drop'].forEach(evt => {
    dropZone.addEventListener(evt, (e) => {
        if(evt !== 'click' || (!e.target.closest('label') && e.target !== fileInput && e.target !== removeFile && !e.target.closest('#removeFile'))) {
            e.preventDefault();
            if(evt === 'click' && dropZoneContent.style.display !== 'none'){ fileInput.click(); }
            if(evt === 'dragover') dropZone.classList.add('drag-over');
            if(evt === 'dragleave' || evt === 'drop') dropZone.classList.remove('drag-over');
            if(evt === 'drop' && e.dataTransfer.files.length) handleFileSelect(e.dataTransfer.files[0]);
        }
    });
});
fileInput.addEventListener('change', (e) => { if (e.target.files.length) handleFileSelect(e.target.files[0]); });
removeFile.addEventListener('click', (e) => { e.stopPropagation(); resetUpload(); });







uploadBtn.addEventListener('click', () => {
    if (selectedFileData && !uploadBtn.disabled) {
        uploadBtn.disabled = true;
        uploadFile(selectedFileData);
    }
});

function handleFileSelect(file) {
    if (!SUPPORTED_TYPES.includes(file.type)) return showError('Please select a valid image (JPEG/PNG)');
    if (file.size > MAX_FILE_SIZE) return showError('File too large');
    
    selectedFileData = file;
    hideError();
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        dropZoneContent.style.display = 'none';
        selectedFile.style.display = 'flex';
        uploadBtn.style.display = 'inline-flex';
    };
    reader.readAsDataURL(file);
}


let currentAnimStep = 0;
let animInterval = null;
let uploadAbortController = null;

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    uploadAbortController = new AbortController();
    
    try {
        uploadBtn.style.display = 'none';
        progressContainer.style.display = 'flex';
        hideError();
        
        // Start detached animation logic
        currentAnimStep = 0;
        const steps = [document.getElementById('step1'), document.getElementById('step2'), document.getElementById('step3'), document.getElementById('step4')];
        steps.forEach(s => s.className = 'step');
        
        animInterval = setInterval(() => {
            if(currentAnimStep < 3) currentAnimStep++;
            steps.forEach((s, idx) => {
                s.className = 'step';
                if(idx < currentAnimStep) s.classList.add('done');
                else if(idx === currentAnimStep) s.classList.add('active');
            });
        }, 1000); // Progress exactly every 1000ms
        
        // Add timeout: 5 minutes max for upload
        const timeoutId = setTimeout(() => {
            uploadAbortController.abort();
            throw new Error('Upload timeout. The file may be too large or connection is slow. Try again.');
        }, 5 * 60 * 1000);
        
        const response = await fetch('/api/upload', { 
            method: 'POST', 
            body: formData,
            signal: uploadAbortController.signal 
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Upload failed' }));
            throw new Error(errData.detail || 'Upload failed');
        }
        const data = await response.json();
        pollJobStatus(data.job_id);
    } catch (err) {
        if(animInterval) clearInterval(animInterval);
        if (err.name === 'AbortError') {
            showError('Upload cancelled or timed out.');
        } else {
            showError(err.message || 'Upload failed. Please try again.');
        }
        progressContainer.style.display = 'none';
        uploadBtn.style.display = 'inline-flex';
        uploadBtn.disabled = false;
        uploadAbortController = null;
    }
}

function pollJobStatus(jobId) {
    let attempts = 0;
    const maxAttempts = 120; // 2 minutes max polling
    const poll = async () => {
        try {
            const res = await fetch(`/api/jobs/${jobId}`, {
                signal: AbortSignal.timeout(5000) // 5 second timeout per request
            });
            
            if (!res.ok) throw new Error('Failed to check status');
            const data = await res.json();
            
            if (data.status === 'completed' || data.status === 'complete') {
                const checkReady = setInterval(() => {
                    if (currentAnimStep >= 2) {
                        clearInterval(checkReady);
                        if(animInterval) clearInterval(animInterval);
                        
                        const steps = [document.getElementById('step1'), document.getElementById('step2'), document.getElementById('step3'), document.getElementById('step4')];
                        steps.forEach(s => { s.className = 'step done'; });
                        
                        setTimeout(() => {
                            window.location.href = `/static/results.html?job_id=${jobId}`;
                        }, 500);
                    }
                }, 200);
                return;
            }
            if (data.status === 'failed') throw new Error(data.error || 'Analysis failed');

            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(poll, 1000);
            } else {
                throw new Error('Analysis is taking too long. Please check back in a moment.');
            }
        } catch (err) {
            if(animInterval) clearInterval(animInterval);
            showError(err.message || 'Failed to get analysis results');
            progressContainer.style.display = 'none';
            uploadBtn.style.display = 'inline-flex';
            uploadBtn.disabled = false;
        }
    };
    poll();
}







function resetUpload() {
    selectedFileData = null;
    fileInput.value = '';
    previewImage.src = '';
    dropZoneContent.style.display = 'block';
    selectedFile.style.display = 'none';
    uploadBtn.style.display = 'none';
    uploadBtn.disabled = false;
    progressContainer.style.display = 'none';
    hideError();
}
function showError(m) { errorMessage.textContent = m; errorMessage.style.display = 'block'; }
function hideError() { errorMessage.style.display = 'none'; }
function formatFileSize(b) { return b === 0 ? '0 B' : (b/Math.pow(1024, Math.floor(Math.log(b)/Math.log(1024)))).toFixed(2) + ' ' + ['B','KB','MB','GB'][Math.floor(Math.log(b)/Math.log(1024))]; }
