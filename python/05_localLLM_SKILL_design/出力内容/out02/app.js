// JavaScript for Scroll Reveal Animation
const revealElements = document.querySelectorAll('.reveal');

const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1 // Element must be 10% visible to trigger
};

const observerCallback = (entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // Trigger the reveal class
            entry.target.classList.add('reveal');
            // Stop observing once revealed
            observer.unobserve(entry.target);
        }
    });
};

const observer = new IntersectionObserver(observerCallback, observerOptions);

// Initialize observation for all elements marked with .reveal
revealElements.forEach(el => {
    // Special handling for the Hero content which needs immediate (but animated) reveal
    if (el.closest('#hero')) {
        setTimeout(() => {
            el.classList.add('reveal');
        }, 100); // Small delay to ensure CSS transition fires on load
    } else {
        observer.observe(el);
    }
});