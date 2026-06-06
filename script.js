document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================================================
    // 1. Dark / Light Theme Toggle
    // ==========================================================================
    const themeToggleBtn = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;

    // Check for saved theme preference, otherwise use system preference (default dark)
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme) {
        htmlElement.setAttribute('data-theme', savedTheme);
    } else {
        htmlElement.setAttribute('data-theme', systemPrefersDark ? 'dark' : 'light');
    }

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });

    // ==========================================================================
    // 2. Mobile Responsive Menu
    // ==========================================================================
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navMenu = document.getElementById('navMenu');
    const navLinks = document.querySelectorAll('.nav-link');

    const toggleMenu = () => {
        mobileMenuBtn.classList.toggle('active');
        navMenu.classList.toggle('active');
        document.body.classList.toggle('overflow-hidden'); // Prevent background scroll when menu open
    };

    mobileMenuBtn.addEventListener('click', toggleMenu);

    // Close menu when a link is clicked
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (navMenu.classList.contains('active')) {
                toggleMenu();
            }
        });
    });

    // Close menu if window is resized above mobile breakpoint
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && navMenu.classList.contains('active')) {
            mobileMenuBtn.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.classList.remove('overflow-hidden');
        }
    });

    // ==========================================================================
    // 3. Scroll Reveal Animations (Intersection Observer)
    // ==========================================================================
    const revealElements = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right');
    
    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active-reveal');
                // Once it reveals, we don't need to observe it anymore
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15, // Trigger when 15% of the element is visible
        rootMargin: '0px 0px -50px 0px' // Offset trigger point slightly from bottom of screen
    });

    revealElements.forEach(element => {
        revealObserver.observe(element);
    });

    // ==========================================================================
    // 4. Active Navigation Link on Scroll
    // ==========================================================================
    const sections = document.querySelectorAll('section');
    
    const navObserverOptions = {
        threshold: 0.3, // 30% of section visible in viewport
        rootMargin: '-10% 0px -40% 0px' // Narrow active zone for better accuracy
    };

    const navObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, navObserverOptions);

    sections.forEach(section => {
        navObserver.observe(section);
    });

    // ==========================================================================
    // 5. Contact Form Submission Handler
    // ==========================================================================
    const contactForm = document.getElementById('contactForm');

    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const submitButton = contactForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            
            // Get form values
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const message = document.getElementById('message').value;

            // Simple UI loading state feedback
            submitButton.disabled = true;
            submitButton.textContent = '发送中...';

            // Simulate form submission (e.g. AJAX or Formspree/Netlify integration)
            setTimeout(() => {
                // Reset button and form
                submitButton.disabled = false;
                submitButton.textContent = '发送成功！';
                submitButton.style.backgroundColor = '#22c55e'; // Green feedback
                submitButton.style.color = '#ffffff';

                contactForm.reset();

                // Custom notification toast
                const toast = document.createElement('div');
                toast.className = 'toast-notification';
                toast.textContent = `谢谢您的来信，${name}！我会尽快回复您。`;
                document.body.appendChild(toast);

                // Add styling to toast dynamically
                Object.assign(toast.style, {
                    position: 'fixed',
                    bottom: '2rem',
                    right: '2rem',
                    backgroundColor: 'var(--card-bg)',
                    border: '1px solid var(--primary-color)',
                    color: 'var(--text-primary)',
                    padding: '1rem 2rem',
                    borderRadius: '12px',
                    boxShadow: 'var(--shadow-md)',
                    zIndex: '2000',
                    backdropFilter: 'blur(10px)',
                    transition: 'opacity 0.5s ease, transform 0.5s ease',
                    transform: 'translateY(20px)',
                    opacity: '0'
                });

                // Animate toast in
                setTimeout(() => {
                    toast.style.transform = 'translateY(0)';
                    toast.style.opacity = '1';
                }, 100);

                // Remove toast and reset button styles after 4 seconds
                setTimeout(() => {
                    toast.style.opacity = '0';
                    toast.style.transform = 'translateY(20px)';
                    setTimeout(() => toast.remove(), 500);

                    // Reset button style
                    submitButton.style.backgroundColor = '';
                    submitButton.style.color = '';
                    submitButton.textContent = originalButtonText;
                }, 4000);

            }, 1500);
        });
    }
});
