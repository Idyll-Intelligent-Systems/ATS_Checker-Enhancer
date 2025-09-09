// Theme Management System
class ThemeManager {
    constructor() {
        this.themes = {
            'theme-light': {
                name: 'Light',
                icon: 'fas fa-sun',
                description: 'Clean and minimal light theme'
            },
            'theme-dark': {
                name: 'Dark',
                icon: 'fas fa-moon',
                description: 'Modern dark theme for reduced eye strain'
            },
            'theme-futuristic': {
                name: 'Futuristic',
                icon: 'fas fa-rocket',
                description: 'Cyberpunk-inspired neon theme'
            }
        };
        
        this.currentTheme = this.getCurrentTheme();
        this.preferredColorScheme = this.getPreferredColorScheme();
        this.systemThemeListener = null;
        
        this.init();
    }

    init() {
        this.setupThemeToggle();
        this.setupSystemThemeListener();
        this.setupThemePreview();
        this.applyStoredTheme();
        this.createThemeSelector();
    }

    getCurrentTheme() {
        return document.body.className || 'theme-dark';
    }

    getPreferredColorScheme() {
        if (window.matchMedia) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return 'dark';
    }

    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.cycleTheme();
            });

            // Handle keyboard navigation
            themeToggle.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.cycleTheme();
                }
            });
        }
    }

    setupSystemThemeListener() {
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            this.systemThemeListener = (e) => {
                // Only auto-switch if user hasn't manually selected a theme
                const hasManualPreference = localStorage.getItem('zex-theme-manual');
                if (!hasManualPreference) {
                    this.setTheme(e.matches ? 'theme-dark' : 'theme-light');
                }
            };
            
            darkModeQuery.addEventListener('change', this.systemThemeListener);
        }
    }

    setupThemePreview() {
        // Create theme preview functionality for settings page
        const themeCards = document.querySelectorAll('.theme-card');
        themeCards.forEach(card => {
            card.addEventListener('click', () => {
                const theme = card.dataset.theme;
                if (theme && this.themes[theme]) {
                    this.setTheme(theme, true);
                }
            });

            card.addEventListener('mouseenter', () => {
                this.previewTheme(card.dataset.theme);
            });

            card.addEventListener('mouseleave', () => {
                this.stopPreview();
            });
        });
    }

    applyStoredTheme() {
        const storedTheme = localStorage.getItem('zex-theme');
        if (storedTheme && this.themes[storedTheme]) {
            this.setTheme(storedTheme, false);
        } else {
            // Apply system preference if no stored theme
            const systemTheme = this.preferredColorScheme === 'dark' ? 'theme-dark' : 'theme-light';
            this.setTheme(systemTheme, false);
        }
    }

    createThemeSelector() {
        const themeSelector = document.getElementById('themeSelector');
        if (!themeSelector) return;

        // Create theme options
        Object.keys(this.themes).forEach(themeKey => {
            const theme = this.themes[themeKey];
            const option = document.createElement('div');
            option.className = 'theme-option';
            option.dataset.theme = themeKey;
            
            option.innerHTML = `
                <div class="theme-preview ${themeKey}">
                    <div class="theme-preview-header">
                        <div class="theme-preview-dots">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                    <div class="theme-preview-content">
                        <div class="theme-preview-sidebar"></div>
                        <div class="theme-preview-main">
                            <div class="theme-preview-card"></div>
                            <div class="theme-preview-card"></div>
                        </div>
                    </div>
                </div>
                <div class="theme-info">
                    <div class="theme-name">
                        <i class="${theme.icon}"></i>
                        ${theme.name}
                    </div>
                    <div class="theme-description">${theme.description}</div>
                </div>
                <div class="theme-actions">
                    <button class="btn btn-sm theme-apply-btn" data-theme="${themeKey}">
                        Apply
                    </button>
                </div>
            `;

            option.addEventListener('click', () => {
                this.setTheme(themeKey, true);
            });

            themeSelector.appendChild(option);
        });

        // Add event listeners for apply buttons
        themeSelector.addEventListener('click', (e) => {
            if (e.target.matches('.theme-apply-btn')) {
                const theme = e.target.dataset.theme;
                this.setTheme(theme, true);
            }
        });
    }

    cycleTheme() {
        const themeKeys = Object.keys(this.themes);
        const currentIndex = themeKeys.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themeKeys.length;
        const nextTheme = themeKeys[nextIndex];
        
        this.setTheme(nextTheme, true);
    }

    setTheme(themeName, isManualSelection = false) {
        if (!this.themes[themeName]) return;

        // Remove current theme class
        Object.keys(this.themes).forEach(theme => {
            document.body.classList.remove(theme);
        });

        // Apply new theme
        document.body.className = themeName;
        this.currentTheme = themeName;

        // Store preference
        localStorage.setItem('zex-theme', themeName);
        if (isManualSelection) {
            localStorage.setItem('zex-theme-manual', 'true');
        }

        // Update theme toggle icon
        this.updateThemeToggleIcon();

        // Update theme selector if exists
        this.updateThemeSelector();

        // Dispatch theme change event
        this.dispatchThemeChangeEvent(themeName);

        // Show theme change notification
        if (isManualSelection) {
            this.showThemeChangeNotification(this.themes[themeName].name);
        }

        // Apply theme-specific customizations
        this.applyThemeCustomizations(themeName);
    }

    updateThemeToggleIcon() {
        const themeToggle = document.getElementById('themeToggle');
        if (!themeToggle) return;

        const theme = this.themes[this.currentTheme];
        const iconElement = themeToggle.querySelector('i') || themeToggle;
        
        // Update icon class
        iconElement.className = theme.icon;
        
        // Update tooltip
        themeToggle.setAttribute('title', `Switch to next theme (Current: ${theme.name})`);
    }

    updateThemeSelector() {
        const themeOptions = document.querySelectorAll('.theme-option');
        themeOptions.forEach(option => {
            option.classList.toggle('active', option.dataset.theme === this.currentTheme);
        });
    }

    dispatchThemeChangeEvent(themeName) {
        const event = new CustomEvent('themeChange', {
            detail: {
                theme: themeName,
                themeData: this.themes[themeName]
            }
        });
        window.dispatchEvent(event);
    }

    showThemeChangeNotification(themeName) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.innerHTML = `
            <div class="theme-notification-content">
                <i class="${this.themes[this.currentTheme].icon}"></i>
                <span>Switched to ${themeName} theme</span>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);

        // Remove after delay
        setTimeout(() => {
            notification.classList.add('hide');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 2000);
    }

    applyThemeCustomizations(themeName) {
        // Apply theme-specific customizations
        switch(themeName) {
            case 'theme-futuristic':
                this.applyFuturisticEffects();
                break;
            case 'theme-dark':
                this.applyDarkThemeEffects();
                break;
            case 'theme-light':
                this.applyLightThemeEffects();
                break;
        }

        // Update meta theme color
        this.updateMetaThemeColor(themeName);
    }

    applyFuturisticEffects() {
        // Add special effects for futuristic theme
        const heroSection = document.querySelector('.hero');
        if (heroSection) {
            heroSection.classList.add('futuristic-effects');
        }

        // Add glow effects to interactive elements
        const interactiveElements = document.querySelectorAll('.btn, .service-card, .metric-card');
        interactiveElements.forEach(el => {
            el.classList.add('futuristic-glow');
        });
    }

    applyDarkThemeEffects() {
        // Remove futuristic effects
        this.removeFuturisticEffects();
        
        // Add dark theme specific effects
        const cards = document.querySelectorAll('.service-card, .metric-card, .api-card');
        cards.forEach(card => {
            card.classList.add('dark-theme-shadow');
        });
    }

    applyLightThemeEffects() {
        // Remove futuristic effects
        this.removeFuturisticEffects();
        
        // Add light theme specific effects
        const cards = document.querySelectorAll('.service-card, .metric-card, .api-card');
        cards.forEach(card => {
            card.classList.remove('dark-theme-shadow');
        });
    }

    removeFuturisticEffects() {
        const heroSection = document.querySelector('.hero');
        if (heroSection) {
            heroSection.classList.remove('futuristic-effects');
        }

        const glowElements = document.querySelectorAll('.futuristic-glow');
        glowElements.forEach(el => {
            el.classList.remove('futuristic-glow');
        });
    }

    updateMetaThemeColor(themeName) {
        let themeColor;
        switch(themeName) {
            case 'theme-light':
                themeColor = '#ffffff';
                break;
            case 'theme-dark':
                themeColor = '#0f1419';
                break;
            case 'theme-futuristic':
                themeColor = '#000011';
                break;
            default:
                themeColor = '#0f1419';
        }

        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        metaThemeColor.content = themeColor;
    }

    previewTheme(themeName) {
        if (!this.themes[themeName]) return;
        
        // Store current theme
        this.previewMode = {
            originalTheme: this.currentTheme,
            isPreviewActive: true
        };

        // Apply preview theme
        this.setTheme(themeName, false);
    }

    stopPreview() {
        if (this.previewMode && this.previewMode.isPreviewActive) {
            // Restore original theme
            this.setTheme(this.previewMode.originalTheme, false);
            this.previewMode = null;
        }
    }

    // Theme validation and error handling
    validateTheme(themeName) {
        return this.themes.hasOwnProperty(themeName);
    }

    resetToDefault() {
        this.setTheme('theme-dark', true);
        localStorage.removeItem('zex-theme-manual');
    }

    // Accessibility features
    setupAccessibilityFeatures() {
        // High contrast mode detection
        if (window.matchMedia) {
            const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
            highContrastQuery.addEventListener('change', (e) => {
                if (e.matches) {
                    document.body.classList.add('high-contrast');
                } else {
                    document.body.classList.remove('high-contrast');
                }
            });

            // Apply immediately if high contrast is preferred
            if (highContrastQuery.matches) {
                document.body.classList.add('high-contrast');
            }
        }

        // Reduced motion detection
        if (window.matchMedia) {
            const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
            reducedMotionQuery.addEventListener('change', (e) => {
                if (e.matches) {
                    document.body.classList.add('reduced-motion');
                } else {
                    document.body.classList.remove('reduced-motion');
                }
            });

            // Apply immediately if reduced motion is preferred
            if (reducedMotionQuery.matches) {
                document.body.classList.add('reduced-motion');
            }
        }
    }

    // Export/Import theme settings
    exportSettings() {
        return {
            theme: this.currentTheme,
            manual: localStorage.getItem('zex-theme-manual') === 'true',
            timestamp: new Date().toISOString()
        };
    }

    importSettings(settings) {
        if (settings.theme && this.validateTheme(settings.theme)) {
            this.setTheme(settings.theme, settings.manual);
        }
    }

    // Cleanup
    destroy() {
        if (this.systemThemeListener && window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            darkModeQuery.removeEventListener('change', this.systemThemeListener);
        }
    }
}

// Additional CSS for theme notifications and effects
const themeCSS = `
    .theme-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: var(--shadow-xl);
        z-index: 10000;
        transform: translateX(100%);
        opacity: 0;
        transition: all 0.3s ease-out;
    }

    .theme-notification.show {
        transform: translateX(0);
        opacity: 1;
    }

    .theme-notification.hide {
        transform: translateX(100%);
        opacity: 0;
    }

    .theme-notification-content {
        display: flex;
        align-items: center;
        gap: 12px;
        color: var(--text-primary);
        font-weight: 500;
    }

    .theme-notification-content i {
        color: var(--primary-500);
    }

    .theme-option {
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .theme-option:hover,
    .theme-option.active {
        border-color: var(--primary-500);
        background: var(--bg-secondary);
    }

    .theme-preview {
        width: 100%;
        height: 100px;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 12px;
        position: relative;
    }

    .theme-preview.theme-light {
        background: #ffffff;
        color: #1f2937;
    }

    .theme-preview.theme-dark {
        background: #0f1419;
        color: #f8fafc;
    }

    .theme-preview.theme-futuristic {
        background: #000011;
        color: #00ffff;
    }

    .theme-preview-header {
        height: 20px;
        padding: 6px 12px;
        display: flex;
        align-items: center;
    }

    .theme-preview-dots {
        display: flex;
        gap: 4px;
    }

    .theme-preview-dots span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: currentColor;
        opacity: 0.6;
    }

    .theme-preview-content {
        display: flex;
        height: 80px;
        padding: 8px;
        gap: 8px;
    }

    .theme-preview-sidebar {
        width: 30%;
        background: currentColor;
        opacity: 0.1;
        border-radius: 4px;
    }

    .theme-preview-main {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .theme-preview-card {
        flex: 1;
        background: currentColor;
        opacity: 0.15;
        border-radius: 4px;
    }

    .futuristic-glow {
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3) !important;
    }

    .dark-theme-shadow {
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    }

    .high-contrast * {
        border-width: 2px !important;
    }

    .reduced-motion * {
        animation: none !important;
        transition: none !important;
    }

    @media (max-width: 768px) {
        .theme-notification {
            left: 16px;
            right: 16px;
            top: 80px;
            transform: translateY(-100%);
        }

        .theme-notification.show {
            transform: translateY(0);
        }

        .theme-notification.hide {
            transform: translateY(-100%);
        }
    }
`;

// Inject theme CSS
const injectThemeCSS = () => {
    const style = document.createElement('style');
    style.textContent = themeCSS;
    document.head.appendChild(style);
};

// Initialize theme manager
let themeManager;
document.addEventListener('DOMContentLoaded', () => {
    injectThemeCSS();
    themeManager = new ThemeManager();
    console.log('🎨 Theme Manager initialized');
});

// Global theme functions
function setTheme(themeName) {
    if (themeManager) {
        themeManager.setTheme(themeName, true);
    }
}

function resetTheme() {
    if (themeManager) {
        themeManager.resetToDefault();
    }
}

function exportThemeSettings() {
    return themeManager ? themeManager.exportSettings() : null;
}

function importThemeSettings(settings) {
    if (themeManager) {
        themeManager.importSettings(settings);
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
