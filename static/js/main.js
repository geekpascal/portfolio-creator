<!-- static/js/main.js -->
document.addEventListener('DOMContentLoaded', (event) => {
    // Navigation scroll effect
    const nav = document.getElementById('main-nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 10) {
            nav.classList.add('bg-white', 'shadow-md');
        } else {
            nav.classList.remove('bg-white', 'shadow-md');
        }
    });

    // Animate elements on scroll
    const animateElements = document.querySelectorAll('.animate-element');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                anime({
                    targets: entry.target,
                    opacity: 1,
                    translateY: 0,
                    duration: 600,
                    easing: 'easeOutCubic'
                });
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    animateElements.forEach(element => {
        observer.observe(element);
    });

    // Initialize Lucide icons
    lucide.createIcons();
});