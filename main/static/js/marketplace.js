/**
 * Marketplace Enhancement JavaScript
 * Additional functionality for the marketplace
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize marketplace features
    initializeMarketplace();
});

function initializeMarketplace() {
    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading animation for product cards
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Add product card hover effects
    productCards.forEach(card => {
        const productImage = card.querySelector('.product-image');
        
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
            if (productImage) {
                productImage.style.transform = 'scale(1.1)';
            }
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            if (productImage) {
                productImage.style.transform = 'scale(1)';
            }
        });
    });

    // Add notification system
    window.showNotification = function(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 9999;
            min-width: 300px;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    };

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    
                    // Remove invalid class after user types
                    field.addEventListener('input', function() {
                        this.classList.remove('is-invalid');
                    }, { once: true });
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
    });

    // Add price formatting
    const priceElements = document.querySelectorAll('.price-tag, #totalAmount');
    priceElements.forEach(element => {
        const price = element.textContent.replace(/[^\d.]/g, '');
        if (price) {
            element.textContent = `₹${parseFloat(price).toLocaleString('en-IN', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 2
            })}`;
        }
    });

    // Add search highlighting
    const searchInput = document.getElementById('searchInput');
    if (searchInput && searchInput.value) {
        highlightSearchResults(searchInput.value);
    }

    // Add lazy loading for product images
    const productImages = document.querySelectorAll('.product-image');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        productImages.forEach(img => imageObserver.observe(img));
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl + K for search focus
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }

        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });

    // Add quick stats update
    updateMarketplaceStats();
}

function highlightSearchResults(searchTerm) {
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        const content = card.innerHTML;
        const highlightedContent = content.replace(
            new RegExp(`(${searchTerm})`, 'gi'),
            '<mark style="background: #fff3cd; padding: 2px 4px; border-radius: 3px;">$1</mark>'
        );
        card.innerHTML = highlightedContent;
    });
}

function updateMarketplaceStats() {
    const productCards = document.querySelectorAll('.product-card');
    const produceCount = document.querySelectorAll('[data-type="produce"]').length;
    const toolsCount = document.querySelectorAll('[data-type="tool"]').length;
    
    // Update stats display if elements exist
    const statsElements = document.querySelectorAll('.stats-number');
    if (statsElements.length > 0) {
        // Animate numbers
        statsElements.forEach(element => {
            const target = parseInt(element.dataset.target || element.textContent);
            animateNumber(element, target);
        });
    }
}

function animateNumber(element, target) {
    const start = 0;
    const duration = 2000;
    const startTime = performance.now();

    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (target - start) * easeOutExpo(progress));
        element.textContent = current.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }

    requestAnimationFrame(updateNumber);
}

function easeOutExpo(t) {
    return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
}

// Enhanced product modal functions
window.showProductDetails = function(productId) {
    // This would fetch product details and show in a modal
    console.log('Showing details for product:', productId);
    showNotification('Product details feature coming soon!', 'info');
};

window.addToWishlist = function(productId) {
    // Add to wishlist functionality
    console.log('Adding to wishlist:', productId);
    showNotification('Added to wishlist!', 'success');
};

window.shareProduct = function(productId, productName) {
    if (navigator.share) {
        navigator.share({
            title: productName,
            text: `Check out this product on Kissan Connect marketplace`,
            url: window.location.href
        });
    } else {
        // Fallback - copy to clipboard
        navigator.clipboard.writeText(window.location.href).then(() => {
            showNotification('Product link copied to clipboard!', 'success');
        });
    }
};

// Add CSS for notifications and enhancements
const style = document.createElement('style');
style.textContent = `
    .notification {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px;
        line-height: 1.4;
    }

    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .notification-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 5px;
        border-radius: 3px;
        margin-left: auto;
    }

    .notification-close:hover {
        background: rgba(255,255,255,0.2);
    }

    .product-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .product-image {
        transition: transform 0.3s ease;
    }

    .is-invalid {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
    }

    mark {
        background: #fff3cd !important;
        padding: 2px 4px !important;
        border-radius: 3px !important;
    }

    .product-image.loaded {
        opacity: 1;
        transform: scale(1);
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }

    /* Responsive enhancements */
    @media (max-width: 768px) {
        .notification {
            top: 10px;
            right: 10px;
            left: 10px;
            transform: translateY(-100%);
        }

        .notification.show {
            transform: translateY(0);
        }
    }
`;

document.head.appendChild(style);

console.log('🚀 Marketplace enhanced with additional features loaded!');
