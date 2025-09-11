// Theme management: toggle between light and dark modes and persist preference
(function () {
    'use strict';

    const storageKey = 'dashboard-theme';

    document.addEventListener('DOMContentLoaded', () => {
        const saved = localStorage.getItem(storageKey);
        if (saved) {
            applyTheme(saved);
        } else {
            const initial = document.body.getAttribute('data-theme') || 'light';
            applyTheme(initial);
        }

        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('click', () => {
                const current = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                applyTheme(current);
            });
        }
    });

    function applyTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        document.body.className = 'theme-' + theme;
        localStorage.setItem(storageKey, theme);
    }
})();

