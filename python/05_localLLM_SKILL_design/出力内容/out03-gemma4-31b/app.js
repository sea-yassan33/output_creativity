
        document.addEventListener('DOMContentLoaded', () => {
            // Hero fade-in
            setTimeout(() => {
                document.getElementById('hero-content').classList.add('is-visible');
            }, 200);

            // Header scroll effect
            const header = document.getElementById('main-header');
            window.addEventListener('scroll', () => {
                if (window.scrollY > 50) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            });

            // Intersection Observer for reveal animations
            const observerOptions = {
                threshold: 0.12
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                    }
                });
            }, observerOptions);

            document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

            // Mobile Nav Toggle
            const mobileToggle = document.querySelector('.mobile-toggle');
            const navLinks = document.querySelector('.nav-links');
            const body = document.body;

            const toggleMenu = () => {
                const expanded = mobileToggle.getAttribute('aria-expanded') === 'true' || false;
                mobileToggle.setAttribute('aria-expanded', !expanded);
                mobileToggle.classList.toggle('active');
                navLinks.classList.toggle('is-active');
                body.style.overflow = expanded ? 'auto' : 'hidden';
            };

            mobileToggle.addEventListener('click', toggleMenu);

            // Close menu on link click
            document.querySelectorAll('.nav-links a').forEach(link => {
                link.addEventListener('click', () => {
                    if (navLinks.classList.contains('is-active')) {
                        toggleMenu();
                    }
                });
            });

            // Esc key to close menu
            window.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && navLinks.classList.contains('is-active')) {
                    toggleMenu();
                }
            });

            // Form submit demo
            const form = document.getElementById('bookingForm');
            const submitBtn = document.getElementById('submitBtn');

            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const originalText = submitBtn.innerText;
                submitBtn.innerText = 'Sending...';
                submitBtn.disabled = true;
                
                setTimeout(() => {
                    submitBtn.innerText = 'Request Sent';
                    submitBtn.style.backgroundColor = '#4A5240';
                    submitBtn.style.borderColor = '#4A5240';
                    submitBtn.style.color = '#E8DCC8';
                    
                    setTimeout(() => {
                        submitBtn.innerText = originalText;
                        submitBtn.disabled = false;
                        submitBtn.style.backgroundColor = '';
                        submitBtn.style.borderColor = '';
                        submitBtn.style.color = '';
                        form.reset();
                    }, 3000);
                }, 1500);
            });
        });
    