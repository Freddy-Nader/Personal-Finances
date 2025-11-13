// API Wrapper for Personal Finance Management Application
class FinanceAPI {
    constructor(baseURL = 'http://localhost:8000/api') {
        this.baseURL = baseURL;
    }

    // Generic HTTP request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);

            // Handle different response status codes
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            // Handle 204 No Content responses
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // GET request
    async get(endpoint, params = {}) {
        const queryString = Object.keys(params).length
            ? '?' + new URLSearchParams(params).toString()
            : '';
        return this.request(`${endpoint}${queryString}`, { method: 'GET' });
    }

    // POST request
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Card Management Methods
    async getCards() {
        return this.get('/cards');
    }

    async getCard(cardId) {
        return this.get(`/cards/${cardId}`);
    }

    async createCard(cardData) {
        return this.post('/cards', cardData);
    }

    async updateCard(cardId, cardData) {
        return this.put(`/cards/${cardId}`, cardData);
    }

    async deleteCard(cardId) {
        return this.delete(`/cards/${cardId}`);
    }

    // Section Management Methods
    async getCardSections(cardId) {
        return this.get(`/cards/${cardId}/sections`);
    }

    async createSection(cardId, sectionData) {
        return this.post(`/cards/${cardId}/sections`, sectionData);
    }

    // Transaction Management Methods
    async getTransactions(filters = {}) {
        return this.get('/transactions', filters);
    }

    async getTransaction(transactionId) {
        return this.get(`/transactions/${transactionId}`);
    }

    async createTransaction(transactionData) {
        return this.post('/transactions', transactionData);
    }

    async updateTransaction(transactionId, transactionData) {
        return this.put(`/transactions/${transactionId}`, transactionData);
    }

    async deleteTransaction(transactionId) {
        return this.delete(`/transactions/${transactionId}`);
    }

    // Investment Management Methods
    async getInvestmentPositions() {
        return this.get('/investments/positions');
    }

    async createInvestmentPosition(positionData) {
        return this.post('/investments/positions', positionData);
    }

    async getInvestmentMovements(filters = {}) {
        return this.get('/investments/movements', filters);
    }

    async createInvestmentMovement(movementData) {
        return this.post('/investments/movements', movementData);
    }

    // Dashboard Methods
    async getDashboardSummary(period = 'month') {
        return this.get('/dashboard/summary', { period });
    }

    async getDashboardCharts(chartType, period = 'month') {
        const params = { period };
        if (chartType) {
            params.chartType = chartType;
        }
        return this.get('/dashboard/charts', params);
    }

    // Utility Methods
    async healthCheck() {
        try {
            // Simple health check - try to get cards
            await this.getCards();
            return { status: 'healthy', timestamp: new Date().toISOString() };
        } catch (error) {
            return {
                status: 'unhealthy',
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    // Error Handling Helper
    handleError(error, context = '') {
        const errorMessage = error.message || 'Unknown error occurred';

        console.error(`API Error${context ? ` (${context})` : ''}:`, error);

        // You can customize error handling here
        // For example, show toast notifications, redirect on auth errors, etc.
        if (errorMessage.includes('fetch')) {
            throw new Error('Unable to connect to server. Please check your connection.');
        }

        if (errorMessage.includes('404')) {
            throw new Error('Requested resource not found.');
        }

        if (errorMessage.includes('500')) {
            throw new Error('Server error. Please try again later.');
        }

        throw error;
    }

    // Batch Operations (if needed)
    async batchRequest(requests) {
        try {
            const promises = requests.map(req =>
                this.request(req.endpoint, req.options)
            );
            return await Promise.allSettled(promises);
        } catch (error) {
            console.error('Batch request failed:', error);
            throw error;
        }
    }
}

// Create and export API instance
const api = new FinanceAPI();

// Export for both ES6 modules and CommonJS
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FinanceAPI, api };
} else if (typeof window !== 'undefined') {
    window.FinanceAPI = FinanceAPI;
    window.api = api;
}

// Export the class and instance for ES6 modules (if supported)
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    // CommonJS export
    module.exports = { FinanceAPI, api };
}