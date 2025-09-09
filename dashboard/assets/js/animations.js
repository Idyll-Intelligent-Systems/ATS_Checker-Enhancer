// Advanced Animation System
class AnimationManager {
    constructor() {
        this.observers = new Map();
        this.animationQueue = [];
        this.isRunning = false;
        
        this.init();
    }

    init() {
        this.setupIntersectionObserver();
        this.setupScrollAnimations();
        this.setupParticleSystem();
        this.setupTypewriter();
        this.setupCountUpAnimations();
    }

    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '0px 0px -10% 0px',
            threshold: [0, 0.1, 0.5, 1]
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const element = entry.target;
                const animationType = element.dataset.animation || 'fadeIn';
                const delay = parseInt(element.dataset.delay) || 0;
                
                if (entry.isIntersecting && entry.intersectionRatio > 0.1) {
                    setTimeout(() => {
                        this.triggerAnimation(element, animationType);
                    }, delay);
                    
                    // Remove observer after animation to prevent re-triggering
                    if (!element.dataset.repeat) {
                        observer.unobserve(element);
                    }
                }
            });
        }, options);

        // Observe all elements with animation data attributes
        document.querySelectorAll('[data-animation]').forEach(el => {
            observer.observe(el);
        });

        // Store observer reference
        this.observers.set('intersection', observer);
    }

    setupScrollAnimations() {
        let ticking = false;
        
        const updateAnimations = () => {
            this.updateParallax();
            this.updateProgressBars();
            ticking = false;
        };

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateAnimations);
                ticking = true;
            }
        });
    }

    updateParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = parseFloat(element.dataset.speed) || 0.5;
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }

    updateProgressBars() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        
        const progressBars = document.querySelectorAll('.scroll-progress');
        progressBars.forEach(bar => {
            bar.style.width = `${scrollPercent}%`;
        });
    }

    setupParticleSystem() {
        const particleContainer = document.querySelector('.hero-particles');
        if (!particleContainer) return;

        this.createParticles(particleContainer, 50);
    }

    createParticles(container, count) {
        for (let i = 0; i < count; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random properties
            const size = Math.random() * 4 + 2;
            const x = Math.random() * 100;
            const y = Math.random() * 100;
            const duration = Math.random() * 20 + 10;
            const delay = Math.random() * 5;
            
            particle.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                background: var(--primary-500);
                border-radius: 50%;
                left: ${x}%;
                top: ${y}%;
                opacity: ${Math.random() * 0.5 + 0.2};
                animation: particleFloat ${duration}s ${delay}s infinite ease-in-out;
            `;
            
            container.appendChild(particle);
        }
    }

    setupTypewriter() {
        const typewriterElements = document.querySelectorAll('.typewriter');
        
        typewriterElements.forEach(element => {
            const text = element.textContent;
            const speed = parseInt(element.dataset.speed) || 50;
            const delay = parseInt(element.dataset.delay) || 0;
            
            setTimeout(() => {
                this.typewriterEffect(element, text, speed);
            }, delay);
        });
    }

    typewriterEffect(element, text, speed) {
        element.textContent = '';
        element.style.borderRight = '2px solid var(--primary-500)';
        
        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
                // Remove cursor after a delay
                setTimeout(() => {
                    element.style.borderRight = 'none';
                }, 1000);
            }
        }, speed);
    }

    setupCountUpAnimations() {
        const countElements = document.querySelectorAll('[data-count-up]');
        
        countElements.forEach(element => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCountUp(element);
                        observer.unobserve(element);
                    }
                });
            });
            
            observer.observe(element);
        });
    }

    animateCountUp(element) {
        const target = parseInt(element.dataset.countUp);
        const duration = parseInt(element.dataset.duration) || 2000;
        const startTime = performance.now();
        const startValue = 0;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(
                startValue + (target - startValue) * this.easeOutQuart(progress)
            );
            
            element.textContent = this.formatNumber(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    triggerAnimation(element, animationType) {
        // Remove any existing animation classes
        element.classList.remove('animate-in', 'animate-out');
        
        // Add the appropriate animation class
        element.classList.add('animate-in');
        
        // Add specific animation type class
        switch(animationType) {
            case 'fadeIn':
                element.classList.add('animate-fade-in');
                break;
            case 'slideUp':
                element.classList.add('animate-slide-up');
                break;
            case 'slideDown':
                element.classList.add('animate-slide-down');
                break;
            case 'slideLeft':
                element.classList.add('animate-slide-left');
                break;
            case 'slideRight':
                element.classList.add('animate-slide-right');
                break;
            case 'scaleIn':
                element.classList.add('animate-scale-in');
                break;
            case 'bounce':
                element.classList.add('animate-bounce');
                break;
            case 'pulse':
                element.classList.add('animate-pulse');
                break;
            case 'wiggle':
                element.classList.add('animate-wiggle');
                break;
            case 'float':
                element.classList.add('animate-float');
                break;
            default:
                element.classList.add('animate-fade-in');
        }
    }

    // Advanced animation methods
    createMorphingShape(container, options = {}) {
        const shape = document.createElement('div');
        const {
            size = 100,
            color = 'var(--primary-500)',
            duration = 10,
            blur = false
        } = options;
        
        shape.className = 'morphing-shape';
        shape.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            background: ${color};
            position: absolute;
            animation: morphShape ${duration}s infinite;
            ${blur ? 'filter: blur(20px);' : ''}
            opacity: 0.6;
        `;
        
        container.appendChild(shape);
        return shape;
    }

    createRippleEffect(element, event) {
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('div');
        ripple.className = 'ripple-effect';
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    createFloatingElements(container, count = 10) {
        for (let i = 0; i < count; i++) {
            const element = document.createElement('div');
            element.className = 'floating-element';
            
            const size = Math.random() * 20 + 10;
            const x = Math.random() * 100;
            const delay = Math.random() * 5;
            const duration = Math.random() * 10 + 15;
            
            element.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                background: var(--primary-500);
                border-radius: 50%;
                left: ${x}%;
                bottom: -${size}px;
                opacity: 0.3;
                animation: floatUp ${duration}s ${delay}s infinite ease-in-out;
            `;
            
            container.appendChild(element);
        }
    }

    createTextRevealAnimation(element, options = {}) {
        const {
            direction = 'up',
            stagger = 100,
            duration = 600
        } = options;
        
        const text = element.textContent;
        element.innerHTML = '';
        
        // Split text into spans
        const chars = text.split('').map(char => {
            const span = document.createElement('span');
            span.textContent = char === ' ' ? '\u00A0' : char;
            span.style.cssText = `
                display: inline-block;
                opacity: 0;
                transform: translateY(${direction === 'up' ? '20px' : '-20px'});
                transition: all ${duration}ms ease-out;
            `;
            return span;
        });
        
        chars.forEach(span => element.appendChild(span));
        
        // Animate each character with stagger
        chars.forEach((span, index) => {
            setTimeout(() => {
                span.style.opacity = '1';
                span.style.transform = 'translateY(0)';
            }, index * stagger);
        });
    }

    createLoadingAnimation(container, type = 'spinner') {
        const loader = document.createElement('div');
        loader.className = `loading-animation loading-${type}`;
        
        switch(type) {
            case 'spinner':
                loader.innerHTML = '<div class="spinner"></div>';
                break;
            case 'dots':
                loader.innerHTML = `
                    <div class="dots">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                `;
                break;
            case 'pulse':
                loader.innerHTML = '<div class="pulse"></div>';
                break;
            case 'wave':
                loader.innerHTML = `
                    <div class="wave">
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                    </div>
                `;
                break;
        }
        
        container.appendChild(loader);
        return loader;
    }

    // Utility methods
    easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }

    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    // Animation queue system
    queueAnimation(callback, delay = 0) {
        this.animationQueue.push({ callback, delay });
        if (!this.isRunning) {
            this.processQueue();
        }
    }

    processQueue() {
        if (this.animationQueue.length === 0) {
            this.isRunning = false;
            return;
        }
        
        this.isRunning = true;
        const { callback, delay } = this.animationQueue.shift();
        
        setTimeout(() => {
            callback();
            this.processQueue();
        }, delay);
    }

    // Performance monitoring
    measurePerformance(name, fn) {
        const start = performance.now();
        fn();
        const end = performance.now();
        console.log(`Animation "${name}" took ${end - start} milliseconds`);
    }

    // Cleanup methods
    removeAllAnimations(element) {
        const animationClasses = [
            'animate-fade-in', 'animate-fade-out',
            'animate-slide-up', 'animate-slide-down',
            'animate-slide-left', 'animate-slide-right',
            'animate-scale-in', 'animate-scale-out',
            'animate-bounce', 'animate-pulse',
            'animate-wiggle', 'animate-float',
            'animate-in', 'animate-out'
        ];
        
        element.classList.remove(...animationClasses);
    }

    destroy() {
        // Clean up all observers
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
        
        // Clear animation queue
        this.animationQueue = [];
        this.isRunning = false;
        
        // Remove event listeners
        window.removeEventListener('scroll', this.updateAnimations);
    }
}

// CSS keyframes that need to be injected
const additionalCSS = `
    @keyframes particleFloat {
        0%, 100% {
            transform: translateY(0px) rotate(0deg);
            opacity: 0.2;
        }
        25% {
            transform: translateY(-20px) rotate(90deg);
            opacity: 1;
        }
        50% {
            transform: translateY(-10px) rotate(180deg);
            opacity: 0.8;
        }
        75% {
            transform: translateY(-30px) rotate(270deg);
            opacity: 0.6;
        }
    }

    @keyframes floatUp {
        0% {
            transform: translateY(0) rotate(0deg);
            opacity: 0.3;
        }
        50% {
            opacity: 0.6;
        }
        100% {
            transform: translateY(-100vh) rotate(360deg);
            opacity: 0;
        }
    }

    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .loading-dots .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--primary-500);
        display: inline-block;
        margin: 0 2px;
        animation: dotPulse 1.4s ease-in-out infinite both;
    }

    .loading-dots .dot:nth-child(1) { animation-delay: -0.32s; }
    .loading-dots .dot:nth-child(2) { animation-delay: -0.16s; }

    @keyframes dotPulse {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }

    .loading-wave .wave-bar {
        width: 4px;
        height: 20px;
        background: var(--primary-500);
        display: inline-block;
        margin: 0 2px;
        animation: waveAnimation 1s ease-in-out infinite;
    }

    .loading-wave .wave-bar:nth-child(1) { animation-delay: 0s; }
    .loading-wave .wave-bar:nth-child(2) { animation-delay: 0.1s; }
    .loading-wave .wave-bar:nth-child(3) { animation-delay: 0.2s; }
    .loading-wave .wave-bar:nth-child(4) { animation-delay: 0.3s; }

    @keyframes waveAnimation {
        0%, 40%, 100% {
            transform: scaleY(0.4);
        }
        20% {
            transform: scaleY(1);
        }
    }
`;

// Inject additional CSS
const injectCSS = () => {
    const style = document.createElement('style');
    style.textContent = additionalCSS;
    document.head.appendChild(style);
};

// Initialize animation manager
let animationManager;
document.addEventListener('DOMContentLoaded', () => {
    injectCSS();
    animationManager = new AnimationManager();
    console.log('✨ Animation Manager initialized');
});

// Global animation functions
function createRipple(element, event) {
    if (animationManager) {
        animationManager.createRippleEffect(element, event);
    }
}

function animateElement(element, animationType, delay = 0) {
    if (animationManager) {
        setTimeout(() => {
            animationManager.triggerAnimation(element, animationType);
        }, delay);
    }
}

// Add click ripple effect to buttons
document.addEventListener('click', (e) => {
    if (e.target.matches('.btn, .nav-link, .service-card, .metric-card')) {
        createRipple(e.target, e);
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AnimationManager;
}
