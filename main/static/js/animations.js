// filepath: Kissan_Connect/Kissan_Connect/main/static/js/animations.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS (Animate On Scroll) library
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true
    });

    // Smooth scrolling for anchor links
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
});