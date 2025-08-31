// Dashboard-specific functionality
const Dashboard = {
    charts: {},
    
    init() {
        this.loadDashboardData();
        this.setupRefreshInterval();
        this.setupCharts();
    },
    
    async loadDashboardData() {
        await Promise.all([
            this.loadHealthTips(),
            this.loadWeatherData(),
            this.loadHealthAlerts(),
            this.loadLifestyleStats()
        ]);
    },
    
    async loadHealthTips() {
        const container = document.getElementById('health-tips');
        if (!container) return;
        
        try {
            App.showLoading(container);
            const response = await App.api('/get-tips', { method: 'POST' });
            const data = await response.json();
            
            if (response.ok) {
                App.renderHealthTips(data.tips, container);
            } else {
                container.innerHTML = '<p class="text-danger">Unable to load health tips</p>';
            }
        } catch (error) {
            console.error('Health tips error:', error);
            container.innerHTML = '<p class="text-danger">Error loading health tips</p>';
        }
    },
    
    async loadWeatherData() {
        const container = document.getElementById('weather-widget');
        if (!container) return;
        
        try {
            const response = await App.api('/weather');
            const data = await response.json();
            
            if (response.ok) {
                App.renderWeather(data, container);
            } else {
                container.innerHTML = '<p class="text-warning">Weather data unavailable</p>';
            }
        } catch (error) {
            console.error('Weather error:', error);
            container.innerHTML = '<p class="text-warning">Weather data unavailable</p>';
        }
    },
    
    async loadHealthAlerts() {
        const container = document.getElementById('health-alerts');
        if (!container) return;
        
        try {
            const response = await App.api('/alerts');
            const data = await response.json();
            
            if (response.ok) {
                App.renderAlerts(data.alerts, container);
            } else {
                container.innerHTML = '<p class="text-info">No alerts available</p>';
            }
        } catch (error) {
            console.error('Alerts error:', error);
            container.innerHTML = '<p class="text-warning">Unable to load alerts</p>';
        }
    },
    
    async loadLifestyleStats() {
        try {
            const response = await App.api('/lifestyle?limit=7');
            const data = await response.json();
            
            if (response.ok && data.logs) {
                this.updateLifestyleStats(data.logs);
            }
        } catch (error) {
            console.error('Lifestyle stats error:', error);
        }
    },
    
    updateLifestyleStats(logs) {
        if (!logs || logs.length === 0) return;
        
        // Calculate averages
        const avgSleep = logs.reduce((sum, log) => sum + log.sleep_hours, 0) / logs.length;
        const avgExercise = logs.reduce((sum, log) => sum + log.exercise_minutes, 0) / logs.length;
        const avgWater = logs.reduce((sum, log) => sum + log.water_glasses, 0) / logs.length;
        
        // Update stat cards
        this.updateStatCard('avg-sleep', avgSleep.toFixed(1), 'hours');
        this.updateStatCard('avg-exercise', Math.round(avgExercise), 'minutes');
        this.updateStatCard('avg-water', Math.round(avgWater), 'glasses');
        this.updateStatCard('total-logs', logs.length, 'entries');
    },
    
    updateStatCard(id, value, unit) {
        const card = document.getElementById(id);
        if (card) {
            const numberElement = card.querySelector('.stat-number');
            const labelElement = card.querySelector('.stat-label');
            
            if (numberElement) numberElement.textContent = value;
            if (labelElement && unit) labelElement.textContent = unit;
        }
    },
    
    setupCharts() {
        // Initialize lifestyle chart if container exists
        const chartContainer = document.getElementById('lifestyle-chart');
        if (chartContainer) {
            this.loadLifestyleChart();
        }
    },
    
    async loadLifestyleChart() {
        try {
            const response = await App.api('/lifestyle_chart_data');
            const data = await response.json();
            
            if (response.ok) {
                Charts.createLifestyleChart('lifestyle-chart', data);
            }
        } catch (error) {
            console.error('Chart data error:', error);
        }
    },
    
    setupRefreshInterval() {
        // Refresh data every 5 minutes
        setInterval(() => {
            this.loadWeatherData();
            this.loadHealthAlerts();
        }, 5 * 60 * 1000);
        
        // Refresh tips every 30 minutes
        setInterval(() => {
            this.loadHealthTips();
        }, 30 * 60 * 1000);
    },
    
    // Quick actions
    async logQuickEntry(type, value) {
        const today = new Date().toISOString().split('T')[0];
        const data = {
            date: today,
            sleep_hours: type === 'sleep' ? value : 8,
            exercise_minutes: type === 'exercise' ? value : 30,
            water_glasses: type === 'water' ? value : 8,
            meals: 'Quick entry',
            notes: `Quick ${type} entry: ${value}`
        };
        
        try {
            const response = await App.api('/log-lifestyle', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                App.showSuccess(`${type} logged successfully!`);
                this.loadLifestyleStats();
                this.loadLifestyleChart();
            } else {
                const error = await response.json();
                App.showError(error.error || 'Failed to log entry');
            }
        } catch (error) {
            console.error('Quick log error:', error);
            App.showError('Network error occurred');
        }
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.classList.contains('dashboard-page')) {
        Dashboard.init();
    }
});

// Export for global access
window.Dashboard = Dashboard;
