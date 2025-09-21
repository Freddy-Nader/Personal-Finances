// Dashboard JavaScript with Chart.js Integration
class Dashboard {
    constructor() {
        this.charts = {};
        this.currentPeriod = 'month';
        this.dashboardData = null;
        this.initializeEventListeners();
        this.loadDashboard();
    }

    initializeEventListeners() {
        // Period filter change
        const periodFilter = document.getElementById('periodFilter');
        if (periodFilter) {
            periodFilter.addEventListener('change', (e) => {
                this.currentPeriod = e.target.value;
                this.loadDashboard();
            });
        }

        // Chart control buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('chart-btn')) {
                this.handleChartControl(e.target);
            }
        });
    }

    async loadDashboard() {
        try {
            this.showLoading();

            // Load summary data and charts in parallel
            const [summaryData, balanceChartData, categoryChartData, investmentChartData] = await Promise.all([
                api.getDashboardSummary(this.currentPeriod),
                api.getDashboardCharts('balance_trend', this.currentPeriod),
                api.getDashboardCharts('spending_categories', this.currentPeriod),
                api.getDashboardCharts('investment_performance', this.currentPeriod)
            ]);

            this.dashboardData = summaryData;
            this.updateSummaryCards(summaryData);
            this.updateCharts({
                balance: balanceChartData,
                categories: categoryChartData,
                investments: investmentChartData
            });

            await this.loadRecentTransactions();

        } catch (error) {
            console.error('Failed to load dashboard:', error);
            this.showError('Failed to load dashboard data. Please try again.');
        }
    }

    updateSummaryCards(data) {
        // Total Balance
        const totalBalance = document.getElementById('totalBalance');
        if (totalBalance) {
            totalBalance.textContent = FinanceUtils.formatCurrency(data.total_balance);
        }

        // Credit Available
        const creditAvailable = document.getElementById('creditAvailable');
        if (creditAvailable) {
            creditAvailable.textContent = FinanceUtils.formatCurrency(data.total_credit_available);
        }

        // Investment Value
        const investmentValue = document.getElementById('investmentValue');
        if (investmentValue) {
            investmentValue.textContent = FinanceUtils.formatCurrency(data.total_investments_value);
        }

        // Net Income
        const netIncome = document.getElementById('netIncome');
        if (netIncome) {
            const income = data.period_income - Math.abs(data.period_expenses);
            netIncome.textContent = FinanceUtils.formatCurrency(income, 'USD', true);
        }

        // Update change indicators (mock data for now)
        this.updateChangeIndicators(data);
    }

    updateChangeIndicators(data) {
        // Mock percentage changes - in real implementation, these would come from API
        const changes = {
            balanceChange: this.calculateMockChange(data.total_balance),
            creditChange: this.calculateMockChange(data.total_credit_available),
            investmentChange: this.calculateMockChange(data.total_investments_value),
            incomeChange: this.calculateMockChange(data.period_profit_loss)
        };

        Object.entries(changes).forEach(([elementId, change]) => {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
                element.className = `card-change ${change >= 0 ? 'positive' : 'negative'}`;
            }
        });
    }

    calculateMockChange(value) {
        // Mock calculation - in real app, this would be based on previous period data
        return (Math.random() - 0.5) * 10; // Random change between -5% and +5%
    }

    updateCharts(chartData) {
        this.createBalanceChart(chartData.balance);
        this.createCategoryChart(chartData.categories);
        this.createInvestmentChart(chartData.investments);
    }

    createBalanceChart(data) {
        const ctx = document.getElementById('balanceChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.balance) {
            this.charts.balance.destroy();
        }

        this.charts.balance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || this.getMockLabels(),
                datasets: [{
                    label: 'Balance',
                    data: data.datasets?.[0]?.data || this.getMockBalanceData(),
                    borderColor: '#2383e2',
                    backgroundColor: '#e3f2fd',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return FinanceUtils.formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });
    }

    createCategoryChart(data) {
        const ctx = document.getElementById('categoryChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.categories) {
            this.charts.categories.destroy();
        }

        this.charts.categories = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || this.getMockCategoryLabels(),
                datasets: [{
                    data: data.datasets?.[0]?.data || this.getMockCategoryData(),
                    backgroundColor: [
                        '#2383e2', '#0f7b0f', '#e03e3e', '#ffc400',
                        '#9b59b6', '#e67e22', '#1abc9c', '#34495e'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createInvestmentChart(data) {
        const ctx = document.getElementById('investmentChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.investments) {
            this.charts.investments.destroy();
        }

        this.charts.investments = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || this.getMockInvestmentLabels(),
                datasets: [{
                    label: 'Portfolio Value',
                    data: data.datasets?.[0]?.data || this.getMockInvestmentData(),
                    backgroundColor: '#0f7b0f',
                    borderColor: '#0d6d0d',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return FinanceUtils.formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });
    }

    handleChartControl(button) {
        // Remove active class from all chart buttons in the same container
        const container = button.closest('.chart-controls');
        container.querySelectorAll('.chart-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Add active class to clicked button
        button.classList.add('active');

        // Handle chart type changes (for balance chart)
        const chartType = button.dataset.chart;
        if (chartType && this.charts.balance) {
            // Switch between balance and income/expense view
            this.updateBalanceChartView(chartType);
        }
    }

    async updateBalanceChartView(viewType) {
        try {
            const chartData = await api.getDashboardCharts(
                viewType === 'income' ? 'income_expense' : 'balance_trend',
                this.currentPeriod
            );

            if (viewType === 'income') {
                this.createIncomeExpenseChart(chartData);
            } else {
                this.createBalanceChart(chartData);
            }
        } catch (error) {
            console.error('Failed to update chart view:', error);
        }
    }

    createIncomeExpenseChart(data) {
        const ctx = document.getElementById('balanceChart');
        if (!ctx || !this.charts.balance) return;

        this.charts.balance.destroy();

        this.charts.balance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || this.getMockLabels(),
                datasets: [{
                    label: 'Income',
                    data: data.datasets?.[0]?.data || this.getMockIncomeData(),
                    backgroundColor: '#0f7b0f'
                }, {
                    label: 'Expenses',
                    data: data.datasets?.[1]?.data || this.getMockExpenseData(),
                    backgroundColor: '#e03e3e'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return FinanceUtils.formatCurrency(Math.abs(value));
                            }
                        }
                    }
                }
            }
        });
    }

    async loadRecentTransactions() {
        try {
            const transactions = await api.getTransactions({ limit: 5 });
            this.displayRecentTransactions(transactions.transactions || transactions);
        } catch (error) {
            console.error('Failed to load recent transactions:', error);
            const container = document.getElementById('recentTransactions');
            if (container) {
                container.innerHTML = '<div class="error">Failed to load recent transactions</div>';
            }
        }
    }

    displayRecentTransactions(transactions) {
        const container = document.getElementById('recentTransactions');
        if (!container) return;

        if (!transactions || transactions.length === 0) {
            container.innerHTML = UIComponents.createEmptyState(
                'No recent transactions found',
                'Add Transaction',
                'window.location.href = "transactions.html"'
            );
            return;
        }

        const transactionItems = transactions.map(transaction => {
            const amount = parseFloat(transaction.amount);
            const amountClass = amount >= 0 ? 'text-positive' : 'text-negative';
            const amountText = FinanceUtils.formatCurrency(Math.abs(amount), 'USD', true);
            const date = FinanceUtils.formatDate(transaction.transaction_date, 'short');

            return `
                <div class="transaction-item">
                    <div class="transaction-info">
                        <div class="transaction-description">${transaction.description}</div>
                        <div class="transaction-meta">
                            <span class="transaction-date">${date}</span>
                            <span class="transaction-category">${transaction.category || 'Uncategorized'}</span>
                        </div>
                    </div>
                    <div class="transaction-amount ${amountClass}">${amountText}</div>
                </div>
            `;
        }).join('');

        container.innerHTML = transactionItems;
    }

    showLoading() {
        // Show loading state for summary cards
        const loadingElements = [
            'totalBalance', 'creditAvailable', 'investmentValue', 'netIncome'
        ];

        loadingElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = '...';
            }
        });

        // Show loading for recent transactions
        const recentTransactions = document.getElementById('recentTransactions');
        if (recentTransactions) {
            recentTransactions.innerHTML = '<div class="loading">Loading recent transactions...</div>';
        }
    }

    showError(message) {
        UIComponents.createNotification(message, 'error');
    }

    // Mock data methods (for development/fallback)
    getMockLabels() {
        const labels = [];
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        return labels;
    }

    getMockBalanceData() {
        return [5000, 5200, 4800, 5100, 5300, 5150, 5400];
    }

    getMockCategoryLabels() {
        return ['Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping'];
    }

    getMockCategoryData() {
        return [300, 150, 200, 250, 180];
    }

    getMockInvestmentLabels() {
        return ['Stocks', 'Crypto', 'Bonds', 'ETFs'];
    }

    getMockInvestmentData() {
        return [2500, 800, 1200, 1500];
    }

    getMockIncomeData() {
        return [1000, 1200, 800, 1100, 1300, 900, 1150];
    }

    getMockExpenseData() {
        return [-800, -900, -750, -850, -950, -700, -880];
    }

    // Cleanup method
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Handle page visibility change to refresh data
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.dashboard) {
        window.dashboard.loadDashboard();
    }
});