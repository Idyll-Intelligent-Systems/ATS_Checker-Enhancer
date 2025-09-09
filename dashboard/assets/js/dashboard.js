// Dashboard Main JavaScript
class ZexDashboard {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupIntersectionObserver();
        this.startCounters();
        this.initializeMetrics();
    }

    init() {
        // Initialize theme
        this.initializeTheme();
        
        // Initialize dropdowns
        this.initializeDropdowns();
        
        // Initialize mobile menu
        this.initializeMobileMenu();
        
        // Setup service interactions
        this.setupServiceInteractions();
        
        // Initialize API status monitoring
        this.monitorApiStatus();
        
        // Setup periodic data updates
        this.setupDataUpdates();
    }

    initializeTheme() {
        const savedTheme = localStorage.getItem('zex-theme') || 'theme-dark';
        document.body.className = savedTheme;
        
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    toggleTheme() {
        const currentTheme = document.body.className;
        let newTheme;
        
        switch(currentTheme) {
            case 'theme-light':
                newTheme = 'theme-dark';
                break;
            case 'theme-dark':
                newTheme = 'theme-futuristic';
                break;
            case 'theme-futuristic':
                newTheme = 'theme-light';
                break;
            default:
                newTheme = 'theme-dark';
        }
        
        document.body.className = newTheme;
        localStorage.setItem('zex-theme', newTheme);
        
        // Trigger theme change event
        window.dispatchEvent(new CustomEvent('themeChange', { detail: { theme: newTheme } }));
        
        this.showToast('Theme changed successfully!', 'success');
    }

    initializeDropdowns() {
        const dropdownItems = document.querySelectorAll('.nav-item.dropdown');
        
        dropdownItems.forEach(item => {
            const trigger = item.querySelector('.nav-link');
            const menu = item.querySelector('.dropdown-menu');
            
            if (trigger && menu) {
                trigger.addEventListener('mouseenter', () => {
                    item.classList.add('active');
                });
                
                item.addEventListener('mouseleave', () => {
                    item.classList.remove('active');
                });
                
                // Handle keyboard navigation
                trigger.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        item.classList.toggle('active');
                    }
                });
            }
        });
    }

    initializeMobileMenu() {
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.getElementById('navMenu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navToggle.classList.toggle('active');
                navMenu.classList.toggle('active');
            });
        }
    }

    setupEventListeners() {
        // Smooth scrolling for anchor links
        document.addEventListener('click', (e) => {
            if (e.target.matches('a[href^="#"]')) {
                e.preventDefault();
                const target = document.querySelector(e.target.getAttribute('href'));
                if (target) {
                    this.scrollToElement(target);
                }
            }
        });

        // Handle window resize
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));

        // Handle escape key for modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });

        // Handle chart period changes
        const chartControls = document.querySelectorAll('.chart-controls .btn');
        chartControls.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const period = e.target.dataset.period;
                if (period) {
                    this.updateChartPeriod(period);
                }
            });
        });

        // Handle industry selector change
        const industrySelector = document.getElementById('industrySelector');
        if (industrySelector) {
            industrySelector.addEventListener('change', (e) => {
                this.updateIndustryComparison(e.target.value);
            });
        }
    }

    scrollToElement(element) {
        const headerHeight = document.querySelector('.navbar').offsetHeight;
        const targetPosition = element.offsetTop - headerHeight - 20;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }

    setupServiceInteractions() {
        // Service card hover effects
        const serviceCards = document.querySelectorAll('.service-card');
        serviceCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.classList.add('animate-scale-in');
            });
            
            card.addEventListener('mouseleave', () => {
                card.classList.remove('animate-scale-in');
            });
        });
    }

    openService(serviceType) {
        let url;
        switch(serviceType) {
            case 'ats':
                url = 'http://localhost:8000';
                break;
            case 'website':
                url = 'http://localhost:8080';
                break;
            default:
                this.showToast('Service URL not configured', 'warning');
                return;
        }
        
        this.showServiceModal(serviceType, url);
    }

    showServiceModal(serviceType, url) {
        const modal = document.getElementById('serviceModal');
        const modalTitle = document.getElementById('modalTitle');
        const serviceFrame = document.getElementById('serviceFrame');
        
        if (modal && modalTitle && serviceFrame) {
            modalTitle.textContent = this.getServiceTitle(serviceType);
            serviceFrame.src = url;
            modal.classList.add('active');
            
            // Add loading state
            serviceFrame.addEventListener('load', () => {
                serviceFrame.classList.add('loaded');
            });
        }
    }

    getServiceTitle(serviceType) {
        const titles = {
            'ats': 'Zex ATS Analyzer',
            'website': 'Dynamic Website Generator',
            'analytics': 'Career Analytics Dashboard'
        };
        return titles[serviceType] || 'Service';
    }

    closeModal() {
        const modal = document.getElementById('serviceModal');
        if (modal) {
            modal.classList.remove('active');
            setTimeout(() => {
                const serviceFrame = document.getElementById('serviceFrame');
                if (serviceFrame) {
                    serviceFrame.src = '';
                }
            }, 300);
        }
    }

    initializeAnimations() {
        // Add animation classes to elements that should animate on load
        const animateElements = document.querySelectorAll('.animate-on-scroll');
        animateElements.forEach(el => {
            el.classList.add('animate-fade-in');
        });
    }

    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, options);

        // Observe elements that should animate on scroll
        const animateElements = document.querySelectorAll('.animate-on-scroll');
        animateElements.forEach(el => observer.observe(el));
    }

    startCounters() {
        const counters = document.querySelectorAll('[data-count]');
        counters.forEach(counter => {
            const target = parseInt(counter.dataset.count);
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = target.toLocaleString() + (counter.textContent.includes('%') ? '%' : '+');
                    clearInterval(timer);
                } else {
                    counter.textContent = Math.floor(current).toLocaleString() + (counter.textContent.includes('%') ? '%' : '+');
                }
            }, 30);
        });
    }

    initializeMetrics() {
        // Simulate real-time metric updates
        setInterval(() => {
            this.updateMetrics();
        }, 30000); // Update every 30 seconds
    }

    updateMetrics() {
        const metrics = {
            totalUsers: this.generateMetricValue(12546, 0.02),
            totalAnalyses: this.generateMetricValue(45892, 0.03),
            totalWebsites: this.generateMetricValue(8234, 0.025),
            averageScore: this.generateMetricValue(87.2, 0.01, true)
        };

        Object.keys(metrics).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                this.animateValue(element, parseInt(element.textContent.replace(/,/g, '')), metrics[key]);
            }
        });
    }

    generateMetricValue(base, volatility, isDecimal = false) {
        const change = (Math.random() - 0.5) * 2 * volatility;
        const newValue = base * (1 + change);
        return isDecimal ? Math.round(newValue * 10) / 10 : Math.round(newValue);
    }

    animateValue(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = start + (end - start) * this.easeOutCubic(progress);
            element.textContent = Math.round(current).toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    monitorApiStatus() {
        const apiEndpoints = [
            { id: 'ats-api', url: 'http://localhost:8000/health', name: 'ATS API' },
            { id: 'website-api', url: 'http://localhost:8080/health', name: 'Website API' }
        ];

        apiEndpoints.forEach(api => {
            this.checkApiStatus(api);
        });

        // Check status every minute
        setInterval(() => {
            apiEndpoints.forEach(api => {
                this.checkApiStatus(api);
            });
        }, 60000);
    }

    async checkApiStatus(api) {
        try {
            const response = await fetch(api.url, { 
                method: 'GET', 
                timeout: 5000 
            });
            
            const isOnline = response.ok;
            this.updateApiStatus(api.id, isOnline);
        } catch (error) {
            this.updateApiStatus(api.id, false);
        }
    }

    updateApiStatus(apiId, isOnline) {
        const statusElements = document.querySelectorAll(`[data-api="${apiId}"] .api-status`);
        statusElements.forEach(element => {
            element.className = isOnline ? 'api-status online' : 'api-status offline';
            element.textContent = isOnline ? 'Online' : 'Offline';
        });
    }

    updateChartPeriod(period) {
        // Update chart controls
        document.querySelectorAll('.chart-controls .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-period="${period}"]`).classList.add('active');
        
        // Update chart data (this would typically fetch new data)
        this.refreshCharts(period);
    }

    refreshCharts(period) {
        // This would typically make an API call to get new data
        // For demo purposes, we'll simulate data updates
        if (window.usageChart) {
            window.usageChart.data.datasets[0].data = this.generateChartData(period);
            window.usageChart.update();
        }
    }

    generateChartData(period) {
        const dataPoints = period === '7d' ? 7 : period === '30d' ? 30 : 90;
        return Array.from({ length: dataPoints }, () => Math.floor(Math.random() * 100) + 50);
    }

    updateIndustryComparison(industry) {
        const benchmarkData = {
            technology: { score: 85, label: 'Technology Industry' },
            finance: { score: 78, label: 'Finance Industry' },
            healthcare: { score: 82, label: 'Healthcare Industry' },
            marketing: { score: 88, label: 'Marketing Industry' },
            engineering: { score: 86, label: 'Engineering Industry' }
        };

        const data = benchmarkData[industry];
        if (data) {
            const benchmarkItem = document.querySelector('.benchmark-item');
            if (benchmarkItem) {
                benchmarkItem.querySelector('.benchmark-label').textContent = data.label;
                benchmarkItem.querySelector('.benchmark-fill').style.width = `${data.score}%`;
                benchmarkItem.querySelector('.benchmark-value').textContent = `${data.score}%`;
            }
        }
    }

    setupDataUpdates() {
        // Simulate real-time data updates
        setInterval(() => {
            this.updateLiveData();
        }, 5000);
    }

    updateLiveData() {
        // Update random metrics with small changes
        const elements = [
            { id: 'totalUsers', base: 12546 },
            { id: 'totalAnalyses', base: 45892 },
            { id: 'totalWebsites', base: 8234 }
        ];

        elements.forEach(({ id, base }) => {
            const element = document.getElementById(id);
            if (element) {
                const change = Math.floor((Math.random() - 0.5) * 100);
                const newValue = base + change;
                if (newValue > 0) {
                    element.textContent = newValue.toLocaleString();
                }
            }
        });
    }

    copyEndpoint(serviceType) {
        const endpoints = {
            'ats': 'http://localhost:8000/api/v1/analyze',
            'website': 'http://localhost:8080/api/v1/upload'
        };

        const endpoint = endpoints[serviceType];
        if (endpoint) {
            navigator.clipboard.writeText(endpoint).then(() => {
                this.showToast('Endpoint copied to clipboard!', 'success');
            }).catch(() => {
                this.showToast('Failed to copy endpoint', 'error');
            });
        }
    }

    showToast(message, type = 'info', duration = 3000) {
        const toast = this.createToast(message, type);
        document.body.appendChild(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 100);

        // Remove toast
        setTimeout(() => {
            toast.classList.add('removing');
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, duration);
    }

    createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: 'fas fa-check',
            error: 'fas fa-times',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <div class="toast-icon">
                <i class="${icons[type] || icons.info}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        return toast;
    }

    handleResize() {
        // Handle responsive adjustments
        if (window.innerWidth < 768 && document.getElementById('navMenu').classList.contains('active')) {
            document.getElementById('navMenu').classList.remove('active');
            document.getElementById('navToggle').classList.remove('active');
        }
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Global functions for HTML onclick handlers
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        dashboard.scrollToElement(element);
    }
}

function openService(serviceType) {
    dashboard.openService(serviceType);
}

function closeModal() {
    dashboard.closeModal();
}

function copyEndpoint(serviceType) {
    dashboard.copyEndpoint(serviceType);
}

// Initialize dashboard when DOM is loaded
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new ZexDashboard();
    
    // Add some demo functionality
    console.log('🚀 Zex Dashboard initialized successfully!');
    console.log('Available themes: light, dark, futuristic');
    console.log('Toggle themes by clicking the theme button in the navigation');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, pause updates
        console.log('Dashboard paused');
    } else {
        // Page is visible, resume updates
        console.log('Dashboard resumed');
        if (dashboard) {
            dashboard.updateMetrics();
        }
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ZexDashboard;
}
