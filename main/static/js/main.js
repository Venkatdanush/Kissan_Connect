/* filepath: f:\ohooo\projects\kissanconnect\main\static\js\main.js */
// Kissan Connect Enhanced JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🌱 Kissan Connect loaded successfully!');
    
    // Initialize AOS (Animate On Scroll)
    AOS.init({
        duration: 1000,
        easing: 'ease-in-out',
        once: true,
        offset: 100
    });
    
    // Smooth scrolling for navigation links
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
    
    // Navbar transparency on scroll
    window.addEventListener('scroll', function() {
        const navbar = document.getElementById('mainNavbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // ===== COUNTER ANIMATION FUNCTION =====
    // ENHANCED COUNTER ANIMATION - GUARANTEED TO WORK! 🚀
    function animateCounters() {
        const counters = document.querySelectorAll('.stat-number-modern[data-target]');
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            const duration = 2000; // 2 seconds
            const increment = target / (duration / 16); // 60fps
            let current = 0;
            
            const updateCounter = () => {
                if (current < target) {
                    current += increment;
                    if (current > target) current = target;
                    
                    // Format numbers with K, M suffixes
                    let displayValue = Math.floor(current);
                    if (target >= 1000 && target < 1000000) {
                        if (Math.floor(current) >= 1000) {
                            displayValue = (Math.floor(current / 100) / 10).toFixed(1) + 'K';
                            if (displayValue.endsWith('.0K')) {
                                displayValue = Math.floor(current / 1000) + 'K';
                            }
                        }
                    } else if (target >= 1000000) {
                        if (Math.floor(current) >= 1000000) {
                            displayValue = (Math.floor(current / 100000) / 10).toFixed(1) + 'M';
                            if (displayValue.endsWith('.0M')) {
                                displayValue = Math.floor(current / 1000000) + 'M';
                            }
                        }
                    }
                    
                    counter.textContent = displayValue;
                    requestAnimationFrame(updateCounter);
                } else {
                    // Final formatting
                    let finalValue;
                    if (target >= 1000 && target < 1000000) {
                        finalValue = (target / 1000) + 'K';
                        if (finalValue.endsWith('.0K')) {
                            finalValue = (target / 1000).toString() + 'K';
                        }
                    } else if (target >= 1000000) {
                        finalValue = (target / 1000000) + 'M';
                        if (finalValue.endsWith('.0M')) {
                            finalValue = (target / 1000000).toString() + 'M';
                        }
                    } else {
                        finalValue = target.toString();
                    }
                    counter.textContent = finalValue;
                }
            };
            
            updateCounter();
        });
    }
    
    // BETTER INTERSECTION OBSERVER 
    document.addEventListener('DOMContentLoaded', function() {
        const observerOptions = {
            threshold: 0.3,
            rootMargin: '0px 0px -50px 0px'
        };

        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Start animation when stats section is visible
                    setTimeout(() => {
                        animateCounters();
                    }, 300);
                    // Stop observing after animation starts
                    counterObserver.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe stats section
        const statsSection = document.querySelector('.stats-section-modern');
        if (statsSection) {
            counterObserver.observe(statsSection);
            console.log('✅ Stats observer set up successfully!');
        } else {
            console.log('❌ Stats section not found!');
        }
    });

    // FALLBACK - Manual trigger after 3 seconds if intersection observer fails
    setTimeout(() => {
        const counters = document.querySelectorAll('.stat-number-modern[data-target]');
        if (counters.length > 0 && counters[0].textContent === '0') {
            console.log('🔄 Triggering fallback animation...');
            animateCounters();
        }
    }, 3000);
    
    // ===== CHATBOT FUNCTIONALITY =====
    function openChatbot() {
        // Create chatbot overlay
        const chatOverlay = document.createElement('div');
        chatOverlay.className = 'chatbot-overlay';
        chatOverlay.innerHTML = `
            <div class="chatbot-container">
                <div class="chatbot-header">
                    <div class="chatbot-title">
                        <i class="fas fa-robot me-2"></i>
                        AI Farm Assistant
                    </div>
                    <button class="chatbot-close" onclick="closeChatbot()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="chatbot-messages" id="chatbotMessages">
                    <div class="message bot-message">
                        <div class="message-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-content">
                            Hello! I'm your AI Farm Assistant. How can I help you today?
                            <br><br>
                            You can ask me about:
                            <ul>
                                <li>Crop recommendations</li>
                                <li>Disease identification</li>
                                <li>Weather advice</li>
                                <li>Farming best practices</li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="chatbot-input">
                    <input type="text" id="chatbotInput" placeholder="Type your message..." onkeypress="handleChatEnter(event)">
                    <button onclick="sendChatMessage()">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(chatOverlay);
        document.getElementById('chatbotInput').focus();
    }
    
    function closeChatbot() {
        const chatOverlay = document.querySelector('.chatbot-overlay');
        if (chatOverlay) {
            chatOverlay.remove();
        }
    }
    
    function handleChatEnter(event) {
        if (event.key === 'Enter') {
            sendChatMessage();
        }
    }
    
    function sendChatMessage() {
        const input = document.getElementById('chatbotInput');
        const message = input.value.trim();
        
        if (message) {
            addChatMessage(message, 'user');
            input.value = '';
            
            // Simulate AI response
            setTimeout(() => {
                const response = generateAIResponse(message);
                addChatMessage(response, 'bot');
            }, 1000);
        }
    }
    
    function addChatMessage(message, type) {
        const messagesContainer = document.getElementById('chatbotMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">${message}</div>
                <div class="message-avatar">
                    <i class="fas fa-user"></i>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">${message}</div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function generateAIResponse(userMessage) {
        const message = userMessage.toLowerCase();
        
        if (message.includes('crop') || message.includes('suggest')) {
            return "For crop recommendations, I'd need to know your location, soil type, and season. Our AI system analyzes multiple factors including weather patterns, soil conditions, and market prices to suggest the best crops for your farm.";
        } else if (message.includes('disease') || message.includes('pest')) {
            return "For disease detection, you can upload photos of affected plants through our Disease Detection feature. Our AI can identify over 200+ plant diseases and provide treatment recommendations including both organic and chemical solutions.";
        } else if (message.includes('weather')) {
            return "Our Weather Intelligence system provides real-time forecasts, severe weather alerts, and long-term climate predictions. You can access detailed weather information through the Weather section of our platform.";
        } else if (message.includes('price') || message.includes('market')) {
            return "Our Digital Marketplace allows you to set your own prices and connect directly with consumers. You'll get better prices compared to traditional middlemen, and can showcase your produce quality to build customer relationships.";
        } else {
            return "That's a great question! Our platform offers comprehensive AI-powered solutions for modern farming. You can explore our Services page to learn more about crop suggestions, weather intelligence, disease detection, and marketplace features. Is there a specific area you'd like to know more about?";
        }
    }
    
    // ===== FORM HANDLING =====
    document.addEventListener('DOMContentLoaded', function() {
        // Modern form labels animation
        const modernInputs = document.querySelectorAll('.form-control-modern');
        modernInputs.forEach(input => {
            // Check if input has value on load
            if (input.value.trim() !== '') {
                input.classList.add('has-value');
            }
            
            input.addEventListener('input', function() {
                if (this.value.trim() !== '') {
                    this.classList.add('has-value');
                } else {
                    this.classList.remove('has-value');
                }
            });
        });

        // Contact form submission
        const contactForm = document.getElementById('contactForm');
        if (contactForm) {
            contactForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Show loading state
                const submitBtn = this.querySelector('button[type="submit"]');
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Sending...';
                submitBtn.disabled = true;
                
                // Simulate form submission
                setTimeout(() => {
                    // Show success message
                    showNotification('Message sent successfully! We\'ll get back to you soon.', 'success');
                    
                    // Reset form
                    contactForm.reset();
                    
                    // Reset form labels
                    modernInputs.forEach(input => {
                        input.classList.remove('has-value');
                    });
                    
                    // Reset button
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 2000);
            });
        }
    });
    
    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    // Add floating chat button styles
    const chatBtnStyles = `
        .floating-chat-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #FF6B35, #DAA520);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(255, 107, 53, 0.4);
            transition: all 0.3s ease;
            z-index: 1000;
            animation: pulse 2s infinite;
        }
        
        .floating-chat-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 15px 40px rgba(255, 107, 53, 0.6);
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .particle {
            position: absolute;
            animation: particleFloat 6s linear infinite;
        }
        
        @keyframes particleFloat {
            0% {
                transform: translateY(100vh) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) rotate(360deg);
                opacity: 0;
            }
        }
    `;
    
    // Inject styles
    const styleSheet = document.createElement('style');
    styleSheet.textContent = chatBtnStyles;
    document.head.appendChild(styleSheet);
    
    // Feature tracking analytics (placeholder)
    function trackFeatureClick(featureName) {
        console.log(`Feature clicked: ${featureName}`);
        // Here you could send analytics data to your backend
    }
    
    // Add feature click tracking
    document.querySelectorAll('.feature-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const featureName = this.closest('.feature-card').querySelector('.feature-title').textContent;
            trackFeatureClick(featureName);
        });
    });
});

// Chatbot functionality
function openChatbot() {
    // Create chatbot overlay
    const chatOverlay = document.createElement('div');
    chatOverlay.className = 'chatbot-overlay';
    chatOverlay.innerHTML = `
        <div class="chatbot-container">
            <div class="chatbot-header">
                <div class="chatbot-title">
                    <i class="fas fa-robot me-2"></i>
                    AI Farm Assistant
                </div>
                <button class="chatbot-close" onclick="closeChatbot()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="chatbot-messages" id="chatbotMessages">
                <div class="message bot-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        Hello! I'm your AI Farm Assistant. How can I help you today?
                        <br><br>
                        You can ask me about:
                        <ul>
                            <li>Crop recommendations</li>
                            <li>Disease identification</li>
                            <li>Weather advice</li>
                            <li>Farming best practices</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="chatbot-input">
                <input type="text" id="chatbotInput" placeholder="Type your message..." onkeypress="handleChatEnter(event)">
                <button onclick="sendChatMessage()">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(chatOverlay);
    document.getElementById('chatbotInput').focus();
}

function closeChatbot() {
    const chatOverlay = document.querySelector('.chatbot-overlay');
    if (chatOverlay) {
        chatOverlay.remove();
    }
}

function handleChatEnter(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

function sendChatMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();
    
    if (message) {
        addChatMessage(message, 'user');
        input.value = '';
        
        // Simulate AI response
        setTimeout(() => {
            const response = generateAIResponse(message);
            addChatMessage(response, 'bot');
        }, 1000);
    }
}

function addChatMessage(message, type) {
    const messagesContainer = document.getElementById('chatbotMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    if (type === 'user') {
        messageDiv.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">${message}</div>
        `;
    }
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function generateAIResponse(userMessage) {
    const message = userMessage.toLowerCase();
    
    if (message.includes('crop') || message.includes('suggest')) {
        return "For crop recommendations, I'd need to know your location, soil type, and season. Our AI system analyzes multiple factors including weather patterns, soil conditions, and market prices to suggest the best crops for your farm.";
    } else if (message.includes('disease') || message.includes('pest')) {
        return "For disease detection, you can upload photos of affected plants through our Disease Detection feature. Our AI can identify over 200+ plant diseases and provide treatment recommendations including both organic and chemical solutions.";
    } else if (message.includes('weather')) {
        return "Our Weather Intelligence system provides real-time forecasts, severe weather alerts, and long-term climate predictions. You can access detailed weather information through the Weather section of our platform.";
    } else if (message.includes('price') || message.includes('market')) {
        return "Our Digital Marketplace allows you to set your own prices and connect directly with consumers. You'll get better prices compared to traditional middlemen, and can showcase your produce quality to build customer relationships.";
    } else {
        return "That's a great question! Our platform offers comprehensive AI-powered solutions for modern farming. You can explore our Services page to learn more about crop suggestions, weather intelligence, disease detection, and marketplace features. Is there a specific area you'd like to know more about?";
    }
}

// ===== FORM HANDLING =====
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Sending...';
            submitBtn.disabled = true;
            
            // Simulate form submission
            setTimeout(() => {
                // Show success message
                showNotification('Message sent successfully! We\'ll get back to you soon.', 'success');
                
                // Reset form
                contactForm.reset();
                
                // Reset button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }
});

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
            ${message}
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// ===== ADD THESE STYLES TO YOUR CSS =====
// Add chatbot and notification styles to your style.css
const additionalCSS = `
/* Chatbot Styles */
.chatbot-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease;
}

.chatbot-container {
    width: 90%;
    max-width: 500px;
    height: 70vh;
    background: var(--white);
    border-radius: 1rem;
    box-shadow: var(--shadow-2xl);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.chatbot-header {
    background: var(--primary-gradient);
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chatbot-title {
    font-weight: 600;
    font-size: 1.1rem;
}

.chatbot-close {
    background: none;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 50%;
    transition: var(--transition);
}

.chatbot-close:hover {
    background: rgba(255, 255, 255, 0.2);
}

.chatbot-messages {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    background: var(--gray-50);
}

.message {
    display: flex;
    margin-bottom: 1rem;
    gap: 0.75rem;
}

.bot-message {
    justify-content: flex-start;
}

.user-message {
    justify-content: flex-end;
}

.message-avatar {
    width: 35px;
    height: 35px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
    flex-shrink: 0;
}

.bot-message .message-avatar {
    background: var(--primary-gradient);
    color: white;
}

.user-message .message-avatar {
    background: var(--gray-600);
    color: white;
}

.message-content {
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: 1rem;
    line-height: 1.5;
}

.bot-message .message-content {
    background: var(--white);
    border-bottom-left-radius: 0.25rem;
}

.user-message .message-content {
    background: var(--primary-500);
    color: white;
    border-bottom-right-radius: 0.25rem;
}

.message-content ul {
    margin: 0.5rem 0;
    padding-left: 1.25rem;
}

.chatbot-input {
    padding: 1rem;
    background: var(--white);
    border-top: 1px solid var(--gray-200);
    display: flex;
    gap: 0.75rem;
}

.chatbot-input input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: 1px solid var(--gray-300);
    border-radius: 2rem;
    outline: none;
    transition: var(--transition);
}

.chatbot-input input:focus {
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.chatbot-input button {
    width: 45px;
    height: 45px;
    background: var(--primary-gradient);
    border: none;
    border-radius: 50%;
    color: white;
    cursor: pointer;
    transition: var(--transition);
    display: flex;
    align-items: center;
    justify-content: center;
}

.chatbot-input button:hover {
    transform: scale(1.05);
    box-shadow: var(--shadow-lg);
}

/* Notification Styles */
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--white);
    border-radius: 0.5rem;
    box-shadow: var(--shadow-lg);
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    z-index: 10000;
    animation: slideInRight 0.3s ease;
    max-width: 400px;
    border-left: 4px solid var(--primary-500);
}

.notification-success {
    border-left-color: #10b981;
}

.notification-content {
    flex: 1;
    color: var(--gray-700);
}

.notification-close {
    background: none;
    border: none;
    color: var(--gray-500);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 50%;
    transition: var(--transition);
}

.notification-close:hover {
    background: var(--gray-100);
    color: var(--gray-700);
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
`;

// Add the styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalCSS;
document.head.appendChild(styleSheet);