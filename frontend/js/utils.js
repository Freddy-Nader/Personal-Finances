// Utility Functions for Personal Finance Application

class FinanceUtils {
    // Date and Time Utilities
    static formatDate(date, format = 'short') {
        const d = new Date(date);
        const options = {
            short: { month: 'short', day: 'numeric', year: 'numeric' },
            long: { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' },
            time: { hour: '2-digit', minute: '2-digit', hour12: true },
            datetime: {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            }
        };

        return d.toLocaleDateString('en-US', options[format] || options.short);
    }

    static formatDateForInput(date) {
        const d = new Date(date);
        return d.toISOString().slice(0, 16); // Format for datetime-local input
    }

    static getDateRange(period) {
        const now = new Date();
        const startDate = new Date();

        switch (period) {
            case 'week':
                startDate.setDate(now.getDate() - 7);
                break;
            case 'month':
                startDate.setMonth(now.getMonth() - 1);
                break;
            case 'quarter':
                startDate.setMonth(now.getMonth() - 3);
                break;
            case 'year':
                startDate.setFullYear(now.getFullYear() - 1);
                break;
            default:
                startDate.setMonth(now.getMonth() - 1);
        }

        return {
            startDate: startDate.toISOString().split('T')[0],
            endDate: now.toISOString().split('T')[0]
        };
    }

    // Currency and Number Utilities
    static formatCurrency(amount, currency = 'USD', showSign = false) {
        const formatter = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        const formatted = formatter.format(Math.abs(amount));

        if (showSign) {
            return amount >= 0 ? `+${formatted}` : `-${formatted}`;
        }

        return formatted;
    }

    static formatNumber(number, decimals = 2) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    }

    static parseNumber(value) {
        if (typeof value === 'number') return value;
        if (typeof value === 'string') {
            // Remove currency symbols and commas
            const cleaned = value.replace(/[$,\s]/g, '');
            return parseFloat(cleaned) || 0;
        }
        return 0;
    }

    // Percentage Utilities
    static formatPercentage(value, decimals = 2) {
        return `${(value * 100).toFixed(decimals)}%`;
    }

    static calculatePercentageChange(oldValue, newValue) {
        if (oldValue === 0) return newValue > 0 ? 1 : 0;
        return (newValue - oldValue) / Math.abs(oldValue);
    }

    // Financial Calculations
    static calculateCompoundInterest(principal, rate, frequency, time) {
        // Formula: A = P(1 + r/n)^(nt)
        // Where: P = principal, r = annual rate, n = compound frequency, t = time in years
        const r = rate / 100; // Convert percentage to decimal
        return principal * Math.pow(1 + r / frequency, frequency * time);
    }

    static getCompoundFrequency(frequencyString) {
        const frequencies = {
            'daily_365': 365,
            'daily_360': 360,
            'semi_weekly_104': 104,
            'weekly_52': 52,
            'bi_weekly_26': 26,
            'semi_monthly_24': 24,
            'monthly_12': 12,
            'bi_monthly_6': 6,
            'quarterly_4': 4,
            'half_yearly_2': 2,
            'yearly_1': 1
        };
        return frequencies[frequencyString] || 12; // Default to monthly
    }

    static calculatePortfolioValue(positions) {
        return positions.reduce((total, position) => {
            return total + (position.current_value || 0);
        }, 0);
    }

    static calculateProfitLoss(positions) {
        return positions.reduce((total, position) => {
            return total + (position.profit_loss || 0);
        }, 0);
    }

    // Array and Data Utilities
    static groupBy(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key];
            groups[group] = groups[group] || [];
            groups[group].push(item);
            return groups;
        }, {});
    }

    static sortBy(array, key, direction = 'asc') {
        return [...array].sort((a, b) => {
            const aValue = a[key];
            const bValue = b[key];

            if (direction === 'desc') {
                return bValue > aValue ? 1 : bValue < aValue ? -1 : 0;
            }
            return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
        });
    }

    static filterBy(array, filters) {
        return array.filter(item => {
            return Object.entries(filters).every(([key, value]) => {
                if (value === '' || value === null || value === undefined) return true;

                if (typeof value === 'string') {
                    return String(item[key]).toLowerCase().includes(value.toLowerCase());
                }

                return item[key] === value;
            });
        });
    }

    // Validation Utilities
    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    static validateCardNumber(cardNumber) {
        // Simple validation - remove spaces and check if it's numeric
        const cleaned = cardNumber.replace(/\s/g, '');
        return /^\d{13,19}$/.test(cleaned);
    }

    static validateRequired(value) {
        return value !== null && value !== undefined && String(value).trim() !== '';
    }

    static validatePositiveNumber(value) {
        const num = this.parseNumber(value);
        return num > 0;
    }

    // URL and Query Utilities
    static getQueryParams() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        for (const [key, value] of params) {
            result[key] = value;
        }
        return result;
    }

    static setQueryParams(params) {
        const url = new URL(window.location);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                url.searchParams.set(key, value);
            } else {
                url.searchParams.delete(key);
            }
        });
        window.history.replaceState({}, '', url);
    }

    // Local Storage Utilities
    static saveToStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
            return false;
        }
    }

    static loadFromStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Failed to load from localStorage:', error);
            return defaultValue;
        }
    }

    static removeFromStorage(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Failed to remove from localStorage:', error);
            return false;
        }
    }

    // DOM Utilities
    static createElement(tag, className = '', textContent = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (textContent) element.textContent = textContent;
        return element;
    }

    static addEventListeners(element, events) {
        Object.entries(events).forEach(([event, handler]) => {
            element.addEventListener(event, handler);
        });
    }

    static debounce(func, wait) {
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

    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Chart Data Utilities
    static prepareChartData(data, labelKey, valueKey) {
        return {
            labels: data.map(item => item[labelKey]),
            datasets: [{
                data: data.map(item => item[valueKey]),
                backgroundColor: this.generateColors(data.length),
                borderWidth: 1
            }]
        };
    }

    static generateColors(count) {
        const colors = [
            '#2383e2', '#0f7b0f', '#e03e3e', '#ffc400', '#9b59b6',
            '#e67e22', '#1abc9c', '#34495e', '#f39c12', '#27ae60'
        ];

        const result = [];
        for (let i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }
        return result;
    }

    // Error Handling Utilities
    static handleError(error, context = '', showToUser = true) {
        console.error(`Error in ${context}:`, error);

        if (showToUser) {
            const message = error.message || 'An unexpected error occurred';
            this.showNotification(message, 'error');
        }

        // You can add error tracking here (e.g., send to analytics)
        return {
            handled: true,
            message: error.message,
            context
        };
    }

    static showNotification(message, type = 'info', duration = 3000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;

        // Add to document
        document.body.appendChild(notification);

        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    }

    // Performance Utilities
    static measurePerformance(name, func) {
        const start = performance.now();
        const result = func();
        const end = performance.now();
        console.log(`${name} took ${end - start} milliseconds`);
        return result;
    }

    static async measureAsyncPerformance(name, asyncFunc) {
        const start = performance.now();
        const result = await asyncFunc();
        const end = performance.now();
        console.log(`${name} took ${end - start} milliseconds`);
        return result;
    }
}

// Make FinanceUtils available globally
if (typeof window !== 'undefined') {
    window.FinanceUtils = FinanceUtils;
}

// Export for CommonJS modules (if supported)
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = { FinanceUtils };
}