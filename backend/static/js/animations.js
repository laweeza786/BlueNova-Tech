/* ============================================================
   BlueNova — Animations Engine v6.0
   Scroll Reveal, Counters, Parallax, Mouse Tracking
   ============================================================ */

(function() {
    'use strict';

    // --------------------------------------------------------
    // 1. SCROLL REVEAL (IntersectionObserver)
    // --------------------------------------------------------
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                // Only unobserve non-repeating elements
                if (!entry.target.dataset.repeat) {
                    revealObserver.unobserve(entry.target);
                }
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px'
    });

    function initScrollReveal() {
        const revealElements = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale, .stagger-children');
        revealElements.forEach(el => revealObserver.observe(el));
    }

    // --------------------------------------------------------
    // 2. ANIMATED COUNTERS
    // --------------------------------------------------------
    function animateCounter(element) {
        const target = parseInt(element.dataset.target) || 0;
        const suffix = element.dataset.suffix || '';
        const prefix = element.dataset.prefix || '';
        const duration = parseInt(element.dataset.duration) || 2000;
        const start = 0;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(start + (target - start) * eased);
            element.textContent = prefix + current.toLocaleString() + suffix;

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.textContent = prefix + target.toLocaleString() + suffix;
            }
        }
        requestAnimationFrame(update);
    }

    function initCounters() {
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.dataset.counted) {
                    entry.target.dataset.counted = 'true';
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        document.querySelectorAll('[data-counter]').forEach(el => {
            counterObserver.observe(el);
        });
    }

    // --------------------------------------------------------
    // 3. PROGRESS BAR ANIMATION
    // --------------------------------------------------------
    function initProgressBars() {
        const progressObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bar = entry.target.querySelector('.progress-bar');
                    if (bar && bar.dataset.width) {
                        setTimeout(() => {
                            bar.style.width = bar.dataset.width;
                        }, 200);
                    }
                    progressObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });

        document.querySelectorAll('.progress-premium').forEach(el => {
            progressObserver.observe(el);
        });
    }

    // --------------------------------------------------------
    // 4. NAVBAR SCROLL EFFECT
    // --------------------------------------------------------
    function initNavbarScroll() {
        const navbar = document.querySelector('.landing-navbar');
        if (!navbar) return;

        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    if (window.scrollY > 60) {
                        navbar.classList.add('scrolled');
                    } else {
                        navbar.classList.remove('scrolled');
                    }
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    // --------------------------------------------------------
    // 5. SCROLL TO TOP BUTTON
    // --------------------------------------------------------
    function initScrollToTop() {
        const btn = document.querySelector('.scroll-top-btn');
        if (!btn) return;

        window.addEventListener('scroll', () => {
            if (window.scrollY > 500) {
                btn.classList.add('visible');
            } else {
                btn.classList.remove('visible');
            }
        });

        btn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // --------------------------------------------------------
    // 6. SMOOTH ANCHOR SCROLLING
    // --------------------------------------------------------
    function initSmoothAnchors() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }

    // --------------------------------------------------------
    // 7. CARD MOUSE TRACKING / TILT
    // --------------------------------------------------------
    function initCardTilt() {
        document.querySelectorAll('[data-tilt]').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = ((y - centerY) / centerY) * -3;
                const rotateY = ((x - centerX) / centerX) * 3;
                card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(800px) rotateX(0) rotateY(0) translateY(0)';
            });
        });
    }

    // --------------------------------------------------------
    // 8. TYPEWRITER EFFECT
    // --------------------------------------------------------
    function initTypewriter() {
        document.querySelectorAll('[data-typewriter]').forEach(el => {
            const text = el.dataset.typewriter;
            const speed = parseInt(el.dataset.speed) || 80;
            el.textContent = '';
            el.style.borderRight = '2px solid var(--primary)';
            let i = 0;

            function type() {
                if (i < text.length) {
                    el.textContent += text.charAt(i);
                    i++;
                    setTimeout(type, speed);
                } else {
                    // Blinking cursor
                    el.style.animation = 'pulse 1s ease-in-out infinite';
                    setTimeout(() => { el.style.borderRight = 'none'; el.style.animation = 'none'; }, 2000);
                }
            }

            const observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    setTimeout(type, 500);
                    observer.unobserve(el);
                }
            }, { threshold: 0.5 });
            observer.observe(el);
        });
    }

    // --------------------------------------------------------
    // 9. STAGGER FADE-IN FOR GRIDS
    // --------------------------------------------------------
    function initStaggerFade() {
        const staggerObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const children = entry.target.children;
                    Array.from(children).forEach((child, index) => {
                        setTimeout(() => {
                            child.style.opacity = '1';
                            child.style.transform = 'translateY(0)';
                        }, index * 80);
                    });
                    staggerObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });

        document.querySelectorAll('.stagger-grid').forEach(el => {
            Array.from(el.children).forEach(child => {
                child.style.opacity = '0';
                child.style.transform = 'translateY(20px)';
                child.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            });
            staggerObserver.observe(el);
        });
    }

    // --------------------------------------------------------
    // 10. PARALLAX EFFECT (Hero Background)
    // --------------------------------------------------------
    function initParallax() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        if (parallaxElements.length === 0) return;

        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    const scrolled = window.scrollY;
                    parallaxElements.forEach(el => {
                        const speed = parseFloat(el.dataset.parallax) || 0.3;
                        el.style.transform = `translateY(${scrolled * speed}px)`;
                    });
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    // --------------------------------------------------------
    // 11. HOVER GLOW EFFECT
    // --------------------------------------------------------
    function initHoverGlow() {
        document.querySelectorAll('[data-glow]').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                card.style.setProperty('--glow-x', `${x}px`);
                card.style.setProperty('--glow-y', `${y}px`);
            });
        });
    }

    // --------------------------------------------------------
    // 12. PASSWORD STRENGTH INDICATOR
    // --------------------------------------------------------
    function initPasswordStrength() {
        document.querySelectorAll('[data-password-strength]').forEach(input => {
            const bars = input.closest('.mb-3, .mb-4, .form-group')?.querySelectorAll('.password-strength-bar');
            if (!bars || bars.length === 0) return;

            input.addEventListener('input', () => {
                const val = input.value;
                let strength = 0;
                if (val.length >= 8) strength++;
                if (/[A-Z]/.test(val)) strength++;
                if (/[0-9]/.test(val)) strength++;
                if (/[^A-Za-z0-9]/.test(val)) strength++;

                bars.forEach((bar, i) => {
                    bar.classList.remove('active', 'medium', 'strong');
                    if (i < strength) {
                        bar.classList.add('active');
                        if (strength >= 3) bar.classList.add('strong');
                        else if (strength >= 2) bar.classList.add('medium');
                    }
                });
            });
        });
    }

    // --------------------------------------------------------
    // INITIALIZATION
    // --------------------------------------------------------
    function init() {
        initScrollReveal();
        initCounters();
        initProgressBars();
        initNavbarScroll();
        initScrollToTop();
        initSmoothAnchors();
        initCardTilt();
        initTypewriter();
        initStaggerFade();
        initParallax();
        initHoverGlow();
        initPasswordStrength();
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
