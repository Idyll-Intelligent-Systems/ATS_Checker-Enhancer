// Animation utilities and effects
function initializeAnimations() {
    // Initialize intersection observer for scroll animations
    initializeScrollAnimations();
    
    // Initialize typing animation
    initializeTypingAnimation();
    
    // Initialize particle background (optional)
    initializeParticleBackground();
    
    // Initialize hover effects
    initializeHoverEffects();
}

// Scroll-triggered animations
function initializeScrollAnimations() {
    // Check if Intersection Observer is supported
    if (!window.IntersectionObserver) {
        console.warn('Intersection Observer not supported');
        return;
    }
    
    // Animation observer options
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    // Create observer
    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Add staggered animation for child elements
                const children = entry.target.querySelectorAll('.animate-child');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.classList.add('animate-in');
                    }, index * 100);
                });
            }
        });
    }, observerOptions);
    
    // Add animation classes to elements
    const animatedElements = document.querySelectorAll(`
        .timeline-item,
        .project-card,
        .skills-section,
        .contact-item,
        .about-content > *,
        .section-header
    `);
    
    animatedElements.forEach(element => {
        element.classList.add('animate-element');
        animationObserver.observe(element);
    });
    
    // Add animation styles
    addAnimationStyles();
}

function addAnimationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .animate-element {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .animate-element.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .animate-child {
            opacity: 0;
            transform: translateX(-20px);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .animate-child.animate-in {
            opacity: 1;
            transform: translateX(0);
        }
        
        /* Staggered animations for timeline items */
        .timeline-item:nth-child(even) .animate-element {
            transform: translateX(30px);
        }
        
        .timeline-item:nth-child(odd) .animate-element {
            transform: translateX(-30px);
        }
        
        /* Project card hover animations */
        .project-card {
            transform-origin: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .project-card:hover {
            transform: translateY(-8px) scale(1.02);
        }
        
        /* Skill tag animations */
        .skill-tag {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .skill-tag:hover {
            transform: translateY(-2px) scale(1.05);
        }
        
        /* Social link animations */
        .social-link {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .social-link:hover {
            transform: translateY(-3px) scale(1.1);
        }
        
        /* Button hover animations */
        .btn {
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        /* Fade in animation for page load */
        .hero-content > * {
            animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        
        .hero-image {
            animation-delay: 0.2s;
        }
        
        .hero-text > * {
            opacity: 0;
        }
        
        .hero-title {
            animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.3s forwards;
        }
        
        .hero-subtitle {
            animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.5s forwards;
        }
        
        .hero-tagline {
            animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.7s forwards;
        }
        
        .hero-buttons {
            animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.9s forwards;
        }
        
        .social-links {
            animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 1.1s forwards;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Floating animation for profile image */
        .profile-img {
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-10px);
            }
        }
        
        /* Loading animation improvements */
        .loading-screen {
            background: linear-gradient(135deg, var(--background-color) 0%, var(--background-alt) 100%);
        }
        
        .loading-spinner {
            animation: spin 1s linear infinite, pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.1);
            }
        }
    `;
    
    document.head.appendChild(style);
}

// Typing animation for hero text
function initializeTypingAnimation() {
    const heroTitle = document.getElementById('hero-title');
    const heroTagline = document.getElementById('hero-tagline');
    
    if (!heroTitle || !profileData) return;
    
    // Add typing animation to title after page load
    setTimeout(() => {
        typeWriter(heroTitle, profileData.personal.title, 100);
    }, 1500);
    
    // Add typing animation to tagline
    if (heroTagline) {
        setTimeout(() => {
            typeWriter(heroTagline, profileData.personal.tagline, 50);
        }, 3000);
    }
}

function typeWriter(element, text, speed = 100) {
    let i = 0;
    const originalText = element.textContent;
    element.textContent = '';
    element.style.borderRight = '2px solid var(--primary-color)';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        } else {
            // Remove cursor after typing is complete
            setTimeout(() => {
                element.style.borderRight = 'none';
            }, 1000);
        }
    }
    
    type();
}

// Particle background animation (optional)
function initializeParticleBackground() {
    const hero = document.querySelector('.hero');
    if (!hero) return;
    
    // Create canvas for particles
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '1';
    canvas.style.opacity = '0.1';
    
    hero.style.position = 'relative';
    hero.appendChild(canvas);
    
    // Resize canvas
    function resizeCanvas() {
        canvas.width = hero.offsetWidth;
        canvas.height = hero.offsetHeight;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Particle system
    const particles = [];
    const particleCount = 50;
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.size = Math.random() * 2 + 1;
        }
        
        update() {
            this.x += this.vx;
            this.y += this.vy;
            
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = getComputedStyle(document.documentElement)
                .getPropertyValue('--primary-color');
            ctx.fill();
        }
    }
    
    // Initialize particles
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        // Draw connections
        particles.forEach((particle, i) => {
            particles.slice(i + 1).forEach(otherParticle => {
                const distance = Math.sqrt(
                    Math.pow(particle.x - otherParticle.x, 2) +
                    Math.pow(particle.y - otherParticle.y, 2)
                );
                
                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particle.x, particle.y);
                    ctx.lineTo(otherParticle.x, otherParticle.y);
                    ctx.strokeStyle = getComputedStyle(document.documentElement)
                        .getPropertyValue('--primary-color');
                    ctx.globalAlpha = 0.1;
                    ctx.stroke();
                    ctx.globalAlpha = 1;
                }
            });
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

// Enhanced hover effects
function initializeHoverEffects() {
    // Add parallax effect to timeline items
    const timelineItems = document.querySelectorAll('.timeline-item');
    
    timelineItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            item.style.transform = 'translateX(10px) scale(1.02)';
            item.style.boxShadow = 'var(--shadow-lg)';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.transform = '';
            item.style.boxShadow = '';
        });
    });
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple 0.6s linear;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Smooth reveal animations for form elements
function initializeFormAnimations() {
    const formGroups = document.querySelectorAll('.form-group');
    
    formGroups.forEach((group, index) => {
        group.style.opacity = '0';
        group.style.transform = 'translateY(20px)';
        group.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        
        setTimeout(() => {
            group.style.opacity = '1';
            group.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });
}

// Initialize form animations when contact section is visible
function initializeContactAnimations() {
    const contactSection = document.getElementById('contact');
    
    if (!contactSection) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                initializeFormAnimations();
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });
    
    observer.observe(contactSection);
}

// Mouse trail effect (optional)
function initializeMouseTrail() {
    const trail = [];
    const maxTrailLength = 10;
    
    document.addEventListener('mousemove', (e) => {
        trail.push({ x: e.clientX, y: e.clientY, time: Date.now() });
        
        if (trail.length > maxTrailLength) {
            trail.shift();
        }
        
        updateTrail();
    });
    
    function updateTrail() {
        // Remove old trail elements
        document.querySelectorAll('.mouse-trail').forEach(el => el.remove());
        
        const now = Date.now();
        
        trail.forEach((point, index) => {
            const age = now - point.time;
            if (age < 500) {
                const trailElement = document.createElement('div');
                trailElement.className = 'mouse-trail';
                trailElement.style.cssText = `
                    position: fixed;
                    width: ${8 - (index * 0.5)}px;
                    height: ${8 - (index * 0.5)}px;
                    background: var(--primary-color);
                    border-radius: 50%;
                    pointer-events: none;
                    z-index: 9999;
                    left: ${point.x}px;
                    top: ${point.y}px;
                    opacity: ${1 - (age / 500)};
                    transform: translate(-50%, -50%);
                    transition: opacity 0.1s ease;
                `;
                
                document.body.appendChild(trailElement);
                
                setTimeout(() => {
                    trailElement.remove();
                }, 500);
            }
        });
    }
}

// Performance optimization: use requestAnimationFrame for smooth animations
function smoothScroll(target, duration = 1000) {
    const targetElement = document.querySelector(target);
    if (!targetElement) return;
    
    const targetPosition = targetElement.offsetTop - 80;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = easeInOutQuad(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        
        if (timeElapsed < duration) {
            requestAnimationFrame(animation);
        }
    }
    
    function easeInOutQuad(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }
    
    requestAnimationFrame(animation);
}

// Initialize contact animations when the module loads
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initializeContactAnimations, 1000);
});

// Export animation functions
window.animations = {
    initializeAnimations,
    typeWriter,
    smoothScroll,
    initializeMouseTrail
};
