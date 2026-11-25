/**
 * KissanConnect AI Assistant Router
 * Redirects all chatbot triggers to the dedicated ChatGPT-style interface (/chat/)
 */

window.openChatbot = function() {
    window.location.href = '/chat/';
};

console.log('🤖 Kissan Sahayak dedicated chat router active (/chat/)');
