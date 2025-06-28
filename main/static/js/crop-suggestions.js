console.log('🌾 Crop Suggestions JavaScript loaded successfully!');

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 Initializing crop suggestions page...');
    initializeFormEnhancements();
    addSubmitButtonEnhancement();
    console.log('✅ Crop suggestions page ready!');
});

// Form enhancements
function initializeFormEnhancements() {
    addSeasonalGuidance();
    addBudgetGuidance();
    addIrrigationGuidance();

    // Trigger help text on page load if values are already set
    const seasonSelect = document.querySelector('[name="season"]');
    if (seasonSelect && seasonSelect.value) {
        seasonSelect.dispatchEvent(new Event('change'));
    }
    const budgetSelect = document.querySelector('[name="budget"]');
    if (budgetSelect && budgetSelect.value) {
        budgetSelect.dispatchEvent(new Event('change'));
    }
    const irrigationSelect = document.querySelector('[name="irrigation"]');
    if (irrigationSelect && irrigationSelect.value) {
        irrigationSelect.dispatchEvent(new Event('change'));
    }
}

// Add seasonal guidance
function addSeasonalGuidance() {
    const seasonSelect = document.querySelector('[name="season"]');
    if (seasonSelect) {
        seasonSelect.addEventListener('change', function() {
            const season = this.value;
            const helpTexts = {
                'kharif': '🌧️ Monsoon season (June-October): Best for rice, cotton, sugarcane, maize',
                'rabi': '❄️ Winter season (November-April): Perfect for wheat, barley, peas, mustard',
                'zaid': '☀️ Summer season (April-June): Suitable for watermelon, cucumber, fodder crops'
            };
            showSeasonHelp(helpTexts[season] || '');
        });
    }
}

// Add budget guidance
function addBudgetGuidance() {
    const budgetSelect = document.querySelector('[name="budget"]');
    if (budgetSelect) {
        budgetSelect.addEventListener('change', function() {
            const budget = this.value;
            const helpTexts = {
                'low': '💰 Low budget: Focus on low-input, high-yield traditional crops',
                'medium': '💸 Medium budget: Balance of investment and returns with improved varieties',
                'high': '💎 High budget: Premium crops with advanced techniques and higher profits'
            };
            showBudgetHelp(helpTexts[budget] || '');
        });
    }
}

// Add irrigation guidance
function addIrrigationGuidance() {
    const irrigationSelect = document.querySelector('[name="irrigation"]');
    if (irrigationSelect) {
        irrigationSelect.addEventListener('change', function() {
            const irrigation = this.value;
            const helpTexts = {
                'rainfed': '🌧️ Rain-dependent: Choose drought-resistant crops like millet, sorghum',
                'drip': '💧 Drip irrigation: Ideal for water-efficient crops like vegetables, fruits',
                'sprinkler': '🚿 Sprinkler system: Good for field crops like wheat, maize, pulses'
            };
            showIrrigationHelp(helpTexts[irrigation] || '');
        });
    }
}

// Show help functions
function showSeasonHelp(helpText) {
    showDynamicHelp('season', helpText, 'fas fa-calendar-alt');
}

function showBudgetHelp(helpText) {
    showDynamicHelp('budget', helpText, 'fas fa-rupee-sign');
}

function showIrrigationHelp(helpText) {
    showDynamicHelp('irrigation', helpText, 'fas fa-tint');
}

// Generic dynamic help function
function showDynamicHelp(fieldName, helpText, iconClass) {
    if (!helpText) return;

    const field = document.querySelector(`[name="${fieldName}"]`);
    if (!field) return;

    // Remove existing help
    const existingHelp = field.parentNode.querySelector('.dynamic-help');
    if (existingHelp) {
        existingHelp.remove();
    }

    // Add new help
    const helpDiv = document.createElement('div');
    helpDiv.className = 'dynamic-help';
    helpDiv.innerHTML = `
        <div class="help-content">
            <i class="${iconClass} me-2"></i>
            <span>${helpText}</span>
        </div>
    `;

    field.parentNode.appendChild(helpDiv);

    // Animate in
    setTimeout(() => helpDiv.classList.add('show'), 100);
}

// Enhanced submit button
function addSubmitButtonEnhancement() {
    const form = document.querySelector('form[method="post"]');
    const submitBtn = form ? form.querySelector('button[type="submit"]') : null;

    if (form && submitBtn) {
        const originalText = submitBtn.innerHTML;

        form.addEventListener('submit', function(e) {
            // Add loading state
            submitBtn.innerHTML = '<i class="fas fa-seedling fa-spin me-2"></i>Generating Your Personalized Crop Recommendations...';
            submitBtn.disabled = true;
            submitBtn.classList.add('loading');

            // Add form validation
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                    field.classList.add('is-valid');
                }
            });

            if (!isValid) {
                e.preventDefault();
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                submitBtn.classList.remove('loading');
                showNotification('Please fill in all required fields', 'error');
                return false;
            }

            // Show progress messages
            setTimeout(() => {
                if (submitBtn.disabled) {
                    submitBtn.innerHTML = '<i class="fas fa-brain fa-pulse me-2"></i>AI is analyzing your farm conditions...';
                }
            }, 2000);

            setTimeout(() => {
                if (submitBtn.disabled) {
                    submitBtn.innerHTML = '<i class="fas fa-chart-line fa-pulse me-2"></i>Calculating optimal crop recommendations...';
                }
            }, 4000);
        });
    }
}

// CLEAN LOCATION DETECTION - BACKEND ONLY
window.detectMyLocation = function() {
    console.log('🔍 Location detection requested');

    if (!navigator.geolocation) {
        showNotification('Geolocation is not supported by this browser', 'error');
        return;
    }

    const btn = document.getElementById('detectLocationBtn');
    if (!btn) {
        console.error('❌ Location button not found');
        return;
    }

    const originalContent = btn.innerHTML;

    // Show loading state
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Detecting...';
    btn.disabled = true;

    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy;
            
            console.log(`📍 Location detected: ${lat}, ${lon} (accuracy: ${accuracy}m)`);

            // Update button to show address lookup
            btn.innerHTML = '<i class="fas fa-search me-2"></i>Finding Address...';

            // Call Django backend for reverse geocoding (ONLY THIS!)
            const backendUrl = `/api/reverse-geocode/?lat=${lat}&lon=${lon}`;
            
            fetch(backendUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('🏠 Backend response:', data);
                
                if (data.success && data.address) {
                    // FIXED: Extract individual values properly
                    const city = data.address.city || '';
                    const state = data.address.state || '';
                    const country = data.address.country || 'India';
                    
                    console.log(`✅ Extracted values: city="${city}", state="${state}", country="${country}"`);
                    
                    // Fill form fields with individual string values
                    fillLocationFields(city, state, country);
                    
                    // Show success message
                    btn.innerHTML = '<i class="fas fa-check-circle me-2"></i>Location Found!';
                    btn.classList.add('success');
                    
                    showNotification(
                        `📍 Location: ${city}, ${state}, ${country}<br>
                         📡 Source: ${data.address.source}<br>
                         🎯 Accuracy: ${Math.round(accuracy)}m`, 
                        'success'
                    );
                    
                    // Reset button after 3 seconds
                    setTimeout(() => {
                        resetLocationButton(btn, originalContent);
                    }, 3000);
                    
                } else {
                    console.error('❌ Backend reverse geocoding failed:', data.error || 'Unknown error');
                    showNotification(data.error || 'Could not determine your exact location. Please enter manually.', 'error');
                    resetLocationButton(btn, originalContent);
                }
            })
            .catch(error => {
                console.error('❌ Reverse geocoding error:', error);
                showNotification('Could not resolve location. Please enter manually.', 'error');
                resetLocationButton(btn, originalContent);
            });
        },
        function(error) {
            console.error('❌ Geolocation error:', error);
            resetLocationButton(btn, originalContent);
            
            let errorMessage = '';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage = '🚫 Location access denied. Please allow location access and try again.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage = '📍 Location information is unavailable. Please check your GPS/internet connection.';
                    break;
                case error.TIMEOUT:
                    errorMessage = '⏱️ Location request timed out. Please try again or enter location manually.';
                    break;
                default:
                    errorMessage = '❓ An unknown error occurred while detecting location.';
                    break;
            }
            showNotification(errorMessage, 'error');
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
};

// FIXED: Fill location fields with individual string parameters
function fillLocationFields(city, state, country) {
    console.log(`🏠 Filling location fields: city="${city}", state="${state}", country="${country}"`);
    
    const cityField = document.querySelector('[name="location"]');
    const stateField = document.querySelector('[name="state"]');
    const countryField = document.querySelector('[name="country"]');

    if (cityField && city) {
        cityField.value = String(city);
        cityField.dispatchEvent(new Event('input'));
        console.log(`✅ City field filled: ${cityField.value}`);
    }
    
    if (stateField && state) {
        stateField.value = String(state);
        stateField.dispatchEvent(new Event('input'));
        console.log(`✅ State field filled: ${stateField.value}`);
    }

    if (countryField && country) {
        // Find matching option in dropdown
        let optionFound = false;
        for (let i = 0; i < countryField.options.length; i++) {
            if (countryField.options[i].value === country || 
                countryField.options[i].text === country) {
                countryField.value = countryField.options[i].value;
                optionFound = true;
                console.log(`✅ Country field filled: ${countryField.value}`);
                break;
            }
        }
        
        // Default to India if country not found in dropdown
        if (!optionFound) {
            countryField.value = 'India';
            console.log(`⚠️ Country not found in dropdown, defaulted to India`);
        }
        
        countryField.dispatchEvent(new Event('change'));
    }
}

function resetLocationButton(btn, originalContent) {
    btn.innerHTML = originalContent;
    btn.disabled = false;
    btn.classList.remove('success', 'detecting');
}

// Enhanced notification system with HTML support
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} notification-modern`;
    
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
        </div>
        <div class="notification-content">
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);

    // Auto remove
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }
    }, type === 'error' ? 8000 : 6000);
}

// Report Action Functions
window.printReport = function() {
    window.print();
};

window.newAnalysis = function() {
    if (confirm('Start a new crop analysis? This will clear the current results.')) {
        window.location.reload();
    }
};

window.contactExpert = function() {
    const expertModal = new bootstrap.Modal(document.getElementById('expertModal'));
    expertModal.show();
};

window.shareResults = function() {
    const shareModal = new bootstrap.Modal(document.getElementById('shareModal'));
    shareModal.show();
};

window.downloadReport = function(format) {
    const btn = event.target;
    const originalContent = btn.innerHTML;
    
    // Show loading state
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
    btn.disabled = true;
    
    // Create form and submit
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/download-report/';
    
    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
    
    // Add format
    const formatInput = document.createElement('input');
    formatInput.type = 'hidden';
    formatInput.name = 'format';
    formatInput.value = format;
    form.appendChild(formatInput);
    
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
    
    // Reset button after delay
    setTimeout(() => {
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }, 3000);
    
    showNotification(`📥 ${format.toUpperCase()} report is being generated and will download shortly!`, 'success');
};

window.submitExpertContact = function() {
    const form = document.getElementById('expertContactForm');
    const formData = new FormData(form);
    
    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch('/contact-expert/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('expertModal')).hide();
            form.reset();
        } else {
            showNotification(data.error || 'Failed to send request', 'error');
        }
    })
    .catch(error => {
        showNotification('Failed to contact expert. Please try again.', 'error');
    });
};

window.generateShareLink = function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/share-results/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `csrfmiddlewaretoken=${csrfToken}&share_method=link`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('generatedLink').value = data.share_link;
            document.getElementById('shareLink').style.display = 'block';
            showNotification(data.message, 'success');
        } else {
            showNotification(data.error || 'Failed to generate share link', 'error');
        }
    })
    .catch(error => {
        showNotification('Failed to generate share link', 'error');
    });
};

window.copyShareLink = function() {
    const linkInput = document.getElementById('generatedLink');
    linkInput.select();
    document.execCommand('copy');
    showNotification('📋 Share link copied to clipboard!', 'success');
};

// Export for global use
window.cropSuggestions = {
    showNotification,
    showDynamicHelp
};

console.log('🚀 Crop suggestions JavaScript fully loaded!');