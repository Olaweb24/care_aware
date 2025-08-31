// Chart.js integration and chart utilities
const Charts = {
    // Chart instances storage
    instances: {},
    
    // Default chart configuration
    defaultConfig: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    borderDash: [2, 2]
                }
            }
        }
    },
    
    // Health theme colors
    colors: {
        primary: '#1e88e5',
        secondary: '#26a69a',
        accent: '#66bb6a',
        warning: '#ff9800',
        danger: '#f44336',
        success: '#4caf50',
        info: '#00bcd4'
    },
    
    // Create lifestyle tracking chart
    createLifestyleChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const config = {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'Sleep (hours)',
                        data: data.sleep_data || [],
                        borderColor: this.colors.primary,
                        backgroundColor: this.colors.primary + '20',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Exercise (minutes)',
                        data: data.exercise_data || [],
                        borderColor: this.colors.accent,
                        backgroundColor: this.colors.accent + '20',
                        tension: 0.4,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Water (glasses)',
                        data: data.water_data || [],
                        borderColor: this.colors.info,
                        backgroundColor: this.colors.info + '20',
                        tension: 0.4,
                        yAxisID: 'y2'
                    }
                ]
            },
            options: {
                ...this.defaultConfig,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Date'
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Sleep (hours)'
                        },
                        beginAtZero: true,
                        max: 12
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Exercise (minutes)'
                        },
                        beginAtZero: true,
                        max: 120,
                        grid: {
                            drawOnChartArea: false,
                        },
                    },
                    y2: {
                        type: 'linear',
                        display: false,
                        beginAtZero: true,
                        max: 15
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                if (context.datasetIndex === 0) return 'hours';
                                if (context.datasetIndex === 1) return 'minutes';
                                if (context.datasetIndex === 2) return 'glasses';
                                return '';
                            }
                        }
                    }
                }
            }
        };
        
        this.instances[canvasId] = new Chart(ctx, config);
        return this.instances[canvasId];
    },
    
    // Create weekly summary chart
    createWeeklySummaryChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const config = {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'Sleep Quality Score',
                        data: data.sleep_scores || [],
                        backgroundColor: this.colors.primary + '80',
                        borderColor: this.colors.primary,
                        borderWidth: 2
                    },
                    {
                        label: 'Activity Score',
                        data: data.activity_scores || [],
                        backgroundColor: this.colors.accent + '80',
                        borderColor: this.colors.accent,
                        borderWidth: 2
                    },
                    {
                        label: 'Hydration Score',
                        data: data.hydration_scores || [],
                        backgroundColor: this.colors.info + '80',
                        borderColor: this.colors.info,
                        borderWidth: 2
                    }
                ]
            },
            options: {
                ...this.defaultConfig,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Score (0-100)'
                        },
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        };
        
        this.instances[canvasId] = new Chart(ctx, config);
        return this.instances[canvasId];
    },
    
    // Create health metrics donut chart
    createHealthMetricsChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const config = {
            type: 'doughnut',
            data: {
                labels: data.labels || ['Sleep', 'Exercise', 'Hydration', 'Nutrition'],
                datasets: [{
                    data: data.values || [80, 65, 90, 75],
                    backgroundColor: [
                        this.colors.primary,
                        this.colors.accent,
                        this.colors.info,
                        this.colors.warning
                    ],
                    borderWidth: 3,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        };
        
        this.instances[canvasId] = new Chart(ctx, config);
        return this.instances[canvasId];
    },
    
    // Create goal progress chart
    createGoalProgressChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const config = {
            type: 'radar',
            data: {
                labels: data.labels || ['Sleep', 'Exercise', 'Hydration', 'Nutrition', 'Stress Management'],
                datasets: [
                    {
                        label: 'Current Week',
                        data: data.current || [8, 7, 9, 6, 5],
                        backgroundColor: this.colors.primary + '20',
                        borderColor: this.colors.primary,
                        pointBackgroundColor: this.colors.primary,
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: this.colors.primary
                    },
                    {
                        label: 'Goals',
                        data: data.goals || [10, 10, 10, 10, 10],
                        backgroundColor: this.colors.accent + '20',
                        borderColor: this.colors.accent,
                        pointBackgroundColor: this.colors.accent,
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: this.colors.accent
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            stepSize: 2
                        }
                    }
                }
            }
        };
        
        this.instances[canvasId] = new Chart(ctx, config);
        return this.instances[canvasId];
    },
    
    // Update chart data
    updateChart(canvasId, newData) {
        const chart = this.instances[canvasId];
        if (!chart) return;
        
        // Update data
        if (newData.labels) {
            chart.data.labels = newData.labels;
        }
        
        if (newData.datasets) {
            newData.datasets.forEach((dataset, index) => {
                if (chart.data.datasets[index]) {
                    chart.data.datasets[index].data = dataset.data;
                }
            });
        }
        
        chart.update();
    },
    
    // Destroy specific chart
    destroyChart(canvasId) {
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
            delete this.instances[canvasId];
        }
    },
    
    // Destroy all charts
    destroyAllCharts() {
        Object.keys(this.instances).forEach(canvasId => {
            this.destroyChart(canvasId);
        });
    },
    
    // Utility: Calculate health scores
    calculateHealthScores(logs) {
        if (!logs || logs.length === 0) return { sleep_scores: [], activity_scores: [], hydration_scores: [] };
        
        const scores = {
            sleep_scores: [],
            activity_scores: [],
            hydration_scores: []
        };
        
        logs.forEach(log => {
            // Sleep score (0-100 based on 7-9 hours being optimal)
            const sleepScore = Math.min(100, Math.max(0, 
                log.sleep_hours >= 7 && log.sleep_hours <= 9 ? 100 :
                log.sleep_hours < 7 ? (log.sleep_hours / 7) * 100 :
                (9 / log.sleep_hours) * 100
            ));
            
            // Activity score (0-100 based on 30+ minutes being optimal)
            const activityScore = Math.min(100, (log.exercise_minutes / 60) * 100);
            
            // Hydration score (0-100 based on 8+ glasses being optimal)
            const hydrationScore = Math.min(100, (log.water_glasses / 8) * 100);
            
            scores.sleep_scores.push(Math.round(sleepScore));
            scores.activity_scores.push(Math.round(activityScore));
            scores.hydration_scores.push(Math.round(hydrationScore));
        });
        
        return scores;
    }
};

// Export for global access
window.Charts = Charts;

// Initialize Chart.js defaults
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#6c757d';
}
