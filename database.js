class FinanceDatabase {
    constructor() {
        this.storageKeys = {
            transactions: 'finance_transactions',
            config: 'finance_config'
        };
        this.initializeStorage();
    }

    initializeStorage() {
        if (!localStorage.getItem(this.storageKeys.transactions)) {
            localStorage.setItem(this.storageKeys.transactions, JSON.stringify([]));
        }
        
        if (!localStorage.getItem(this.storageKeys.config)) {
            const defaultConfig = {
                cards: [
                    { name: 'Cash', type: 'cash' }
                ],
                stockSymbols: [],
                cryptoCoins: []
            };
            localStorage.setItem(this.storageKeys.config, JSON.stringify(defaultConfig));
        } else {
            // Migrate old card format to new format
            this.migrateCardFormat();
        }
    }

    migrateCardFormat() {
        try {
            const config = JSON.parse(localStorage.getItem(this.storageKeys.config));

            // Check if cards are in old format (array of strings)
            if (config.cards && config.cards.length > 0 && typeof config.cards[0] === 'string') {
                config.cards = config.cards.map(cardName => ({
                    name: cardName,
                    type: cardName.toLowerCase() === 'cash' ? 'cash' : 'credit' // Default to credit for unknown cards
                }));

                localStorage.setItem(this.storageKeys.config, JSON.stringify(config));
            }
        } catch (error) {
            console.error('Error migrating card format:', error);
        }
    }

    generateId() {
        return Date.now().toString() + Math.random().toString(36).substr(2, 9);
    }

    validateTransaction(transaction) {
        const requiredFields = ['date', 'type'];
        
        for (const field of requiredFields) {
            if (!transaction[field]) {
                throw new Error(`Missing required field: ${field}`);
            }
        }

        if (!['cash', 'card', 'stock', 'crypto', 'initial_balance'].includes(transaction.type)) {
            throw new Error('Invalid transaction type');
        }

        if (transaction.type === 'cash' || transaction.type === 'card') {
            if (!transaction.medium || !transaction.description || transaction.amount === undefined) {
                throw new Error('Missing required fields for cash/card transaction');
            }
        }

        if (transaction.type === 'initial_balance') {
            if (!transaction.medium || transaction.amount === undefined) {
                throw new Error('Missing required fields for initial balance transaction');
            }
        }

        if (transaction.type === 'stock') {
            if (!transaction.symbol || !transaction.quantity || !transaction.price || !transaction.tradeType) {
                throw new Error('Missing required fields for stock transaction');
            }
        }

        if (transaction.type === 'crypto') {
            if (!transaction.coin || !transaction.quantity || !transaction.price || !transaction.tradeType) {
                throw new Error('Missing required fields for crypto transaction');
            }
        }

        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(transaction.date)) {
            throw new Error('Invalid date format. Use YYYY-MM-DD');
        }

        return true;
    }

    saveTransaction(transactionData) {
        try {
            this.validateTransaction(transactionData);
            
            const transaction = {
                ...transactionData,
                id: this.generateId(),
                createdAt: new Date().toISOString()
            };

            if (transaction.type === 'stock' || transaction.type === 'crypto') {
                const quantity = parseFloat(transaction.quantity);
                const price = parseFloat(transaction.price);
                const fees = parseFloat(transaction.fees) || 0;
                
                transaction.totalValue = (quantity * price) + fees;
                
                if (transaction.tradeType === 'sell') {
                    transaction.totalValue = -transaction.totalValue;
                }
            }

            const transactions = this.getTransactions();
            transactions.push(transaction);
            transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
            
            localStorage.setItem(this.storageKeys.transactions, JSON.stringify(transactions));
            return transaction;
        } catch (error) {
            console.error('Error saving transaction:', error);
            throw error;
        }
    }

    getTransactions(filters = {}) {
        try {
            const transactions = JSON.parse(localStorage.getItem(this.storageKeys.transactions)) || [];
            
            return transactions.filter(transaction => {
                if (filters.dateFrom && transaction.date < filters.dateFrom) {
                    return false;
                }
                
                if (filters.dateTo && transaction.date > filters.dateTo) {
                    return false;
                }
                
                if (filters.type && filters.type !== 'all' && transaction.type !== filters.type) {
                    return false;
                }
                
                if (filters.search) {
                    const searchLower = filters.search.toLowerCase();
                    const searchableFields = [
                        transaction.description,
                        transaction.symbol,
                        transaction.coin,
                        transaction.medium
                    ].filter(field => field);
                    
                    const matchesSearch = searchableFields.some(field => 
                        field.toLowerCase().includes(searchLower)
                    );
                    
                    if (!matchesSearch) {
                        return false;
                    }
                }
                
                return true;
            });
        } catch (error) {
            console.error('Error retrieving transactions:', error);
            return [];
        }
    }

    updateTransaction(id, updates) {
        try {
            const transactions = this.getTransactions();
            const index = transactions.findIndex(t => t.id === id);
            
            if (index === -1) {
                throw new Error('Transaction not found');
            }

            const updatedTransaction = { ...transactions[index], ...updates };
            this.validateTransaction(updatedTransaction);

            if (updatedTransaction.type === 'stock' || updatedTransaction.type === 'crypto') {
                const quantity = parseFloat(updatedTransaction.quantity);
                const price = parseFloat(updatedTransaction.price);
                const fees = parseFloat(updatedTransaction.fees) || 0;
                
                updatedTransaction.totalValue = (quantity * price) + fees;
                
                if (updatedTransaction.tradeType === 'sell') {
                    updatedTransaction.totalValue = -updatedTransaction.totalValue;
                }
            }

            transactions[index] = updatedTransaction;
            transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
            
            localStorage.setItem(this.storageKeys.transactions, JSON.stringify(transactions));
            return updatedTransaction;
        } catch (error) {
            console.error('Error updating transaction:', error);
            throw error;
        }
    }

    deleteTransaction(id) {
        try {
            const transactions = this.getTransactions();
            const filteredTransactions = transactions.filter(t => t.id !== id);
            
            if (filteredTransactions.length === transactions.length) {
                throw new Error('Transaction not found');
            }
            
            localStorage.setItem(this.storageKeys.transactions, JSON.stringify(filteredTransactions));
            return true;
        } catch (error) {
            console.error('Error deleting transaction:', error);
            throw error;
        }
    }

    saveInitialBalance(type, data) {
        try {
            const today = new Date().toISOString().split('T')[0];
            
            if (type === 'cash') {
                const transactionData = {
                    date: today,
                    type: 'initial_balance',
                    medium: data.medium,
                    amount: parseFloat(data.amount),
                    description: `Initial balance for ${data.medium}`,
                    isTransfer: false
                };
                return this.saveTransaction(transactionData);
            }
            
            if (type === 'stock') {
                const quantity = parseFloat(data.quantity);
                const price = parseFloat(data.price);
                const totalValue = quantity * price;
                
                const transactionData = {
                    date: today,
                    type: 'stock',
                    symbol: data.symbol.toUpperCase(),
                    quantity: quantity,
                    price: price,
                    tradeType: 'buy',
                    fees: 0,
                    totalValue: totalValue,
                    description: `Initial holdings for ${data.symbol.toUpperCase()}`
                };
                return this.saveTransaction(transactionData);
            }
            
            if (type === 'crypto') {
                const quantity = parseFloat(data.quantity);
                const price = parseFloat(data.price);
                const totalValue = quantity * price;
                
                const transactionData = {
                    date: today,
                    type: 'crypto',
                    coin: data.coin.toUpperCase(),
                    quantity: quantity,
                    price: price,
                    tradeType: 'buy',
                    fees: 0,
                    totalValue: totalValue,
                    description: `Initial holdings for ${data.coin.toUpperCase()}`
                };
                return this.saveTransaction(transactionData);
            }
            
            throw new Error('Invalid initial balance type');
        } catch (error) {
            console.error('Error saving initial balance:', error);
            throw error;
        }
    }

    getConfig() {
        try {
            return JSON.parse(localStorage.getItem(this.storageKeys.config));
        } catch (error) {
            console.error('Error retrieving config:', error);
            return {
                cards: [{ name: 'Cash', type: 'cash' }],
                stockSymbols: [],
                cryptoCoins: []
            };
        }
    }

    updateConfig(config) {
        try {
            const currentConfig = this.getConfig();
            const updatedConfig = { ...currentConfig, ...config };
            localStorage.setItem(this.storageKeys.config, JSON.stringify(updatedConfig));
            return updatedConfig;
        } catch (error) {
            console.error('Error updating config:', error);
            throw error;
        }
    }

    addCard(cardName, cardType) {
        try {
            if (!cardName || cardName.trim() === '') {
                throw new Error('Card name cannot be empty');
            }

            if (!cardType || !['credit', 'debit', 'cash'].includes(cardType)) {
                throw new Error('Invalid card type');
            }

            const config = this.getConfig();
            const trimmedName = cardName.trim();

            if (config.cards.some(card => card.name === trimmedName)) {
                throw new Error('Card already exists');
            }

            config.cards.push({
                name: trimmedName,
                type: cardType
            });
            return this.updateConfig(config);
        } catch (error) {
            console.error('Error adding card:', error);
            throw error;
        }
    }

    removeCard(cardName) {
        try {
            const config = this.getConfig();
            config.cards = config.cards.filter(card => card.name !== cardName);

            if (config.cards.length === 0) {
                config.cards.push({ name: 'Cash', type: 'cash' });
            }

            return this.updateConfig(config);
        } catch (error) {
            console.error('Error removing card:', error);
            throw error;
        }
    }

    calculateSummary(filters = {}) {
        try {
            const transactions = this.getTransactions(filters);
            
            const summary = {
                cashBalance: 0,
                stocksValue: 0,
                cryptoValue: 0,
                netWorth: 0,
                totalIncome: 0,
                totalExpenses: 0,
                transactionCount: transactions.length
            };

            transactions.forEach(transaction => {
                if (transaction.type === 'cash' || transaction.type === 'card' || transaction.type === 'initial_balance') {
                    const amount = parseFloat(transaction.amount);
                    summary.cashBalance += amount;
                    
                    if (transaction.type !== 'initial_balance') {
                        if (amount > 0) {
                            summary.totalIncome += amount;
                        } else {
                            summary.totalExpenses += Math.abs(amount);
                        }
                    }
                }
                
                if (transaction.type === 'stock') {
                    summary.stocksValue += parseFloat(transaction.totalValue) || 0;
                }
                
                if (transaction.type === 'crypto') {
                    summary.cryptoValue += parseFloat(transaction.totalValue) || 0;
                }
            });

            summary.netWorth = summary.cashBalance + summary.stocksValue + summary.cryptoValue;
            
            return summary;
        } catch (error) {
            console.error('Error calculating summary:', error);
            return {
                cashBalance: 0,
                stocksValue: 0,
                cryptoValue: 0,
                netWorth: 0,
                totalIncome: 0,
                totalExpenses: 0,
                transactionCount: 0
            };
        }
    }

    exportData() {
        try {
            const data = {
                transactions: this.getTransactions(),
                config: this.getConfig(),
                exportDate: new Date().toISOString(),
                version: '1.0'
            };
            
            return JSON.stringify(data, null, 2);
        } catch (error) {
            console.error('Error exporting data:', error);
            throw error;
        }
    }

    importData(jsonString) {
        try {
            const data = JSON.parse(jsonString);
            
            if (!data.transactions || !Array.isArray(data.transactions)) {
                throw new Error('Invalid data format: transactions array not found');
            }

            data.transactions.forEach(transaction => {
                this.validateTransaction(transaction);
            });

            localStorage.setItem(this.storageKeys.transactions, JSON.stringify(data.transactions));
            
            if (data.config) {
                localStorage.setItem(this.storageKeys.config, JSON.stringify(data.config));
            }
            
            return true;
        } catch (error) {
            console.error('Error importing data:', error);
            throw error;
        }
    }

    clearAllData() {
        try {
            localStorage.removeItem(this.storageKeys.transactions);
            localStorage.removeItem(this.storageKeys.config);
            this.initializeStorage();
            return true;
        } catch (error) {
            console.error('Error clearing data:', error);
            throw error;
        }
    }

    getStorageUsage() {
        try {
            const transactions = localStorage.getItem(this.storageKeys.transactions);
            const config = localStorage.getItem(this.storageKeys.config);
            
            const transactionsSize = new Blob([transactions || '']).size;
            const configSize = new Blob([config || '']).size;
            const totalSize = transactionsSize + configSize;
            
            return {
                transactions: transactionsSize,
                config: configSize,
                total: totalSize,
                totalFormatted: this.formatBytes(totalSize)
            };
        } catch (error) {
            console.error('Error calculating storage usage:', error);
            return { transactions: 0, config: 0, total: 0, totalFormatted: '0 B' };
        }
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    formatDate(dateString) {
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            return dateString;
        }
    }
}

const db = new FinanceDatabase();