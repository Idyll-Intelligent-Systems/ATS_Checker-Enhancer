// Dashboard interactions and utilities
// Handles navigation toggles, service modals and clipboard helpers

(function () {
    'use strict';

    // Ensure DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        setupNavigation();
        setupDropdowns();
    });

    function setupNavigation() {
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.getElementById('navMenu');
        if (!navToggle || !navMenu) return;

        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }

    function setupDropdowns() {
        const dropdownItems = document.querySelectorAll('.nav-item.dropdown');
        const menus = document.querySelectorAll('.dropdown-menu');

        const closeAll = () => {
            dropdownItems.forEach(item => item.classList.remove('open'));
            menus.forEach(menu => menu.classList.remove('active'));
        };

        dropdownItems.forEach(item => {
            const menu = document.getElementById(item.dataset.dropdown);
            if (!menu) return;

            item.addEventListener('click', e => {
                e.stopPropagation();
                const isOpen = item.classList.contains('open');
                closeAll();
                if (!isOpen) {
                    item.classList.add('open');
                    menu.classList.add('active');
                }
            });
        });

        document.addEventListener('click', closeAll);
    }

    // Smooth scroll helper used by buttons
    window.scrollToSection = function (id) {
        const target = document.getElementById(id);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    };

    // Service modal management
    const serviceMap = {
        ats: {
            title: 'Zex ATS AI',
            url: 'http://localhost:8000/'
        },
        website: {
            title: 'Dynamic Website Generator',
            url: 'http://localhost:8080/'
        }
    };

    window.openService = function (service) {
        const cfg = serviceMap[service];
        const modal = document.getElementById('serviceModal');
        const frame = document.getElementById('serviceFrame');
        const title = document.getElementById('modalTitle');
        if (!cfg || !modal || !frame || !title) return;

        title.textContent = cfg.title;
        frame.src = cfg.url;
        modal.classList.add('active');
    };

    window.closeModal = function () {
        const modal = document.getElementById('serviceModal');
        const frame = document.getElementById('serviceFrame');
        if (modal) modal.classList.remove('active');
        if (frame) frame.src = '';
    };

    // Endpoint copy helper
    const endpointMap = {
        ats: 'http://localhost:8000/api/v1/analyze',
        website: 'http://localhost:8080/api/v1/upload'
    };

    window.copyEndpoint = function (type) {
        const endpoint = endpointMap[type];
        if (!endpoint) return;

        const copyPromise = navigator.clipboard
            ? navigator.clipboard.writeText(endpoint)
            : legacyCopy(endpoint);

        copyPromise
            .then(() => showCopyFeedback())
            .catch(() => showCopyFeedback());
    };

    function legacyCopy(text) {
        return new Promise(resolve => {
            const temp = document.createElement('textarea');
            temp.value = text;
            temp.setAttribute('readonly', '');
            temp.style.position = 'absolute';
            temp.style.left = '-9999px';
            document.body.appendChild(temp);
            temp.select();
            document.execCommand('copy');
            document.body.removeChild(temp);
            resolve();
        });
    }

    function showCopyFeedback() {
        const btn = window.event ? window.event.currentTarget : null;
        if (!btn) return;
        btn.classList.add('copied');
        setTimeout(() => btn.classList.remove('copied'), 2000);
    }
})();

