
// ==================================================
// JAVASCRIPT IMPLEMENTATIONS
// ==================================================

/**
 * 1. Header Sticky & Scroll Effect
 */
const header = document.getElementById('site-header');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});


/**
 * 2. Intersection Observer for Scroll Animation Reveal
 */
const revealElements = document.querySelectorAll('.reveal');

const observerOptions = {
    root: null, // viewport
    rootMargin: '0px',
    threshold: 0.12 // Trigger when 12% visible (as per spec)
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            // Stop observing once revealed to prevent re-triggering
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

revealElements.forEach(el => {
    // Minor adjustment for initial reveal on load
    if (el.closest('#hero') === null) {
        observer.observe(el);
    }
});


/**
 * 3. Mobile Navigation Toggle (Hamburger Menu)
 */
const menuToggle = document.querySelector('.menu-toggle');
const navLinks = document.getElementById('main-navigation');
const body = document.body;

function toggleMenu() {
    const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true' ? false : true;
    menuToggle.setAttribute('aria-expanded', isExpanded);
    navLinks.style.display = isExpanded ? 'flex' : 'none';
    body.classList.toggle('menu-open', isExpanded);

    if (isExpanded) {
        // Focus management for accessibility
        navLinks.querySelector('a').focus();
    } else {
        menuToggle.focus();
    }
}

menuToggle.addEventListener('click', toggleMenu);

// Close menu when a link is clicked (essential for SPA-like navigation)
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        if (window.innerWidth <= 900) {
            toggleMenu(); // Closes the menu on click
        }
    });
});

// Close menu on ESC key press
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && body.classList.contains('menu-open')) {
        toggleMenu();
    }
});


/**
 * 4. Form Submission Demo
 */
function handleFormSubmit(event) {
    event.preventDefault();
    const submitButton = event.target.querySelector('.btn');

    // Simulate loading state and success message
    submitButton.textContent = '送信中...';
    submitButton.disabled = true;

    setTimeout(() => {
        alert('予約情報を受信しました。担当者より24時間以内に折り返しご連絡いたします。\n（これはデモです）');
        // Reset button state after success
        submitButton.textContent = '予約を申し込む';
        submitButton.disabled = false;
        event.target.reset(); // Clear the form fields
    }, 1500);
}
