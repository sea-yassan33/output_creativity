
        // Custom Luxury Cursor Tracking
        const cursor = document.getElementById('custom-cursor');
        document.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });

        document.querySelectorAll('a, button, input, select').forEach(item => {
            item.addEventListener('mouseenter', () => {
                cursor.style.width = '60px';
                cursor.style.height = '60px';
                cursor.style.backgroundColor = 'rgba(197, 164, 115, 0.1)';
            });
            item.addEventListener('mouseleave', () => {
                cursor.style.width = '40px';
                cursor.style.height = '40px';
                cursor.style.backgroundColor = 'transparent';
            });
        });

        // Sticky Header / Background Blur Scroll Event
        const header = document.getElementById('main-header');
        const headerBrand = document.getElementById('header-brand');
        const headerNav = document.getElementById('header-nav');
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 80) {
                header.classList.add('bg-[#0F1E16]/95', 'backdrop-blur-md', 'shadow-lg', 'py-4');
                header.classList.remove('py-6');
                headerBrand.classList.remove('text-[#E5DDCB]');
                headerBrand.classList.add('text-[#C5A473]');
            } else {
                header.classList.remove('bg-[#0F1E16]/95', 'backdrop-blur-md', 'shadow-lg', 'py-4');
                header.classList.add('py-6');
                headerBrand.classList.remove('text-[#C5A473]');
                headerBrand.classList.add('text-[#E5DDCB]');
            }
        });

        // Mobile Menu Toggling
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        const closeMobileMenu = document.getElementById('close-mobile-menu');

        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.remove('opacity-0', 'pointer-events-none');
        });
        closeMobileMenu.addEventListener('click', () => {
            mobileMenu.classList.add('opacity-0', 'pointer-events-none');
        });
        document.querySelectorAll('.mobile-nav-link').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('opacity-0', 'pointer-events-none');
            });
        });

        // Dynamic Digital Time Simulation (Luxury Hotel Climate Clock)
        function updateTime() {
            const timeSpan = document.getElementById('forest-time');
            const now = new Date();
            const hrs = String(now.getHours()).padStart(2, '0');
            const mins = String(now.getMinutes()).padStart(2, '0');
            timeSpan.innerText = `${hrs}:${mins} JST`;
        }
        setInterval(updateTime, 1000);
        updateTime();

        // Canvas Generative Art: Floating Leaves & Mist Particles
        const canvas = document.getElementById('ambient-canvas');
        const ctx = canvas.getContext('2d');

        let particles = [];
        const maxParticles = 40;

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        class Particle {
            constructor() {
                this.reset();
            }

            reset() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height + canvas.height;
                this.size = Math.random() * 2 + 0.5;
                this.speedY = -(Math.random() * 0.4 + 0.1);
                this.speedX = Math.random() * 0.3 - 0.15;
                this.opacity = Math.random() * 0.5 + 0.1;
                this.waveRange = Math.random() * 20 + 5;
                this.waveSpeed = Math.random() * 0.02 + 0.005;
                this.angle = Math.random() * Math.PI * 2;
            }

            update() {
                this.y += this.speedY;
                this.angle += this.waveSpeed;
                this.x += Math.sin(this.angle) * 0.15 + this.speedX;

                // Reset particle when it goes off screen
                if (this.y < -10 || this.x < -10 || this.x > canvas.width + 10) {
                    this.reset();
                }
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(197, 164, 115, ${this.opacity})`; // Warm Gold Glow
                ctx.shadowBlur = 8;
                ctx.shadowColor = '#C5A473';
                ctx.fill();
                ctx.shadowBlur = 0; // reset
            }
        }

        for (let i = 0; i < maxParticles; i++) {
            particles.push(new Particle());
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw subtle vector wind streams in background
            ctx.strokeStyle = 'rgba(197, 164, 115, 0.03)';
            ctx.lineWidth = 1;
            for (let i = 0; i < 3; i++) {
                ctx.beginPath();
                ctx.moveTo(0, canvas.height * (0.3 + i * 0.2));
                ctx.bezierCurveTo(
                    canvas.width * 0.25, canvas.height * (0.2 + i * 0.2),
                    canvas.width * 0.75, canvas.height * (0.4 + i * 0.2),
                    canvas.width, canvas.height * (0.3 + i * 0.2)
                );
                ctx.stroke();
            }

            particles.forEach(p => {
                p.update();
                p.draw();
            });
            requestAnimationFrame(animate);
        }
        animate();

        // Interactive Zen Ripple Effect in Experience Section
        const rippleSvg = document.getElementById('zen-ripple-svg');
        window.addEventListener('scroll', () => {
            const rect = rippleSvg.getBoundingClientRect();
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                const scrollProgress = (window.innerHeight - rect.top) / (window.innerHeight + rect.height);
                // Rotate the concentric circles subtly based on scroll
                rippleSvg.style.transform = `scale(${1 + scrollProgress * 0.08}) rotate(${scrollProgress * 15}deg)`;
            }
        });

    