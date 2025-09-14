class FinanceApp {
    constructor() {
        this.currentFilters = {};
        this.editingTransaction = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCardOptions();
        this.refreshDashboard();
        this.refreshTransactionList();
        this.setDefaultDates();
        this.handleMovementTypeChange('cash');
    }

    bindEvents() {
        document.getElementById('add-transaction-btn').addEventListener('click', () => {
            this.showModal('add-transaction-modal');
        });

        document.getElementById('manage-btn').addEventListener('click', () => {
            this.showModal('management-modal');
            this.refreshManagementModal();
        });

        document.getElementById('export-btn').addEventListener('click', () => {
            this.exportData();
        });

        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal').id);
            });
        });

        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });

        document.querySelectorAll('.tab-btn').forEach(tabBtn => {
            tabBtn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        document.getElementById('cash-card-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCashCardSubmit();
        });

        document.getElementById('stock-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleStockSubmit();
        });

        document.getElementById('crypto-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCryptoSubmit();
        });

        document.getElementById('initial-cash-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleInitialCashSubmit();
        });

        document.getElementById('initial-stock-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleInitialStockSubmit();
        });

        document.getElementById('initial-crypto-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleInitialCryptoSubmit();
        });

        document.getElementById('apply-filters-btn').addEventListener('click', () => {
            this.applyFilters();
        });

        document.getElementById('reset-filters-btn').addEventListener('click', () => {
            this.resetFilters();
        });

        document.getElementById('add-card-btn').addEventListener('click', () => {
            this.addCard();
        });

        document.getElementById('import-btn').addEventListener('click', () => {
            document.getElementById('import-file').click();
        });

        document.getElementById('import-file').addEventListener('change', (e) => {
            this.importData(e.target.files[0]);
        });

        document.getElementById('clear-data-btn').addEventListener('click', () => {
            this.clearAllData();
        });

        ['stock-quantity', 'stock-price', 'stock-fees'].forEach(id => {
            document.getElementById(id).addEventListener('input', () => {
                this.calculateStockTotal();
            });
        });

        ['crypto-quantity', 'crypto-price', 'crypto-fees'].forEach(id => {
            document.getElementById(id).addEventListener('input', () => {
                this.calculateCryptoTotal();
            });
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

        document.querySelectorAll('input[name="movement-type"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.handleMovementTypeChange(e.target.value);
            });
        });
    }

    setDefaultDates() {
        const today = new Date().toISOString().split('T')[0];
        const oneMonthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        
        document.getElementById('date-from').value = oneMonthAgo;
        document.getElementById('date-to').value = today;
        
        document.getElementById('cash-date').value = today;
        document.getElementById('stock-date').value = today;
        document.getElementById('crypto-date').value = today;
    }

    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
        document.body.style.overflow = '';
        
        if (modalId === 'add-transaction-modal') {
            this.resetForms();
        }
        
        if (modalId === 'edit-transaction-modal') {
            this.editingTransaction = null;
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
        this.resetForms();
        this.editingTransaction = null;
    }

    switchTab(tabName) {
        const clickedTab = document.querySelector(`[data-tab="${tabName}"]`);
        const tabContainer = clickedTab.closest('.tabs');
        
        tabContainer.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const formContainer = tabContainer.nextElementSibling || tabContainer.parentNode;
        formContainer.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        clickedTab.classList.add('active');
        document.getElementById(`${tabName}-form`).classList.add('active');
    }

    resetForms() {
        document.querySelectorAll('form').forEach(form => {
            form.reset();
        });

        this.setDefaultDates();
        this.calculateStockTotal();
        this.calculateCryptoTotal();
        this.handleMovementTypeChange('cash');
    }

    loadCardOptions() {
        const config = db.getConfig();
        const cashMediumSelect = document.getElementById('cash-medium');
        const initialCashMediumSelect = document.getElementById('initial-cash-medium');

        [cashMediumSelect, initialCashMediumSelect].forEach(select => {
            if (select) {
                select.innerHTML = '';
                config.cards.forEach(card => {
                    const option = document.createElement('option');
                    option.value = card.type === 'cash' ? 'cash' : 'card';
                    option.textContent = card.name;
                    option.dataset.cardName = card.name;
                    option.dataset.cardType = card.type;
                    select.appendChild(option);
                });
            }
        });
    }

    handleMovementTypeChange(movementType) {
        const cardSelectionGroup = document.getElementById('card-selection-group');
        const cashMediumSelect = document.getElementById('cash-medium');

        if (movementType === 'cash') {
            cardSelectionGroup.style.display = 'none';
            cashMediumSelect.removeAttribute('required');
        } else {
            cardSelectionGroup.style.display = 'block';
            cashMediumSelect.setAttribute('required', 'required');
            this.loadCardOptionsForType(movementType);
        }
    }

    loadCardOptionsForType(cardType) {
        const config = db.getConfig();
        const cashMediumSelect = document.getElementById('cash-medium');

        cashMediumSelect.innerHTML = '';

        const filteredCards = config.cards.filter(card => {
            return card.type === cardType;
        });

        if (filteredCards.length === 0) {
            const option = document.createElement('option');
            option.value = 'card';
            option.textContent = `No ${cardType} cards available - Add one in Manage`;
            option.dataset.cardName = `${cardType} card`;
            option.disabled = true;
            cashMediumSelect.appendChild(option);
        } else {
            filteredCards.forEach(card => {
                const option = document.createElement('option');
                option.value = 'card';
                option.textContent = card.name;
                option.dataset.cardName = card.name;
                option.dataset.cardType = card.type;
                cashMediumSelect.appendChild(option);
            });
        }
    }

    handleCashCardSubmit() {
        try {
            const form = document.getElementById('cash-card-form');
            const formData = new FormData(form);
            const movementType = document.querySelector('input[name="movement-type"]:checked').value;

            let medium, type;

            if (movementType === 'cash') {
                medium = 'Cash';
                type = 'cash';
            } else {
                const selectedOption = document.getElementById('cash-medium').selectedOptions[0];
                medium = selectedOption.dataset.cardName;
                type = 'card';
            }

            const transactionData = {
                date: document.getElementById('cash-date').value,
                type: type,
                medium: medium,
                amount: parseFloat(document.getElementById('cash-amount').value),
                description: document.getElementById('cash-description').value,
                isTransfer: document.getElementById('cash-transfer').checked
            };

            if (this.editingTransaction) {
                db.updateTransaction(this.editingTransaction.id, transactionData);
                this.showToast('Transaction updated successfully', 'success');
                this.closeModal('edit-transaction-modal');
            } else {
                db.saveTransaction(transactionData);
                this.showToast('Transaction added successfully', 'success');
                this.closeModal('add-transaction-modal');
            }

            this.refreshDashboard();
            this.refreshTransactionList();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    handleStockSubmit() {
        try {
            const transactionData = {
                date: document.getElementById('stock-date').value,
                type: 'stock',
                symbol: document.getElementById('stock-symbol').value.toUpperCase(),
                quantity: parseFloat(document.getElementById('stock-quantity').value),
                price: parseFloat(document.getElementById('stock-price').value),
                tradeType: document.getElementById('stock-type').value,
                fees: parseFloat(document.getElementById('stock-fees').value) || 0
            };

            if (this.editingTransaction) {
                db.updateTransaction(this.editingTransaction.id, transactionData);
                this.showToast('Transaction updated successfully', 'success');
                this.closeModal('edit-transaction-modal');
            } else {
                db.saveTransaction(transactionData);
                this.showToast('Transaction added successfully', 'success');
                this.closeModal('add-transaction-modal');
            }
            
            this.refreshDashboard();
            this.refreshTransactionList();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    handleCryptoSubmit() {
        try {
            const transactionData = {
                date: document.getElementById('crypto-date').value,
                type: 'crypto',
                coin: document.getElementById('crypto-coin').value.toUpperCase(),
                quantity: parseFloat(document.getElementById('crypto-quantity').value),
                price: parseFloat(document.getElementById('crypto-price').value),
                tradeType: document.getElementById('crypto-type').value,
                fees: parseFloat(document.getElementById('crypto-fees').value) || 0
            };

            if (this.editingTransaction) {
                db.updateTransaction(this.editingTransaction.id, transactionData);
                this.showToast('Transaction updated successfully', 'success');
                this.closeModal('edit-transaction-modal');
            } else {
                db.saveTransaction(transactionData);
                this.showToast('Transaction added successfully', 'success');
                this.closeModal('add-transaction-modal');
            }
            
            this.refreshDashboard();
            this.refreshTransactionList();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    calculateStockTotal() {
        const quantity = parseFloat(document.getElementById('stock-quantity').value) || 0;
        const price = parseFloat(document.getElementById('stock-price').value) || 0;
        const fees = parseFloat(document.getElementById('stock-fees').value) || 0;
        
        const total = (quantity * price) + fees;
        document.getElementById('stock-total').value = total.toFixed(2);
    }

    calculateCryptoTotal() {
        const quantity = parseFloat(document.getElementById('crypto-quantity').value) || 0;
        const price = parseFloat(document.getElementById('crypto-price').value) || 0;
        const fees = parseFloat(document.getElementById('crypto-fees').value) || 0;
        
        const total = (quantity * price) + fees;
        document.getElementById('crypto-total').value = total.toFixed(2);
    }

    handleInitialCashSubmit() {
        try {
            const selectedOption = document.getElementById('initial-cash-medium').selectedOptions[0];
            const amount = parseFloat(document.getElementById('initial-cash-amount').value);
            
            if (amount <= 0) {
                this.showToast('Initial balance must be greater than 0', 'warning');
                return;
            }
            
            const data = {
                medium: selectedOption.dataset.cardName,
                amount: amount
            };

            db.saveInitialBalance('cash', data);
            this.showToast(`Initial balance set for ${data.medium}: ${db.formatCurrency(amount)}`, 'success');
            
            document.getElementById('initial-cash-form').reset();
            this.refreshDashboard();
            this.refreshTransactionList();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    handleInitialStockSubmit() {
        try {
            const symbol = document.getElementById('initial-stock-symbol').value.trim().toUpperCase();
            const quantity = parseFloat(document.getElementById('initial-stock-quantity').value);
            const price = parseFloat(document.getElementById('initial-stock-price').value);
            
            if (!symbol || quantity <= 0 || price <= 0) {
                this.showToast('Please enter valid stock information', 'warning');
                return;
            }
            
            const data = {
                symbol: symbol,
                quantity: quantity,
                price: price
            };

            db.saveInitialBalance('stock', data);
            this.showToast(`Initial stock holdings set: ${quantity} shares of ${symbol} at ${db.formatCurrency(price)}`, 'success');
            
            document.getElementById('initial-stock-form').reset();
            this.refreshDashboard();
            this.refreshTransactionList();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    handleInitialCryptoSubmit() {
        try {
            const coin = document.getElementById('initial-crypto-coin').value.trim().toUpperCase();
            const quantity = parseFloat(document.getElementById('initial-crypto-quantity').value);
            const price = parseFloat(document.getElementById('initial-crypto-price').value);
            
            if (!coin || quantity <= 0 || price <= 0) {
                this.showToast('Please enter valid crypto information', 'warning');
                return;
            }
            
            const data = {
                coin: coin,
                quantity: quantity,
                price: price
            };

            db.saveInitialBalance('crypto', data);
            this.showToast(`Initial crypto holdings set: ${quantity} ${coin} at ${db.formatCurrency(price)}`, 'success');
            
            document.getElementById('initial-crypto-form').reset();
            this.refreshDashboard();
            this.refreshTransactionList();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    applyFilters() {
        this.currentFilters = {
            dateFrom: document.getElementById('date-from').value,
            dateTo: document.getElementById('date-to').value,
            type: document.getElementById('type-filter').value,
            search: document.getElementById('search-filter').value
        };
        
        this.refreshDashboard();
        this.refreshTransactionList();
        this.showToast('Filters applied', 'success');
    }

    resetFilters() {
        this.currentFilters = {};
        
        document.getElementById('date-from').value = '';
        document.getElementById('date-to').value = '';
        document.getElementById('type-filter').value = 'all';
        document.getElementById('search-filter').value = '';
        
        this.setDefaultDates();
        this.refreshDashboard();
        this.refreshTransactionList();
        this.showToast('Filters reset', 'success');
    }

    refreshDashboard() {
        const summary = db.calculateSummary(this.currentFilters);
        
        document.getElementById('cash-balance').textContent = db.formatCurrency(summary.cashBalance);
        document.getElementById('stocks-value').textContent = db.formatCurrency(summary.stocksValue);
        document.getElementById('crypto-value').textContent = db.formatCurrency(summary.cryptoValue);
        document.getElementById('net-worth').textContent = db.formatCurrency(summary.netWorth);
    }

    refreshTransactionList() {
        const transactions = db.getTransactions(this.currentFilters);
        const tbody = document.getElementById('transactions-tbody');
        
        tbody.innerHTML = '';
        
        if (transactions.length === 0) {
            tbody.innerHTML = '<tr class="empty-state"><td colspan="5">No transactions found.</td></tr>';
            return;
        }

        transactions.forEach(transaction => {
            const row = this.createTransactionRow(transaction);
            tbody.appendChild(row);
        });
    }

    createTransactionRow(transaction) {
        const row = document.createElement('tr');
        
        const dateCell = document.createElement('td');
        dateCell.textContent = db.formatDate(transaction.date);
        
        const typeCell = document.createElement('td');
        typeCell.textContent = this.getTransactionTypeDisplay(transaction);
        
        const descriptionCell = document.createElement('td');
        descriptionCell.textContent = this.getTransactionDescription(transaction);
        
        const amountCell = document.createElement('td');
        const amount = this.getTransactionAmount(transaction);
        amountCell.textContent = db.formatCurrency(Math.abs(amount));
        amountCell.className = amount >= 0 ? 'amount-positive' : 'amount-negative';
        
        const actionsCell = document.createElement('td');
        actionsCell.innerHTML = `
            <div class="transaction-actions">
                <button class="btn btn-secondary btn-small" onclick="app.editTransaction('${transaction.id}')">Edit</button>
                <button class="btn btn-danger btn-small" onclick="app.deleteTransaction('${transaction.id}')">Delete</button>
            </div>
        `;
        
        row.appendChild(dateCell);
        row.appendChild(typeCell);
        row.appendChild(descriptionCell);
        row.appendChild(amountCell);
        row.appendChild(actionsCell);
        
        return row;
    }

    getTransactionTypeDisplay(transaction) {
        if (transaction.type === 'cash' || transaction.type === 'card') {
            return transaction.medium;
        }
        if (transaction.type === 'stock') {
            return `Stock (${transaction.symbol})`;
        }
        if (transaction.type === 'crypto') {
            return `Crypto (${transaction.coin})`;
        }
        return transaction.type;
    }

    getTransactionDescription(transaction) {
        if (transaction.type === 'cash' || transaction.type === 'card') {
            return transaction.description + (transaction.isTransfer ? ' (Transfer)' : '');
        }
        if (transaction.type === 'initial_balance') {
            return transaction.description;
        }
        if (transaction.type === 'stock') {
            return `${transaction.tradeType.toUpperCase()} ${transaction.quantity} shares at ${db.formatCurrency(transaction.price)}`;
        }
        if (transaction.type === 'crypto') {
            return `${transaction.tradeType.toUpperCase()} ${transaction.quantity} ${transaction.coin} at ${db.formatCurrency(transaction.price)}`;
        }
        return '';
    }

    getTransactionAmount(transaction) {
        if (transaction.type === 'cash' || transaction.type === 'card' || transaction.type === 'initial_balance') {
            return transaction.amount;
        }
        return transaction.totalValue;
    }

    editTransaction(id) {
        const transaction = db.getTransactions().find(t => t.id === id);
        if (!transaction) {
            this.showToast('Transaction not found', 'error');
            return;
        }

        this.editingTransaction = transaction;
        
        if (transaction.type === 'cash' || transaction.type === 'card') {
            this.populateCashCardForm(transaction);
            this.switchTab('cash-card');
        } else if (transaction.type === 'stock') {
            this.populateStockForm(transaction);
            this.switchTab('stock');
        } else if (transaction.type === 'crypto') {
            this.populateCryptoForm(transaction);
            this.switchTab('crypto');
        }

        this.showModal('edit-transaction-modal');
        this.createEditForm(transaction);
    }

    createEditForm(transaction) {
        const container = document.getElementById('edit-form-container');
        
        if (transaction.type === 'cash' || transaction.type === 'card') {
            const isCard = transaction.type === 'card';
            let movementType = 'cash';

            if (isCard) {
                // Try to determine card type from stored cards
                const config = db.getConfig();
                const cardInfo = config.cards.find(card => card.name === transaction.medium);
                movementType = cardInfo ? cardInfo.type : 'credit'; // Default to credit if not found
            }

            container.innerHTML = `
                <form id="edit-cash-card-form">
                    <div class="form-group">
                        <label for="edit-cash-date">Date:</label>
                        <input type="date" id="edit-cash-date" value="${transaction.date}" required>
                    </div>
                    <div class="form-group">
                        <label>Movement Type:</label>
                        <div class="checkbox-filters">
                            <label class="filter-checkbox">
                                <input type="radio" name="edit-movement-type" value="cash" id="edit-movement-cash" ${movementType === 'cash' ? 'checked' : ''}>
                                <span class="checkmark">Cash</span>
                            </label>
                            <label class="filter-checkbox">
                                <input type="radio" name="edit-movement-type" value="credit" id="edit-movement-credit" ${movementType === 'credit' ? 'checked' : ''}>
                                <span class="checkmark">Credit Card</span>
                            </label>
                            <label class="filter-checkbox">
                                <input type="radio" name="edit-movement-type" value="debit" id="edit-movement-debit" ${movementType === 'debit' ? 'checked' : ''}>
                                <span class="checkmark">Debit Card</span>
                            </label>
                        </div>
                    </div>
                    <div class="form-group" id="edit-card-selection-group" style="display: ${isCard ? 'block' : 'none'};">
                        <label for="edit-cash-medium">Select Card:</label>
                        <select id="edit-cash-medium" ${isCard ? 'required' : ''}>
                            <option value="card">Select a card</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="edit-cash-amount">Amount:</label>
                        <input type="number" id="edit-cash-amount" step="0.01" value="${transaction.amount}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-cash-description">Description:</label>
                        <input type="text" id="edit-cash-description" value="${transaction.description}" required>
                    </div>
                    <div class="form-group checkbox-group">
                        <label>
                            <input type="checkbox" id="edit-cash-transfer" ${transaction.isTransfer ? 'checked' : ''}>
                            Inter-bank transfer
                        </label>
                    </div>
                    <button type="submit" class="btn btn-primary">Update Transaction</button>
                </form>
            `;
            
            this.loadEditCardOptions(transaction.medium, movementType);

            document.querySelectorAll('input[name="edit-movement-type"]').forEach(radio => {
                radio.addEventListener('change', (e) => {
                    this.handleEditMovementTypeChange(e.target.value);
                });
            });

            document.getElementById('edit-cash-card-form').addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleEditCashCardSubmit();
            });
        }
        
        else if (transaction.type === 'stock') {
            container.innerHTML = `
                <form id="edit-stock-form">
                    <div class="form-group">
                        <label for="edit-stock-date">Date:</label>
                        <input type="date" id="edit-stock-date" value="${transaction.date}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-stock-symbol">Symbol:</label>
                        <input type="text" id="edit-stock-symbol" value="${transaction.symbol}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-stock-quantity">Quantity:</label>
                        <input type="number" id="edit-stock-quantity" step="0.001" value="${transaction.quantity}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-stock-price">Price per Share:</label>
                        <input type="number" id="edit-stock-price" step="0.01" value="${transaction.price}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-stock-type">Type:</label>
                        <select id="edit-stock-type" required>
                            <option value="buy" ${transaction.tradeType === 'buy' ? 'selected' : ''}>Buy</option>
                            <option value="sell" ${transaction.tradeType === 'sell' ? 'selected' : ''}>Sell</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="edit-stock-fees">Fees:</label>
                        <input type="number" id="edit-stock-fees" step="0.01" value="${transaction.fees || 0}">
                    </div>
                    <button type="submit" class="btn btn-primary">Update Transaction</button>
                </form>
            `;
            
            document.getElementById('edit-stock-form').addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleEditStockSubmit();
            });
        }
        
        else if (transaction.type === 'crypto') {
            container.innerHTML = `
                <form id="edit-crypto-form">
                    <div class="form-group">
                        <label for="edit-crypto-date">Date:</label>
                        <input type="date" id="edit-crypto-date" value="${transaction.date}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-crypto-coin">Coin:</label>
                        <input type="text" id="edit-crypto-coin" value="${transaction.coin}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-crypto-quantity">Quantity:</label>
                        <input type="number" id="edit-crypto-quantity" step="0.00000001" value="${transaction.quantity}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-crypto-price">Price (USD):</label>
                        <input type="number" id="edit-crypto-price" step="0.01" value="${transaction.price}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-crypto-type">Type:</label>
                        <select id="edit-crypto-type" required>
                            <option value="buy" ${transaction.tradeType === 'buy' ? 'selected' : ''}>Buy</option>
                            <option value="sell" ${transaction.tradeType === 'sell' ? 'selected' : ''}>Sell</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="edit-crypto-fees">Fees:</label>
                        <input type="number" id="edit-crypto-fees" step="0.01" value="${transaction.fees || 0}">
                    </div>
                    <button type="submit" class="btn btn-primary">Update Transaction</button>
                </form>
            `;
            
            document.getElementById('edit-crypto-form').addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleEditCryptoSubmit();
            });
        }
    }

    loadEditCardOptions(selectedMedium, movementType) {
        const config = db.getConfig();
        const select = document.getElementById('edit-cash-medium');

        if (movementType === 'cash') {
            return;
        }

        select.innerHTML = '';

        const filteredCards = config.cards.filter(card => {
            return card.type === movementType;
        });

        filteredCards.forEach(card => {
            const option = document.createElement('option');
            option.value = 'card';
            option.textContent = card.name;
            option.dataset.cardName = card.name;
            option.dataset.cardType = card.type;
            option.selected = card.name === selectedMedium;
            select.appendChild(option);
        });
    }

    handleEditMovementTypeChange(movementType) {
        const cardSelectionGroup = document.getElementById('edit-card-selection-group');
        const cashMediumSelect = document.getElementById('edit-cash-medium');

        if (movementType === 'cash') {
            cardSelectionGroup.style.display = 'none';
            cashMediumSelect.removeAttribute('required');
        } else {
            cardSelectionGroup.style.display = 'block';
            cashMediumSelect.setAttribute('required', 'required');
            this.loadEditCardOptionsForType(movementType);
        }
    }

    loadEditCardOptionsForType(cardType) {
        const config = db.getConfig();
        const cashMediumSelect = document.getElementById('edit-cash-medium');

        cashMediumSelect.innerHTML = '';

        const filteredCards = config.cards.filter(card => {
            return card.type === cardType;
        });

        if (filteredCards.length === 0) {
            const option = document.createElement('option');
            option.value = 'card';
            option.textContent = `No ${cardType} cards available - Add one in Manage`;
            option.dataset.cardName = `${cardType} card`;
            option.disabled = true;
            cashMediumSelect.appendChild(option);
        } else {
            filteredCards.forEach(card => {
                const option = document.createElement('option');
                option.value = 'card';
                option.textContent = card.name;
                option.dataset.cardName = card.name;
                option.dataset.cardType = card.type;
                cashMediumSelect.appendChild(option);
            });
        }
    }

    handleEditCashCardSubmit() {
        const movementType = document.querySelector('input[name="edit-movement-type"]:checked').value;

        let medium, type;

        if (movementType === 'cash') {
            medium = 'Cash';
            type = 'cash';
        } else {
            const selectedOption = document.getElementById('edit-cash-medium').selectedOptions[0];
            medium = selectedOption.dataset.cardName;
            type = 'card';
        }

        const transactionData = {
            date: document.getElementById('edit-cash-date').value,
            type: type,
            medium: medium,
            amount: parseFloat(document.getElementById('edit-cash-amount').value),
            description: document.getElementById('edit-cash-description').value,
            isTransfer: document.getElementById('edit-cash-transfer').checked
        };

        this.updateTransaction(transactionData);
    }

    handleEditStockSubmit() {
        const transactionData = {
            date: document.getElementById('edit-stock-date').value,
            type: 'stock',
            symbol: document.getElementById('edit-stock-symbol').value.toUpperCase(),
            quantity: parseFloat(document.getElementById('edit-stock-quantity').value),
            price: parseFloat(document.getElementById('edit-stock-price').value),
            tradeType: document.getElementById('edit-stock-type').value,
            fees: parseFloat(document.getElementById('edit-stock-fees').value) || 0
        };

        this.updateTransaction(transactionData);
    }

    handleEditCryptoSubmit() {
        const transactionData = {
            date: document.getElementById('edit-crypto-date').value,
            type: 'crypto',
            coin: document.getElementById('edit-crypto-coin').value.toUpperCase(),
            quantity: parseFloat(document.getElementById('edit-crypto-quantity').value),
            price: parseFloat(document.getElementById('edit-crypto-price').value),
            tradeType: document.getElementById('edit-crypto-type').value,
            fees: parseFloat(document.getElementById('edit-crypto-fees').value) || 0
        };

        this.updateTransaction(transactionData);
    }

    updateTransaction(transactionData) {
        try {
            db.updateTransaction(this.editingTransaction.id, transactionData);
            this.showToast('Transaction updated successfully', 'success');
            this.closeModal('edit-transaction-modal');
            this.refreshDashboard();
            this.refreshTransactionList();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    deleteTransaction(id) {
        if (confirm('Are you sure you want to delete this transaction?')) {
            try {
                db.deleteTransaction(id);
                this.showToast('Transaction deleted successfully', 'success');
                this.refreshDashboard();
                this.refreshTransactionList();
            } catch (error) {
                this.showToast(error.message, 'error');
            }
        }
    }

    addCard() {
        const cardName = document.getElementById('new-card').value.trim();
        const cardType = document.querySelector('input[name="new-card-type"]:checked').value;

        if (!cardName) {
            this.showToast('Please enter a card name', 'warning');
            return;
        }

        try {
            db.addCard(cardName, cardType);
            document.getElementById('new-card').value = '';
            document.getElementById('new-card-credit').checked = true; // Reset to credit
            this.loadCardOptions();
            this.refreshManagementModal();
            this.showToast(`${cardType.charAt(0).toUpperCase() + cardType.slice(1)} card added successfully`, 'success');
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    removeCard(cardName) {
        if (confirm(`Are you sure you want to remove the card "${cardName}"?`)) {
            try {
                db.removeCard(cardName);
                this.loadCardOptions();
                this.refreshManagementModal();
                this.showToast('Card removed successfully', 'success');
            } catch (error) {
                this.showToast(error.message, 'error');
            }
        }
    }

    refreshManagementModal() {
        const config = db.getConfig();
        const cardsList = document.getElementById('cards-list');

        cardsList.innerHTML = '';
        config.cards.forEach(card => {
            const li = document.createElement('li');
            const cardTypeLabel = card.type === 'cash' ? '' : ` (${card.type})`;
            li.innerHTML = `
                <span class="card-item">
                    ${card.name}${cardTypeLabel}
                    ${card.name !== 'Cash' ? `<button class="remove-btn" onclick="app.removeCard('${card.name}')">Remove</button>` : ''}
                </span>
            `;
            cardsList.appendChild(li);
        });
    }

    exportData() {
        try {
            const data = db.exportData();
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `finance-data-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showToast('Data exported successfully', 'success');
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    importData(file) {
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                db.importData(e.target.result);
                this.refreshDashboard();
                this.refreshTransactionList();
                this.loadCardOptions();
                this.showToast('Data imported successfully', 'success');
                this.closeModal('management-modal');
                document.getElementById('import-file').value = '';
            } catch (error) {
                this.showToast(error.message, 'error');
            }
        };
        reader.readAsText(file);
    }

    clearAllData() {
        if (confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
            if (confirm('This will delete ALL transactions and settings. Are you absolutely sure?')) {
                try {
                    db.clearAllData();
                    this.refreshDashboard();
                    this.refreshTransactionList();
                    this.loadCardOptions();
                    this.showToast('All data cleared successfully', 'success');
                    this.closeModal('management-modal');
                } catch (error) {
                    this.showToast(error.message, 'error');
                }
            }
        }
    }

    showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toastContainer.contains(toast)) {
                    toastContainer.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}

const app = new FinanceApp();