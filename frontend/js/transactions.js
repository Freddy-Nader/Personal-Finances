// Transaction Management JavaScript
class TransactionManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 20;
        this.filters = {};
        this.transactions = [];
        this.cards = [];
        this.editingTransaction = null;

        this.initializeEventListeners();
        this.loadInitialData();
    }

    initializeEventListeners() {
        // Add transaction button
        const addBtn = document.getElementById('addTransactionBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.openTransactionModal());
        }

        // Filter controls
        const applyFiltersBtn = document.getElementById('applyFilters');
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => this.applyFilters());
        }

        const clearFiltersBtn = document.getElementById('clearFilters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }

        // Modal controls
        const closeModal = document.getElementById('closeModal');
        if (closeModal) {
            closeModal.addEventListener('click', () => this.closeTransactionModal());
        }

        const cancelBtn = document.getElementById('cancelBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.closeTransactionModal());
        }

        // Form submission
        const transactionForm = document.getElementById('transactionForm');
        if (transactionForm) {
            transactionForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Internal transfer toggle
        const internalTransferCheckbox = document.getElementById('isInternalTransfer');
        if (internalTransferCheckbox) {
            internalTransferCheckbox.addEventListener('change', (e) => {
                this.toggleTransferSection(e.target.checked);
            });
        }

        // Card selection change
        const cardSelect = document.getElementById('cardSelect');
        if (cardSelect) {
            cardSelect.addEventListener('change', () => this.loadSections());
        }

        // Transfer type changes
        const transferFromType = document.getElementById('transferFromType');
        const transferToType = document.getElementById('transferToType');
        if (transferFromType) {
            transferFromType.addEventListener('change', () => this.updateTransferAccounts('from'));
        }
        if (transferToType) {
            transferToType.addEventListener('change', () => this.updateTransferAccounts('to'));
        }

        // Modal click outside to close
        const modal = document.getElementById('transactionModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeTransactionModal();
                }
            });
        }
    }

    async loadInitialData() {
        try {
            this.showLoading();

            // Load cards and transactions in parallel
            await Promise.all([
                this.loadCards(),
                this.loadTransactions()
            ]);

        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showError('Failed to load transaction data. Please refresh the page.');
        }
    }

    async loadCards() {
        try {
            this.cards = await api.getCards();
            this.populateCardSelectors();
        } catch (error) {
            console.error('Failed to load cards:', error);
            this.cards = [];
        }
    }

    populateCardSelectors() {
        const selectors = [
            document.getElementById('cardFilter'),
            document.getElementById('cardSelect')
        ];

        selectors.forEach(selector => {
            if (!selector) return;

            // Clear existing options (except first one for filters)
            const isFilter = selector.id === 'cardFilter';
            while (selector.children.length > (isFilter ? 1 : 0)) {
                selector.removeChild(selector.lastChild);
            }

            // Add card options
            this.cards.forEach(card => {
                const option = document.createElement('option');
                option.value = card.id;
                option.textContent = `${card.name} (${card.type})`;
                selector.appendChild(option);
            });
        });
    }

    async loadSections() {
        const cardSelect = document.getElementById('cardSelect');
        const sectionSelect = document.getElementById('sectionSelect');

        if (!cardSelect || !sectionSelect) return;

        const cardId = cardSelect.value;

        // Clear existing sections (except first option)
        while (sectionSelect.children.length > 1) {
            sectionSelect.removeChild(sectionSelect.lastChild);
        }

        if (!cardId) return;

        try {
            const sections = await api.getCardSections(cardId);
            sections.forEach(section => {
                const option = document.createElement('option');
                option.value = section.id;
                option.textContent = section.name;
                sectionSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Failed to load sections:', error);
        }
    }

    async loadTransactions() {
        try {
            const params = {
                page: this.currentPage,
                limit: this.pageSize,
                ...this.filters
            };

            const response = await api.getTransactions(params);
            this.transactions = response.transactions || response;

            this.displayTransactions();
            this.updatePagination(response);
            this.updateTransactionCount(response.total || this.transactions.length);

        } catch (error) {
            console.error('Failed to load transactions:', error);
            this.showError('Failed to load transactions.');
            this.displayEmptyState();
        }
    }

    displayTransactions() {
        const tbody = document.getElementById('transactionTableBody');
        if (!tbody) return;

        if (!this.transactions || this.transactions.length === 0) {
            this.displayEmptyState();
            return;
        }

        const transactionRows = this.transactions.map(transaction => {
            const amount = parseFloat(transaction.amount);
            const amountClass = amount >= 0 ? 'text-positive' : 'text-negative';
            const amountText = FinanceUtils.formatCurrency(Math.abs(amount), 'USD', true);
            const date = FinanceUtils.formatDate(transaction.transaction_date, 'short');
            const cardName = this.getCardName(transaction.card_id);

            return `
                <tr class="transaction-row" data-id="${transaction.id}">
                    <td>${date}</td>
                    <td>${transaction.description}</td>
                    <td>
                        <span class="category-tag">${transaction.category || 'Uncategorized'}</span>
                    </td>
                    <td>${cardName}</td>
                    <td class="${amountClass} font-mono">${amountText}</td>
                    <td class="action-buttons">
                        <button class="btn btn-sm secondary-btn" onclick="transactionManager.editTransaction(${transaction.id})">
                            Edit
                        </button>
                        <button class="btn btn-sm danger-btn" onclick="transactionManager.deleteTransaction(${transaction.id})">
                            Delete
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        tbody.innerHTML = transactionRows;
    }

    displayEmptyState() {
        const tbody = document.getElementById('transactionTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="6" class="empty-state">
                        No transactions found.
                        <button class="primary-btn" onclick="transactionManager.openTransactionModal()">
                            Add your first transaction
                        </button>
                    </td>
                </tr>
            `;
        }
    }

    getCardName(cardId) {
        if (!cardId) return 'Cash';
        const card = this.cards.find(c => c.id === cardId);
        return card ? card.name : 'Unknown Card';
    }

    updatePagination(response) {
        const paginationContainer = document.getElementById('pagination');
        if (!paginationContainer) return;

        const totalPages = response.total ? Math.ceil(response.total / this.pageSize) : 1;

        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }

        paginationContainer.innerHTML = UIComponents.createPagination(
            this.currentPage,
            totalPages,
            'transactionManager.goToPage'
        );
    }

    updateTransactionCount(total) {
        const countElement = document.getElementById('transactionCount');
        const paginationInfo = document.getElementById('paginationInfo');

        if (countElement) {
            countElement.textContent = `${total} transaction${total !== 1 ? 's' : ''}`;
        }

        if (paginationInfo) {
            const totalPages = Math.ceil(total / this.pageSize);
            paginationInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        }
    }

    applyFilters() {
        const cardFilter = document.getElementById('cardFilter').value;
        const categoryFilter = document.getElementById('categoryFilter').value;
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;

        this.filters = {};
        if (cardFilter) this.filters.cardId = cardFilter;
        if (categoryFilter) this.filters.category = categoryFilter;
        if (startDate) this.filters.startDate = startDate;
        if (endDate) this.filters.endDate = endDate;

        this.currentPage = 1;
        this.loadTransactions();
    }

    clearFilters() {
        // Clear form inputs
        document.getElementById('cardFilter').value = '';
        document.getElementById('categoryFilter').value = '';
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';

        // Clear filters and reload
        this.filters = {};
        this.currentPage = 1;
        this.loadTransactions();
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadTransactions();
    }

    openTransactionModal(transaction = null) {
        this.editingTransaction = transaction;

        const modal = document.getElementById('transactionModal');
        const modalTitle = document.getElementById('modalTitle');
        const form = document.getElementById('transactionForm');

        if (transaction) {
            modalTitle.textContent = 'Edit Transaction';
            this.populateForm(transaction);
        } else {
            modalTitle.textContent = 'Add Transaction';
            form.reset();
            this.setDefaultFormValues();
        }

        UIComponents.showModal('transactionModal');
    }

    closeTransactionModal() {
        UIComponents.hideModal('transactionModal');
        this.editingTransaction = null;
        this.toggleTransferSection(false);
    }

    populateForm(transaction) {
        document.getElementById('amount').value = transaction.amount;
        document.getElementById('description').value = transaction.description;
        document.getElementById('transactionDate').value = FinanceUtils.formatDateForInput(transaction.transaction_date);
        document.getElementById('cardSelect').value = transaction.card_id || '';
        document.getElementById('category').value = transaction.category || '';
        document.getElementById('isInternalTransfer').checked = transaction.is_internal_transfer || false;

        // Load sections for the selected card
        if (transaction.card_id) {
            this.loadSections().then(() => {
                document.getElementById('sectionSelect').value = transaction.section_id || '';
            });
        }

        // Handle transfer fields
        if (transaction.is_internal_transfer) {
            this.toggleTransferSection(true);
            document.getElementById('transferFromType').value = transaction.transfer_from_type || '';
            document.getElementById('transferFromId').value = transaction.transfer_from_id || '';
            document.getElementById('transferToType').value = transaction.transfer_to_type || '';
            document.getElementById('transferToId').value = transaction.transfer_to_id || '';
        }
    }

    setDefaultFormValues() {
        const now = new Date();
        document.getElementById('transactionDate').value = FinanceUtils.formatDateForInput(now);
        document.getElementById('isInternalTransfer').checked = false;
    }

    toggleTransferSection(show) {
        const transferSection = document.getElementById('transferSection');
        if (transferSection) {
            transferSection.style.display = show ? 'block' : 'none';
        }

        // Clear transfer fields when hiding
        if (!show) {
            ['transferFromType', 'transferFromId', 'transferToType', 'transferToId'].forEach(id => {
                const element = document.getElementById(id);
                if (element) element.value = '';
            });
        }
    }

    updateTransferAccounts(direction) {
        const typeSelect = document.getElementById(`transfer${direction === 'from' ? 'From' : 'To'}Type`);
        const accountSelect = document.getElementById(`transfer${direction === 'from' ? 'From' : 'To'}Id`);

        if (!typeSelect || !accountSelect) return;

        // Clear existing options
        while (accountSelect.children.length > 1) {
            accountSelect.removeChild(accountSelect.lastChild);
        }

        const type = typeSelect.value;

        if (type === 'card') {
            this.cards.forEach(card => {
                const option = document.createElement('option');
                option.value = card.id;
                option.textContent = card.name;
                accountSelect.appendChild(option);
            });
        }
        // Additional types (cash, stock, crypto) would be implemented here
    }

    async handleFormSubmit(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const transactionData = this.buildTransactionData(formData);

        // Validate form
        const validation = this.validateTransaction(transactionData);
        if (!validation.isValid) {
            this.showError(validation.errors.join(', '));
            return;
        }

        try {
            if (this.editingTransaction) {
                await api.updateTransaction(this.editingTransaction.id, transactionData);
                UIComponents.createNotification('Transaction updated successfully', 'success');
            } else {
                await api.createTransaction(transactionData);
                UIComponents.createNotification('Transaction added successfully', 'success');
            }

            this.closeTransactionModal();
            this.loadTransactions();

        } catch (error) {
            console.error('Failed to save transaction:', error);
            this.showError('Failed to save transaction. Please try again.');
        }
    }

    buildTransactionData(formData) {
        return {
            amount: parseFloat(formData.get('amount')),
            description: formData.get('description'),
            transaction_date: formData.get('transactionDate'),
            card_id: formData.get('cardSelect') || null,
            section_id: formData.get('sectionSelect') || null,
            category: formData.get('category') || null,
            is_internal_transfer: formData.get('isInternalTransfer') === 'on',
            transfer_from_type: formData.get('transferFromType') || null,
            transfer_from_id: formData.get('transferFromId') || null,
            transfer_to_type: formData.get('transferToType') || null,
            transfer_to_id: formData.get('transferToId') || null
        };
    }

    validateTransaction(data) {
        const errors = [];

        if (!data.description || data.description.trim() === '') {
            errors.push('Description is required');
        }

        if (isNaN(data.amount)) {
            errors.push('Valid amount is required');
        }

        if (!data.transaction_date) {
            errors.push('Transaction date is required');
        }

        if (data.is_internal_transfer) {
            if (!data.transfer_from_type || !data.transfer_to_type) {
                errors.push('Transfer from and to types are required for internal transfers');
            }
            if (!data.transfer_from_id || !data.transfer_to_id) {
                errors.push('Transfer from and to accounts are required for internal transfers');
            }
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    async editTransaction(transactionId) {
        try {
            const transaction = await api.getTransaction(transactionId);
            this.openTransactionModal(transaction);
        } catch (error) {
            console.error('Failed to load transaction for editing:', error);
            this.showError('Failed to load transaction details.');
        }
    }

    async deleteTransaction(transactionId) {
        if (!confirm('Are you sure you want to delete this transaction?')) {
            return;
        }

        try {
            await api.deleteTransaction(transactionId);
            UIComponents.createNotification('Transaction deleted successfully', 'success');
            this.loadTransactions();
        } catch (error) {
            console.error('Failed to delete transaction:', error);
            this.showError('Failed to delete transaction.');
        }
    }

    showLoading() {
        const tbody = document.getElementById('transactionTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr class="loading-row">
                    <td colspan="6" class="loading">Loading transactions...</td>
                </tr>
            `;
        }
    }

    showError(message) {
        UIComponents.createNotification(message, 'error');
    }
}

// Initialize transaction manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.transactionManager = new TransactionManager();
});

// Global functions for button clicks
function editTransaction(id) {
    if (window.transactionManager) {
        window.transactionManager.editTransaction(id);
    }
}

function deleteTransaction(id) {
    if (window.transactionManager) {
        window.transactionManager.deleteTransaction(id);
    }
}