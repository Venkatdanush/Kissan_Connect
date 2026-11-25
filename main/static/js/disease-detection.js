/* 
 * Disease Detection JavaScript Module
 * Handles image upload, camera capture, and AI analysis
 */

class DiseaseDetection {
    constructor() {
        this.currentStream = null;
        this.uploadZone = document.getElementById('uploadZone');
        this.imageInput = document.getElementById('imageInput');
        this.previewImg = document.getElementById('previewImg');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.resultsSection = document.getElementById('resultsSection');
        
        this.initializeEventListeners();
        this.initializeDragDrop();
    }

    initializeEventListeners() {
        // File input change event
        this.imageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleImageSelection(file);
            }
        });

        // Form submission
        document.getElementById('diseaseDetectionForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeImage();
        });

        // Camera modal events
        document.getElementById('cameraModal').addEventListener('hidden.bs.modal', () => {
            this.stopCamera();
        });
    }

    initializeDragDrop() {
        // Drag and drop events
        this.uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadZone.classList.add('dragover');
        });

        this.uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadZone.classList.remove('dragover');
        });

        this.uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (this.validateImageFile(file)) {
                    this.imageInput.files = files;
                    this.handleImageSelection(file);
                }
            }
        });
    }

    validateImageFile(file) {
        // Check file type
        if (!file.type.startsWith('image/')) {
            this.showAlert('Please select a valid image file.', 'error');
            return false;
        }

        // Check file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showAlert('File size must be less than 10MB.', 'error');
            return false;
        }

        return true;
    }

    handleImageSelection(file) {
        if (!this.validateImageFile(file)) {
            return;
        }

        // Create image preview
        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImg.src = e.target.result;
            document.getElementById('uploadContent').style.display = 'none';
            document.getElementById('imagePreview').style.display = 'block';
            this.analyzeBtn.disabled = false;
            
            // Add success state to upload zone
            this.uploadZone.classList.add('success');
            this.uploadZone.classList.remove('error', 'processing');
        };
        reader.readAsDataURL(file);
    }

    removeImage() {
        this.imageInput.value = '';
        document.getElementById('uploadContent').style.display = 'block';
        document.getElementById('imagePreview').style.display = 'none';
        this.analyzeBtn.disabled = true;
        this.resultsSection.style.display = 'none';
        
        // Reset upload zone state
        this.uploadZone.classList.remove('success', 'error', 'processing');
    }

    async openCamera() {
        try {
            const modal = new bootstrap.Modal(document.getElementById('cameraModal'));
            modal.show();
            
            this.currentStream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'environment' // Use back camera on mobile
                } 
            });
            
            document.getElementById('cameraVideo').srcObject = this.currentStream;
        } catch (err) {
            console.error('Error accessing camera:', err);
            this.showAlert('Unable to access camera. Please check permissions and try again.', 'error');
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('cameraModal'));
            if (modal) modal.hide();
        }
    }

    capturePhoto() {
        const video = document.getElementById('cameraVideo');
        const canvas = document.getElementById('cameraCanvas');
        const context = canvas.getContext('2d');
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob((blob) => {
            const file = new File([blob], 'captured-plant.jpg', { type: 'image/jpeg' });
            
            // Create a FileList-like object
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            this.imageInput.files = dataTransfer.files;
            
            this.handleImageSelection(file);
            this.stopCamera();
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('cameraModal'));
            if (modal) modal.hide();
            
            this.showAlert('Photo captured successfully!', 'success');
        }, 'image/jpeg', 0.8);
    }

    stopCamera() {
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => {
                track.stop();
            });
            this.currentStream = null;
        }
    }

    async analyzeImage() {
        if (!this.imageInput.files[0]) {
            this.showAlert('Please select an image first.', 'error');
            return;
        }

        // Show loading overlay
        this.showLoading(true);
        this.uploadZone.classList.add('processing');

        // Update loading text progressively
        const loadingTexts = [
            'Processing image with AI...',
            'Analyzing plant features...',
            'Identifying disease patterns...',
            'Consulting agricultural database...',
            'Generating treatment recommendations...',
            'Finalizing analysis...'
        ];
        
        let textIndex = 0;
        const textInterval = setInterval(() => {
            if (textIndex < loadingTexts.length) {
                document.getElementById('loadingText').textContent = loadingTexts[textIndex];
                textIndex++;
            }
        }, 1500);

        try {
            // Prepare form data
            const formData = new FormData();
            formData.append('plant_image', this.imageInput.files[0]);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

            // Submit to backend
            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            clearInterval(textInterval);
            this.showLoading(false);
            
            if (data.success) {
                this.displayResults(data);
                this.uploadZone.classList.remove('processing');
                this.uploadZone.classList.add('success');
            } else {
                this.showAlert('Error: ' + (data.error || 'Failed to analyze image. Please try again.'), 'error');
                this.uploadZone.classList.remove('processing');
                this.uploadZone.classList.add('error');
            }
        } catch (error) {
            clearInterval(textInterval);
            this.showLoading(false);
            console.error('Error:', error);
            this.showAlert('Network error. Please check your connection and try again.', 'error');
            this.uploadZone.classList.remove('processing');
            this.uploadZone.classList.add('error');
        }
    }

    displayResults(data) {
        const resultsHtml = this.generateResultsHTML(data);
        document.getElementById('analysisResults').innerHTML = resultsHtml;
        this.resultsSection.style.display = 'block';
        
        // Smooth scroll to results
        this.resultsSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });

        // Animate confidence bar
        setTimeout(() => {
            const confidenceBar = document.querySelector('.confidence-fill');
            if (confidenceBar) {
                const confidence = confidenceBar.dataset.confidence;
                confidenceBar.style.width = confidence + '%';
            }
        }, 500);

        // Show success notification
        this.showAlert('Analysis completed successfully!', 'success');
    }

    generateResultsHTML(data) {
        const isHealthy = data.disease_type === 'Healthy' || data.confidence < 50;
        const cardClass = isHealthy ? 'healthy-result-card' : 'disease-result-card';
        const badgeClass = isHealthy ? 'healthy-badge' : 'disease-badge';
        const iconClass = isHealthy ? 'fa-check-circle' : 'fa-exclamation-triangle';
        const iconColor = isHealthy ? 'text-success' : 'text-danger';

        return `
            <div class="disease-result-card ${cardClass}">
                <div class="d-flex align-items-center mb-3">
                    <i class="fas ${iconClass} ${iconColor} fa-2x me-3"></i>
                    <div>
                        <h3 class="mb-1">Analysis Complete</h3>
                        <small class="text-muted">AI-powered plant health assessment</small>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <span class="${badgeClass}">
                                <i class="fas ${iconClass} me-2"></i>
                                ${data.disease_type || 'Unknown'}
                            </span>
                        </div>
                        
                        <h5>Confidence Level</h5>
                        <div class="confidence-bar">
                            <div class="confidence-fill" data-confidence="${data.confidence || 0}" style="width: 0%;"></div>
                        </div>
                        <p class="text-muted mb-4">${data.confidence || 0}% confidence</p>

                        ${data.description ? `
                        <h5>Description</h5>
                        <p class="text-muted">${data.description}</p>
                        ` : ''}
                    </div>
                    
                    <div class="col-md-6">
                        <img src="${this.previewImg.src}" 
                             class="img-fluid rounded shadow-sm" 
                             alt="Analyzed plant image"
                             style="max-height: 300px; width: 100%; object-fit: cover;">
                    </div>
                </div>

                ${data.remedies ? `
                <div class="remedy-section">
                    <h5 class="mb-3">
                        <i class="fas fa-prescription-bottle-alt text-primary me-2"></i>
                        Treatment Recommendations
                    </h5>
                    <div class="remedy-content">
                        ${data.remedies}
                    </div>
                </div>
                ` : ''}

                <div class="mt-4 d-flex gap-2 flex-wrap">
                    <button class="btn btn-primary" onclick="diseaseDetector.analyzeAnother()">
                        <i class="fas fa-redo me-2"></i>Analyze Another Image
                    </button>
                    <button class="btn btn-outline-primary" onclick="diseaseDetector.downloadReport()">
                        <i class="fas fa-download me-2"></i>Download Report
                    </button>
                    <button class="btn btn-outline-success" onclick="diseaseDetector.shareResults()">
                        <i class="fas fa-share-alt me-2"></i>Share Results
                    </button>
                </div>
            </div>
        `;
    }

    analyzeAnother() {
        this.removeImage();
        document.querySelector('.disease-hero-section').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }

    downloadReport() {
        this.showAlert('Report download functionality will be implemented.', 'info');
    }

    shareResults() {
        if (navigator.share) {
            navigator.share({
                title: 'Plant Disease Analysis - Kissan Connect',
                text: 'Check out my plant health analysis results!',
                url: window.location.href
            });
        } else {
            // Fallback for browsers without Web Share API
            const url = window.location.href;
            navigator.clipboard.writeText(url).then(() => {
                this.showAlert('Results link copied to clipboard!', 'success');
            }).catch(() => {
                this.showAlert('Unable to copy link to clipboard.', 'error');
            });
        }
    }

    showLoading(show) {
        if (show) {
            this.loadingOverlay.classList.add('active');
            this.analyzeBtn.classList.add('loading');
            this.analyzeBtn.disabled = true;
        } else {
            this.loadingOverlay.classList.remove('active');
            this.analyzeBtn.classList.remove('loading');
            this.analyzeBtn.disabled = false;
        }
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = `
            top: 100px; 
            right: 20px; 
            z-index: 9999; 
            min-width: 300px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            border: none;
            border-radius: 10px;
        `;
        
        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        alertDiv.innerHTML = `
            <i class="fas ${iconMap[type]} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Global functions for HTML onclick events
let diseaseDetector;

function openCamera() {
    diseaseDetector.openCamera();
}

function capturePhoto() {
    diseaseDetector.capturePhoto();
}

function removeImage() {
    diseaseDetector.removeImage();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 1000,
            once: true,
            offset: 100
        });
    }
    
    // Initialize disease detection
    diseaseDetector = new DiseaseDetection();
    
    console.log('🔬 Disease Detection System Initialized');
});
