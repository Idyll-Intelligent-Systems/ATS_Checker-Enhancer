// Global variables
let profileData = null;
let currentTheme = localStorage.getItem('theme') || 'light';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        // Show loading screen
        showLoading();
        
        // Load profile data
        await loadProfileData();
        
        // Set theme
        setTheme(currentTheme);
        
        // Initialize components
        initializeNavigation();
        initializeThemeToggle();
        initializeScrollEffects();
        initializeContactForm();
        
        // Populate content
        populateContent();
        
        // Hide loading screen
        hideLoading();
        
        // Initialize animations
        if (typeof initializeAnimations === 'function') {
            initializeAnimations();
        }
        
    } catch (error) {
        console.error('Error initializing app:', error);
        hideLoading();
        showError('Failed to load portfolio data. Please refresh the page.');
    }
}

// Loading functions
function showLoading() {
    const loadingScreen = document.getElementById('loading');
    if (loadingScreen) {
        loadingScreen.classList.remove('hidden');
    }
}

function hideLoading() {
    const loadingScreen = document.getElementById('loading');
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.classList.add('hidden');
        }, 1000);
    }
}

// Load profile data
async function loadProfileData() {
    try {
        const response = await fetch('data/profile.json');
        if (!response.ok) {
            throw new Error('Failed to fetch profile data');
        }
        profileData = await response.json();
        return profileData;
    } catch (error) {
        console.error('Error loading profile data:', error);
        throw error;
    }
}

// Theme functions
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    currentTheme = theme;
    localStorage.setItem('theme', theme);
    
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
}

function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(newTheme);
        });
    }
}

// Navigation functions
function initializeNavigation() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Mobile menu toggle
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }
    
    // Smooth scrolling and active link highlighting
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                // Close mobile menu if open
                if (navMenu) navMenu.classList.remove('active');
                if (navToggle) navToggle.classList.remove('active');
                
                // Smooth scroll to target
                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = targetElement.offsetTop - navbarHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Update active nav link on scroll
    window.addEventListener('scroll', updateActiveNavLink);
}

function updateActiveNavLink() {
    const sections = document.querySelectorAll('.section, .hero');
    const navLinks = document.querySelectorAll('.nav-link');
    const navbarHeight = document.querySelector('.navbar').offsetHeight;
    
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - navbarHeight - 100;
        const sectionHeight = section.offsetHeight;
        
        if (window.pageYOffset >= sectionTop && 
            window.pageYOffset < sectionTop + sectionHeight) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

// Scroll effects
function initializeScrollEffects() {
    const backToTop = document.getElementById('back-to-top');
    
    // Back to top button
    if (backToTop) {
        backToTop.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Show/hide back to top button
    window.addEventListener('scroll', () => {
        if (backToTop) {
            if (window.pageYOffset > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        }
    });
}

// Contact form
function initializeContactForm() {
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(contactForm);
            const submitButton = contactForm.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            
            // Show loading state
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            submitButton.disabled = true;
            
            try {
                // If using Netlify forms
                const response = await fetch('/', {
                    method: 'POST',
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: encode({
                        "form-name": "contact",
                        ...Object.fromEntries(formData)
                    })
                });
                
                if (response.ok) {
                    showSuccess('Message sent successfully! Thank you for reaching out.');
                    contactForm.reset();
                } else {
                    throw new Error('Network response was not ok');
                }
                
            } catch (error) {
                console.error('Error submitting form:', error);
                showError('Failed to send message. Please try again or contact me directly.');
            } finally {
                // Restore button state
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
            }
        });
    }
}

// Helper function for form encoding
function encode(data) {
    return Object.keys(data)
        .map(key => encodeURIComponent(key) + "=" + encodeURIComponent(data[key]))
        .join("&");
}

// Populate content with profile data
function populateContent() {
    if (!profileData) return;
    
    populatePersonalInfo();
    populateAboutSection();
    populateExperienceSection();
    populateProjectsSection();
    populateContactSection();
    populateFooter();
}

function populatePersonalInfo() {
    const { personal } = profileData;
    
    // Update navigation brand
    const navName = document.getElementById('nav-name');
    if (navName) navName.textContent = personal.name;
    
    // Update hero section
    const heroName = document.getElementById('hero-name');
    if (heroName) heroName.textContent = personal.name;
    
    const heroTitle = document.getElementById('hero-title');
    if (heroTitle) heroTitle.textContent = personal.title;
    
    const heroTagline = document.getElementById('hero-tagline');
    if (heroTagline) heroTagline.textContent = personal.tagline;
    
    const profileImage = document.getElementById('profile-image');
    if (profileImage) {
        profileImage.src = personal.photo;
        profileImage.alt = `${personal.name} - Profile Picture`;
    }
    
    // Update page title
    document.title = `${personal.name} - ${personal.title}`;
    
    // Update meta description
    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
        metaDescription.content = `${personal.name} - ${personal.title}. ${personal.tagline}`;
    }
    
    // Populate social links
    populateSocialLinks(personal.contact);
}

function populateSocialLinks(contact) {
    const socialLinks = document.getElementById('social-links');
    const footerSocial = document.getElementById('footer-social');
    
    const socialPlatforms = [
        { key: 'linkedin', icon: 'fab fa-linkedin-in', label: 'LinkedIn' },
        { key: 'github', icon: 'fab fa-github', label: 'GitHub' },
        { key: 'twitter', icon: 'fab fa-twitter', label: 'Twitter' },
        { key: 'instagram', icon: 'fab fa-instagram', label: 'Instagram' },
        { key: 'website', icon: 'fas fa-globe', label: 'Website' }
    ];
    
    const createSocialLink = (platform, url, isFooter = false) => {
        const link = document.createElement('a');
        link.href = url;
        link.className = 'social-link';
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.title = platform.label;
        link.innerHTML = `<i class="${platform.icon}"></i>`;
        
        if (isFooter) {
            link.style.fontSize = '0.9rem';
        }
        
        return link;
    };
    
    // Clear existing social links
    if (socialLinks) socialLinks.innerHTML = '';
    if (footerSocial) footerSocial.innerHTML = '';
    
    // Add social links
    socialPlatforms.forEach(platform => {
        const url = contact[platform.key];
        if (url && url !== '#') {
            if (socialLinks) {
                socialLinks.appendChild(createSocialLink(platform, url));
            }
            if (footerSocial) {
                footerSocial.appendChild(createSocialLink(platform, url, true));
            }
        }
    });
}

function populateAboutSection() {
    const { about, skills } = profileData;
    
    // About summary
    const aboutSummary = document.getElementById('about-summary');
    if (aboutSummary) aboutSummary.textContent = about.summary;
    
    // Highlights
    const highlightsList = document.getElementById('about-highlights-list');
    if (highlightsList) {
        highlightsList.innerHTML = '';
        about.highlights.forEach(highlight => {
            const li = document.createElement('li');
            li.textContent = highlight;
            highlightsList.appendChild(li);
        });
    }
    
    // Values
    const valuesGrid = document.getElementById('values-grid');
    if (valuesGrid) {
        valuesGrid.innerHTML = '';
        about.values.forEach(value => {
            const valueItem = document.createElement('div');
            valueItem.className = 'value-item';
            valueItem.textContent = value;
            valuesGrid.appendChild(valueItem);
        });
    }
    
    // Skills
    const skillCategories = [
        { id: 'technical-skills', data: skills.technical },
        { id: 'tools-skills', data: skills.tools },
        { id: 'soft-skills', data: skills.soft }
    ];
    
    skillCategories.forEach(category => {
        const container = document.getElementById(category.id);
        if (container && category.data) {
            container.innerHTML = '';
            category.data.forEach(skill => {
                const skillTag = document.createElement('span');
                skillTag.className = 'skill-tag';
                skillTag.textContent = skill;
                container.appendChild(skillTag);
            });
        }
    });
}

function populateExperienceSection() {
    const { experience } = profileData;
    const timeline = document.getElementById('experience-timeline');
    
    if (!timeline || !experience) return;
    
    timeline.innerHTML = '';
    
    experience.forEach(exp => {
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        
        timelineItem.innerHTML = `
            <div class="timeline-header">
                <h3 class="timeline-role">${exp.role}</h3>
                <div class="timeline-company">${exp.company}</div>
                <div class="timeline-meta">
                    <span><i class="fas fa-map-marker-alt"></i> ${exp.location}</span>
                    <span><i class="fas fa-calendar"></i> ${exp.dates}</span>
                    <span><i class="fas fa-briefcase"></i> ${exp.type}</span>
                </div>
            </div>
            <div class="timeline-description">
                <ul>
                    ${exp.description.map(desc => `<li>${desc}</li>`).join('')}
                </ul>
            </div>
            <div class="timeline-technologies">
                ${exp.technologies.map(tech => `<span class="tech-tag">${tech}</span>`).join('')}
            </div>
        `;
        
        timeline.appendChild(timelineItem);
    });
}

function populateProjectsSection() {
    const { projects } = profileData;
    const projectsGrid = document.getElementById('projects-grid');
    
    if (!projectsGrid || !projects) return;
    
    projectsGrid.innerHTML = '';
    
    projects.forEach(project => {
        const projectCard = document.createElement('div');
        projectCard.className = 'project-card';
        
        const linksHtml = Object.entries(project.links || {})
            .filter(([key, url]) => url && url !== '#')
            .map(([key, url]) => {
                const icons = {
                    demo: 'fas fa-external-link-alt',
                    github: 'fab fa-github',
                    live: 'fas fa-globe'
                };
                const icon = icons[key] || 'fas fa-link';
                return `<a href="${url}" class="project-link" target="_blank" rel="noopener noreferrer">
                    <i class="${icon}"></i> ${key.charAt(0).toUpperCase() + key.slice(1)}
                </a>`;
            }).join('');
        
        projectCard.innerHTML = `
            <div class="project-header">
                <h3 class="project-title">${project.title}</h3>
                <p class="project-description">${project.description}</p>
                <ul class="project-highlights">
                    ${project.highlights.map(highlight => `<li>${highlight}</li>`).join('')}
                </ul>
                <div class="project-technologies">
                    ${project.technologies.map(tech => `<span class="tech-tag">${tech}</span>`).join('')}
                </div>
            </div>
            ${linksHtml ? `<div class="project-links">${linksHtml}</div>` : ''}
        `;
        
        projectsGrid.appendChild(projectCard);
    });
}

function populateContactSection() {
    const { personal } = profileData;
    const { contact } = personal;
    
    // Contact information
    const contactEmail = document.getElementById('contact-email');
    if (contactEmail) {
        contactEmail.textContent = contact.email;
        contactEmail.href = `mailto:${contact.email}`;
    }
    
    const contactPhone = document.getElementById('contact-phone');
    if (contactPhone) contactPhone.textContent = contact.phone;
    
    const contactLocation = document.getElementById('contact-location');
    if (contactLocation) contactLocation.textContent = contact.location;
}

function populateFooter() {
    const { personal } = profileData;
    
    // Update current year
    const currentYear = document.getElementById('current-year');
    if (currentYear) currentYear.textContent = new Date().getFullYear();
    
    // Update footer name
    const footerName = document.getElementById('footer-name');
    if (footerName) footerName.textContent = personal.name;
}

// Utility functions
function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        color: 'white',
        zIndex: '10000',
        fontSize: '0.9rem',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        transform: 'translateX(400px)',
        transition: 'all 0.3s ease'
    });
    
    // Set background color based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after delay
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Export functions for external use
window.profileApp = {
    loadProfileData,
    populateContent,
    setTheme,
    showSuccess,
    showError
};
