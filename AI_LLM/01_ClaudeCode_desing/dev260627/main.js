'use strict';

// Header: scroll state
const header = document.getElementById('site-header');
const onScroll = () => {
  header.classList.toggle('scrolled', window.scrollY > 60);
};
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Reveal on scroll (IntersectionObserver)
const revealItems = document.querySelectorAll('.reveal, .reveal-stagger');
if (revealItems.length && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -48px 0px' });
  revealItems.forEach(el => observer.observe(el));
} else {
  // Fallback: show all immediately
  revealItems.forEach(el => el.classList.add('is-visible'));
}

// Mobile nav toggle
const navToggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('.nav');
if (navToggle && nav) {
  navToggle.addEventListener('click', () => {
    const expanded = navToggle.getAttribute('aria-expanded') === 'true';
    navToggle.setAttribute('aria-expanded', String(!expanded));
    nav.classList.toggle('is-open', !expanded);
    document.body.style.overflow = expanded ? '' : 'hidden';
  });

  // Close on nav link click
  nav.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', () => {
      navToggle.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
      document.body.style.overflow = '';
    });
  });

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && nav.classList.contains('is-open')) {
      navToggle.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
      document.body.style.overflow = '';
      navToggle.focus();
    }
  });
}

// Form submission (demo — no actual backend)
const form = document.querySelector('.contact__form');
if (form) {
  form.addEventListener('submit', e => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    btn.textContent = 'Sent — we will be in touch shortly.';
    btn.disabled = true;
    btn.style.opacity = '0.6';
  });
}

// Smooth reveal for hero (initial load)
document.addEventListener('DOMContentLoaded', () => {
  const heroContent = document.querySelector('.hero .reveal');
  if (heroContent) {
    setTimeout(() => heroContent.classList.add('is-visible'), 200);
  }
});
