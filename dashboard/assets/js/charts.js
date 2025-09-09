// Charts Configuration and Management
class ChartManager {
    constructor() {
        this.charts = {};
        this.colors = this.getThemeColors();
        this.initializeCharts();
        this.setupThemeListener();
    }

    getThemeColors() {
        const theme = document.body.className;
        
        const colorSchemes = {
            'theme-light': {
                primary: '#3b82f6',
                secondary: '#8b5cf6',
                accent: '#06b6d4',
                success: '#10b981',
                warning: '#f59e0b',
                error: '#ef4444',
                text: '#1f2937',
                textSecondary: '#6b7280',
                background: '#ffffff',
                backgroundSecondary: '#f9fafb',
                border: '#e5e7eb',
                gradient: ['#3b82f6', '#8b5cf6', '#06b6d4']
            },
            'theme-dark': {
                primary: '#60a5fa',
                secondary: '#a78bfa',
                accent: '#22d3ee',
                success: '#34d399',
                warning: '#fbbf24',
                error: '#f87171',
                text: '#f8fafc',
                textSecondary: '#cbd5e1',
                background: '#0f1419',
                backgroundSecondary: '#1a1f2e',
                border: '#334155',
                gradient: ['#60a5fa', '#a78bfa', '#22d3ee']
            },
            'theme-futuristic': {
                primary: '#00ffff',
                secondary: '#00ccff',
                accent: '#0099ff',
                success: '#00ff99',
                warning: '#ffcc00',
                error: '#ff3366',
                text: '#00ffff',
                textSecondary: '#0099cc',
                background: '#000011',
                backgroundSecondary: '#001122',
                border: '#003366',
                gradient: ['#00ffff', '#00ccff', '#0099ff']
            }
        };

        return colorSchemes[theme] || colorSchemes['theme-dark'];
    }

    initializeCharts() {
        this.createUsageChart();
        this.createScoreChart();
        this.createPerformanceChart();
        this.createRealtimeChart();
    }

    createUsageChart() {
        const ctx = document.getElementById('usageChart');
        if (!ctx) return;

        const data = {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [
                {
                    label: 'ATS Analyses',
                    data: [65, 78, 90, 85, 92, 88, 95],
                    borderColor: this.colors.primary,
                    backgroundColor: this.hexToRgba(this.colors.primary, 0.1),
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: this.colors.background,
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                },
                {
                    label: 'Websites Generated',
                    data: [45, 52, 48, 61, 55, 67, 72],
                    borderColor: this.colors.secondary,
                    backgroundColor: this.hexToRgba(this.colors.secondary, 0.1),
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.colors.secondary,
                    pointBorderColor: this.colors.background,
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        };

        const options = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: this.colors.text,
                        font: {
                            family: 'Inter',
                            size: 12,
                            weight: '500'
                        },
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: this.colors.backgroundSecondary,
                    titleColor: this.colors.text,
                    bodyColor: this.colors.textSecondary,
                    borderColor: this.colors.border,
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return `${context[0].label}`;
                        },
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        color: this.hexToRgba(this.colors.border, 0.3),
                        drawBorder: false
                    },
                    ticks: {
                        color: this.colors.textSecondary,
                        font: {
                            family: 'Inter',
                            size: 11
                        }
                    }
                },
                y: {
                    display: true,
                    beginAtZero: true,
                    grid: {
                        color: this.hexToRgba(this.colors.border, 0.3),
                        drawBorder: false
                    },
                    ticks: {
                        color: this.colors.textSecondary,
                        font: {
                            family: 'Inter',
                            size: 11
                        }
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart'
            }
        };

        this.charts.usage = new Chart(ctx, {
            type: 'line',
            data: data,
            options: options
        });

        // Store reference for global access
        window.usageChart = this.charts.usage;
    }

    createScoreChart() {
        const ctx = document.getElementById('scoreChart');
        if (!ctx) return;

        const data = {
            labels: ['0-20', '21-40', '41-60', '61-80', '81-100'],
            datasets: [{
                label: 'ATS Score Distribution',
                data: [5, 15, 25, 35, 45],
                backgroundColor: [
                    this.colors.error,
                    this.colors.warning,
                    this.colors.accent,
                    this.colors.secondary,
                    this.colors.success
                ],
                borderWidth: 0,
                borderRadius: 4,
                borderSkipped: false
            }]
        };

        const options = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: this.colors.backgroundSecondary,
                    titleColor: this.colors.text,
                    bodyColor: this.colors.textSecondary,
                    borderColor: this.colors.border,
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        title: function(context) {
                            return `Score Range: ${context[0].label}`;
                        },
                        label: function(context) {
                            return `Count: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: this.colors.textSecondary,
                        font: {
                            family: 'Inter',
                            size: 11
                        }
                    }
                },
                y: {
                    display: false,
                    beginAtZero: true
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart',
                delay: (context) => context.dataIndex * 100
            }
        };

        this.charts.score = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: options
        });
    }

    createPerformanceChart() {
        // Create a performance metrics chart (could be added to dashboard)
        const performanceData = {
            labels: ['Response Time', 'Throughput', 'Accuracy', 'Reliability'],
            datasets: [{
                label: 'Current Performance',
                data: [95, 88, 92, 96],
                backgroundColor: this.hexToRgba(this.colors.primary, 0.2),
                borderColor: this.colors.primary,
                borderWidth: 2,
                pointBackgroundColor: this.colors.primary,
                pointBorderColor: this.colors.background,
                pointBorderWidth: 2,
                pointRadius: 6
            }, {
                label: 'Target Performance',
                data: [98, 95, 98, 99],
                backgroundColor: this.hexToRgba(this.colors.success, 0.2),
                borderColor: this.colors.success,
                borderWidth: 2,
                borderDash: [5, 5],
                pointBackgroundColor: this.colors.success,
                pointBorderColor: this.colors.background,
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        };

        // Store for potential use
        this.performanceData = performanceData;
    }

    createRealtimeChart() {
        // Create a real-time data visualization
        const realtimeData = {
            labels: [],
            datasets: [{
                label: 'Live Requests',
                data: [],
                borderColor: this.colors.accent,
                backgroundColor: this.hexToRgba(this.colors.accent, 0.1),
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 4
            }]
        };

        // Initialize with some data points
        const now = new Date();
        for (let i = 59; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 1000);
            realtimeData.labels.push(this.formatTime(time));
            realtimeData.data = Math.floor(Math.random() * 100) + 50;
        }

        this.realtimeData = realtimeData;
        
        // Start real-time updates
        this.startRealtimeUpdates();
    }

    startRealtimeUpdates() {
        setInterval(() => {
            this.updateRealtimeData();
        }, 2000);
    }

    updateRealtimeData() {
        if (!this.realtimeData) return;

        const now = new Date();
        const newValue = Math.floor(Math.random() * 100) + 50;

        // Add new data point
        this.realtimeData.labels.push(this.formatTime(now));
        this.realtimeData.datasets[0].data.push(newValue);

        // Remove old data points (keep last 60)
        if (this.realtimeData.labels.length > 60) {
            this.realtimeData.labels.shift();
            this.realtimeData.datasets[0].data.shift();
        }

        // Update chart if it exists
        if (this.charts.realtime) {
            this.charts.realtime.update('none');
        }
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { 
            hour12: false, 
            minute: '2-digit', 
            second: '2-digit' 
        });
    }

    updateTheme() {
        this.colors = this.getThemeColors();
        
        // Update all charts with new colors
        Object.keys(this.charts).forEach(chartKey => {
            this.updateChartColors(this.charts[chartKey]);
        });
    }

    updateChartColors(chart) {
        if (!chart) return;

        // Update dataset colors
        chart.data.datasets.forEach((dataset, index) => {
            if (dataset.borderColor) {
                dataset.borderColor = this.colors.gradient[index % this.colors.gradient.length];
            }
            if (dataset.backgroundColor && typeof dataset.backgroundColor === 'string') {
                dataset.backgroundColor = this.hexToRgba(
                    this.colors.gradient[index % this.colors.gradient.length], 
                    0.1
                );
            }
            if (dataset.pointBackgroundColor) {
                dataset.pointBackgroundColor = this.colors.gradient[index % this.colors.gradient.length];
            }
            if (dataset.pointBorderColor) {
                dataset.pointBorderColor = this.colors.background;
            }
        });

        // Update scale colors
        if (chart.options.scales) {
            ['x', 'y'].forEach(axis => {
                if (chart.options.scales[axis]) {
                    if (chart.options.scales[axis].ticks) {
                        chart.options.scales[axis].ticks.color = this.colors.textSecondary;
                    }
                    if (chart.options.scales[axis].grid) {
                        chart.options.scales[axis].grid.color = this.hexToRgba(this.colors.border, 0.3);
                    }
                }
            });
        }

        // Update legend colors
        if (chart.options.plugins?.legend?.labels) {
            chart.options.plugins.legend.labels.color = this.colors.text;
        }

        // Update tooltip colors
        if (chart.options.plugins?.tooltip) {
            const tooltip = chart.options.plugins.tooltip;
            tooltip.backgroundColor = this.colors.backgroundSecondary;
            tooltip.titleColor = this.colors.text;
            tooltip.bodyColor = this.colors.textSecondary;
            tooltip.borderColor = this.colors.border;
        }

        chart.update();
    }

    setupThemeListener() {
        window.addEventListener('themeChange', () => {
            setTimeout(() => {
                this.updateTheme();
            }, 100);
        });
    }

    hexToRgba(hex, alpha = 1) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        if (!result) return hex;
        
        const r = parseInt(result[1], 16);
        const g = parseInt(result[2], 16);
        const b = parseInt(result[3], 16);
        
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // Public methods for external chart manipulation
    updateChartData(chartName, newData) {
        if (this.charts[chartName]) {
            this.charts[chartName].data = newData;
            this.charts[chartName].update();
        }
    }

    addDataPoint(chartName, label, value) {
        if (this.charts[chartName]) {
            this.charts[chartName].data.labels.push(label);
            this.charts[chartName].data.datasets[0].data.push(value);
            this.charts[chartName].update();
        }
    }

    generateSampleData(points = 7) {
        return Array.from({ length: points }, () => 
            Math.floor(Math.random() * 100) + 20
        );
    }

    // Chart export functionality
    exportChart(chartName, filename) {
        if (this.charts[chartName]) {
            const canvas = this.charts[chartName].canvas;
            const url = canvas.toDataURL('image/png');
            
            const link = document.createElement('a');
            link.download = filename || `${chartName}-chart.png`;
            link.href = url;
            link.click();
        }
    }

    // Destroy all charts (for cleanup)
    destroyAll() {
        Object.keys(this.charts).forEach(chartKey => {
            if (this.charts[chartKey]) {
                this.charts[chartKey].destroy();
            }
        });
        this.charts = {};
    }
}

// Initialize charts when DOM is loaded
let chartManager;
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for other scripts to load
    setTimeout(() => {
        chartManager = new ChartManager();
        console.log('📊 Chart Manager initialized');
    }, 500);
});

// Global chart functions
function exportChart(chartName, filename) {
    if (chartManager) {
        chartManager.exportChart(chartName, filename);
    }
}

function updateChartPeriod(period) {
    if (chartManager && chartManager.charts.usage) {
        const newData = chartManager.generateSampleData(
            period === '7d' ? 7 : period === '30d' ? 30 : 90
        );
        chartManager.charts.usage.data.datasets[0].data = newData;
        chartManager.charts.usage.update();
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartManager;
}
