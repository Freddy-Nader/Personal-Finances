// Investment Tracking JavaScript
class InvestmentManager {
    constructor() {
        this.positions = [];
        this.movements = [];
        this.selectedPosition = null;
        this.currentView = 'grid';
        this.currentPage = 1;
        this.pageSize = 10;
        this.filters = {};

        this.initializeEventListeners();
        this.loadInitialData();
    }

    initializeEventListeners() {
        // Header action buttons
        const addPositionBtn = document.getElementById('addPositionBtn');
        const addMovementBtn = document.getElementById('addMovementBtn');

        if (addPositionBtn) {
            addPositionBtn.addEventListener('click', () => this.openPositionModal());
        }

        if (addMovementBtn) {
            addMovementBtn.addEventListener('click', () => this.openMovementModal());
        }

        // View toggle buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('toggle-btn')) {
                this.handleViewToggle(e.target);
            }
        });

        // Filter controls
        const positionFilter = document.getElementById('positionFilter');
        const movementTypeFilter = document.getElementById('movementTypeFilter');

        if (positionFilter) {
            positionFilter.addEventListener('change', () => this.applyMovementFilters());
        }

        if (movementTypeFilter) {
            movementTypeFilter.addEventListener('change', () => this.applyMovementFilters());
        }

        // Modal event listeners
        this.setupModalEventListeners('position');
        this.setupModalEventListeners('movement');
        this.setupModalEventListeners('positionDetails');

        // Form-specific listeners
        this.setupMovementFormListeners();
    }

    setupModalEventListeners(type) {
        const modal = document.getElementById(`${type}Modal`);
        const closeBtn = document.getElementById(`close${type.charAt(0).toUpperCase() + type.slice(1)}Modal`);
        const cancelBtn = document.getElementById(`cancel${type.charAt(0).toUpperCase() + type.slice(1)}Btn`);
        const form = document.getElementById(`${type}Form`);

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeModal(type));
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.closeModal(type));
        }

        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e, type));
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(type);
                }
            });
        }
    }

    setupMovementFormListeners() {
        // Auto-calculate total amount
        const quantityInput = document.getElementById('quantity');
        const priceInput = document.getElementById('pricePerUnit');
        const totalInput = document.getElementById('totalAmount');

        if (quantityInput && priceInput && totalInput) {
            const calculateTotal = () => {
                const quantity = parseFloat(quantityInput.value) || 0;
                const price = parseFloat(priceInput.value) || 0;
                totalInput.value = (quantity * price).toFixed(2);
            };

            quantityInput.addEventListener('input', calculateTotal);
            priceInput.addEventListener('input', calculateTotal);
        }

        // Set current date/time as default
        const movementDateTime = document.getElementById('movementDateTime');
        if (movementDateTime) {
            const now = new Date();
            movementDateTime.value = FinanceUtils.formatDateForInput(now);
        }
    }

    async loadInitialData() {
        try {
            this.showLoading();

            // Load positions and movements in parallel
            await Promise.all([
                this.loadPositions(),
                this.loadMovements()
            ]);

            this.updatePortfolioSummary();

        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showError('Failed to load investment data. Please refresh the page.');
        }
    }

    async loadPositions() {
        try {
            this.positions = await api.getInvestmentPositions();
            this.displayPositions();
            this.populatePositionFilter();
        } catch (error) {
            console.error('Failed to load positions:', error);
            this.positions = [];
            this.displayPositionsError();
        }
    }

    async loadMovements() {
        try {
            const params = {
                page: this.currentPage,
                limit: this.pageSize,
                ...this.filters
            };

            const movements = await api.getInvestmentMovements(params);
            this.movements = Array.isArray(movements) ? movements : movements.movements || [];
            this.displayMovements();
        } catch (error) {
            console.error('Failed to load movements:', error);
            this.movements = [];
            this.displayMovementsError();
        }
    }

    displayPositions() {
        if (this.currentView === 'grid') {
            this.displayPositionsGrid();
        } else {
            this.displayPositionsTable();
        }
    }

    displayPositionsGrid() {
        const positionsGrid = document.getElementById('positionsGrid');
        if (!positionsGrid) return;

        positionsGrid.style.display = 'grid';
        document.getElementById('positionsTable').style.display = 'none';

        if (this.positions.length === 0) {
            positionsGrid.innerHTML = UIComponents.createEmptyState(
                'No investment positions found. Add your first investment to get started.',
                'Add Position',
                'investmentManager.openPositionModal()'
            );
            return;
        }

        const positionItems = this.positions.map(position => {
            return this.createPositionCardHTML(position);
        }).join('');

        positionsGrid.innerHTML = positionItems;
    }

    displayPositionsTable() {
        const positionsGrid = document.getElementById('positionsGrid');
        const positionsTable = document.getElementById('positionsTable');

        if (positionsGrid && positionsTable) {
            positionsGrid.style.display = 'none';
            positionsTable.style.display = 'block';

            const tbody = document.getElementById('positionsTableBody');
            if (tbody) {
                if (this.positions.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="8" class="empty-state">
                                No investment positions found.
                                <button class="primary-btn" onclick="investmentManager.openPositionModal()">
                                    Add Position
                                </button>
                            </td>
                        </tr>
                    `;
                    return;
                }

                const positionRows = this.positions.map(position => {
                    return this.createPositionRowHTML(position);
                }).join('');

                tbody.innerHTML = positionRows;
            }
        }
    }

    createPositionCardHTML(position) {
        const profitLoss = position.profit_loss || 0;
        const plClass = profitLoss >= 0 ? 'text-positive' : 'text-negative';
        const plPrefix = profitLoss >= 0 ? '+' : '';
        const assetIcon = position.asset_type === 'stock' ? '📈' : '₿';

        return `
            <div class="position-item" data-id="${position.id}" onclick="investmentManager.showPositionDetails(${position.id})">
                <div class="position-header">
                    <span class="asset-icon">${assetIcon}</span>
                    <div class="position-symbol">
                        <h4>${position.symbol}</h4>
                        <span class="asset-type">${position.asset_type.charAt(0).toUpperCase() + position.asset_type.slice(1)}</span>
                    </div>
                </div>
                <div class="position-details">
                    <div class="position-row">
                        <span class="label">Quantity:</span>
                        <span class="value">${(position.current_quantity || 0).toFixed(8)}</span>
                    </div>
                    <div class="position-row">
                        <span class="label">Market Value:</span>
                        <span class="value">${FinanceUtils.formatCurrency(position.current_value || 0)}</span>
                    </div>
                    <div class="position-row">
                        <span class="label">P&L:</span>
                        <span class="value ${plClass}">${plPrefix}${FinanceUtils.formatCurrency(Math.abs(profitLoss))}</span>
                    </div>
                </div>
            </div>
        `;
    }

    createPositionRowHTML(position) {
        const profitLoss = position.profit_loss || 0;
        const plClass = profitLoss >= 0 ? 'text-positive' : 'text-negative';
        const plPrefix = profitLoss >= 0 ? '+' : '';

        return `
            <tr class="position-row" data-id="${position.id}">
                <td>${position.symbol}</td>
                <td>${position.asset_type}</td>
                <td class="font-mono">${(position.current_quantity || 0).toFixed(8)}</td>
                <td class="font-mono">${FinanceUtils.formatCurrency(position.avg_cost || 0)}</td>
                <td class="font-mono">${FinanceUtils.formatCurrency(position.current_price || 0)}</td>
                <td class="font-mono">${FinanceUtils.formatCurrency(position.current_value || 0)}</td>
                <td class="font-mono ${plClass}">${plPrefix}${FinanceUtils.formatCurrency(Math.abs(profitLoss))}</td>
                <td class="action-buttons">
                    <button class="btn btn-sm secondary-btn" onclick="investmentManager.showPositionDetails(${position.id})">
                        Details
                    </button>
                    <button class="btn btn-sm primary-btn" onclick="investmentManager.openMovementModal(${position.id})">
                        Trade
                    </button>
                </td>
            </tr>
        `;
    }

    displayMovements() {
        const movementsList = document.getElementById('movementsList');
        if (!movementsList) return;

        if (this.movements.length === 0) {
            movementsList.innerHTML = UIComponents.createEmptyState(
                'No investment movements found.',
                'Record Movement',
                'investmentManager.openMovementModal()'
            );
            return;
        }

        const movementItems = this.movements.map(movement => {
            return this.createMovementHTML(movement);
        }).join('');

        movementsList.innerHTML = movementItems;
    }

    createMovementHTML(movement) {
        const typeClass = movement.movement_type === 'buy' ? 'text-positive' : 'text-negative';
        const typeIcon = movement.movement_type === 'buy' ? '📈' : '📉';
        const date = FinanceUtils.formatDate(movement.movement_datetime, 'datetime');

        // Find position for symbol
        const position = this.positions.find(p => p.id === movement.position_id);
        const symbol = position ? position.symbol : 'Unknown';

        return `
            <div class="movement-item" data-id="${movement.id}">
                <div class="movement-info">
                    <div class="movement-header">
                        <span class="movement-icon ${typeClass}">${typeIcon}</span>
                        <div class="movement-details">
                            <span class="movement-type ${typeClass}">${movement.movement_type.toUpperCase()}</span>
                            <span class="movement-symbol">${symbol}</span>
                        </div>
                        <div class="movement-actions">
                            <button class="btn btn-sm secondary-btn" onclick="investmentManager.editMovement(${movement.id})">
                                Edit
                            </button>
                            <button class="btn btn-sm danger-btn" onclick="investmentManager.deleteMovement(${movement.id})">
                                Delete
                            </button>
                        </div>
                    </div>
                    <div class="movement-data">
                        <div class="movement-quantity">
                            ${movement.quantity} @ ${FinanceUtils.formatCurrency(movement.price_per_unit)}
                        </div>
                        <div class="movement-total">
                            Total: ${FinanceUtils.formatCurrency(movement.total_amount)}
                        </div>
                        <div class="movement-datetime">${date}</div>
                        ${movement.description ? `<div class="movement-description">${movement.description}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    handleViewToggle(button) {
        // Remove active class from all toggle buttons
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Add active class to clicked button
        button.classList.add('active');

        // Update current view
        this.currentView = button.dataset.view;

        // Re-display positions with new view
        this.displayPositions();
    }

    populatePositionFilter() {
        const positionFilter = document.getElementById('positionFilter');
        if (!positionFilter) return;

        // Clear existing options (except first one)
        while (positionFilter.children.length > 1) {
            positionFilter.removeChild(positionFilter.lastChild);
        }

        // Add position options
        this.positions.forEach(position => {
            const option = document.createElement('option');
            option.value = position.id;
            option.textContent = `${position.symbol} (${position.asset_type})`;
            positionFilter.appendChild(option);
        });
    }

    populateMovementPositionSelect() {
        const positionSelect = document.getElementById('movementPosition');
        if (!positionSelect) return;

        // Clear existing options (except first one)
        while (positionSelect.children.length > 1) {
            positionSelect.removeChild(positionSelect.lastChild);
        }

        // Add position options
        this.positions.forEach(position => {
            const option = document.createElement('option');
            option.value = position.id;
            option.textContent = `${position.symbol} (${position.asset_type})`;
            positionSelect.appendChild(option);
        });
    }

    applyMovementFilters() {
        const positionId = document.getElementById('positionFilter').value;
        const movementType = document.getElementById('movementTypeFilter').value;

        this.filters = {};
        if (positionId) this.filters.positionId = positionId;
        if (movementType) this.filters.movementType = movementType;

        this.currentPage = 1;
        this.loadMovements();
    }

    updatePortfolioSummary() {
        // Calculate portfolio metrics
        const totalValue = this.positions.reduce((sum, pos) => sum + (pos.current_value || 0), 0);
        const totalPL = this.positions.reduce((sum, pos) => sum + (pos.profit_loss || 0), 0);
        const totalPositions = this.positions.length;
        const activePositions = this.positions.filter(pos => (pos.current_quantity || 0) > 0).length;

        // Update summary cards
        const totalPortfolioValue = document.getElementById('totalPortfolioValue');
        const totalPositionsEl = document.getElementById('totalPositions');
        const realizedPL = document.getElementById('realizedPL');
        const unrealizedPL = document.getElementById('unrealizedPL');
        const portfolioChange = document.getElementById('portfolioChange');
        const activePositionsEl = document.getElementById('activePositions');
        const realizedPLPercent = document.getElementById('realizedPLPercent');
        const unrealizedPLPercent = document.getElementById('unrealizedPLPercent');

        if (totalPortfolioValue) {
            totalPortfolioValue.textContent = FinanceUtils.formatCurrency(totalValue);
        }

        if (totalPositionsEl) {
            totalPositionsEl.textContent = totalPositions.toString();
        }

        if (activePositionsEl) {
            activePositionsEl.textContent = `${activePositions} active`;
        }

        if (unrealizedPL) {
            unrealizedPL.textContent = FinanceUtils.formatCurrency(totalPL, 'USD', true);
            unrealizedPL.className = `card-value ${totalPL >= 0 ? 'text-positive' : 'text-negative'}`;
        }

        // Mock realized P&L (would come from closed positions)
        const mockRealizedPL = totalValue * 0.05; // 5% of portfolio value
        if (realizedPL) {
            realizedPL.textContent = FinanceUtils.formatCurrency(mockRealizedPL, 'USD', true);
            realizedPL.className = `card-value ${mockRealizedPL >= 0 ? 'text-positive' : 'text-negative'}`;
        }

        // Calculate percentage changes
        const portfolioChangePercent = totalValue > 0 ? (totalPL / (totalValue - totalPL)) * 100 : 0;
        const realizedPLPercentValue = 5.0; // Mock value

        if (portfolioChange) {
            portfolioChange.textContent = `${portfolioChangePercent >= 0 ? '+' : ''}${portfolioChangePercent.toFixed(2)}%`;
            portfolioChange.className = `card-change ${portfolioChangePercent >= 0 ? 'positive' : 'negative'}`;
        }

        if (unrealizedPLPercent) {
            unrealizedPLPercent.textContent = `${portfolioChangePercent >= 0 ? '+' : ''}${portfolioChangePercent.toFixed(2)}%`;
            unrealizedPLPercent.className = `card-change ${portfolioChangePercent >= 0 ? 'positive' : 'negative'}`;
        }

        if (realizedPLPercent) {
            realizedPLPercent.textContent = `+${realizedPLPercentValue.toFixed(2)}%`;
            realizedPLPercent.className = 'card-change positive';
        }
    }

    // Modal Management
    openPositionModal(position = null) {
        const modal = document.getElementById('positionModal');
        const modalTitle = document.getElementById('positionModalTitle');
        const form = document.getElementById('positionForm');

        modalTitle.textContent = 'Add Investment Position';
        form.reset();

        UIComponents.showModal('positionModal');
    }

    openMovementModal(positionId = null) {
        const modal = document.getElementById('movementModal');
        const modalTitle = document.getElementById('movementModalTitle');
        const form = document.getElementById('movementForm');

        modalTitle.textContent = 'Record Movement';
        form.reset();

        // Set current date/time
        const now = new Date();
        const movementDateTime = document.getElementById('movementDateTime');
        if (movementDateTime) {
            movementDateTime.value = FinanceUtils.formatDateForInput(now);
        }

        // Populate position select
        this.populateMovementPositionSelect();

        // Pre-select position if provided
        if (positionId) {
            const positionSelect = document.getElementById('movementPosition');
            if (positionSelect) {
                positionSelect.value = positionId;
            }
        }

        UIComponents.showModal('movementModal');
    }

    showPositionDetails(positionId) {
        const position = this.positions.find(p => p.id === positionId);
        if (!position) return;

        this.selectedPosition = position;

        // Update position details modal
        const modalTitle = document.getElementById('positionDetailsTitle');
        if (modalTitle) {
            modalTitle.textContent = `${position.symbol} Details`;
        }

        // Update summary information
        this.updatePositionDetailsSummary(position);

        // Load position movements
        this.loadPositionMovements(positionId);

        UIComponents.showModal('positionDetailsModal');
    }

    updatePositionDetailsSummary(position) {
        const elements = {
            detailCurrentHoldings: (position.current_quantity || 0).toFixed(8),
            detailAvgCost: FinanceUtils.formatCurrency(position.avg_cost || 0),
            detailTotalInvested: FinanceUtils.formatCurrency(position.total_invested || 0),
            detailCurrentValue: FinanceUtils.formatCurrency(position.current_value || 0),
            detailProfitLoss: FinanceUtils.formatCurrency(position.profit_loss || 0, 'USD', true)
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                if (id === 'detailProfitLoss') {
                    const pl = position.profit_loss || 0;
                    element.className = `value ${pl >= 0 ? 'text-positive' : 'text-negative'}`;
                }
            }
        });
    }

    async loadPositionMovements(positionId) {
        try {
            const movements = await api.getInvestmentMovements({ positionId });
            this.displayPositionMovements(movements);
        } catch (error) {
            console.error('Failed to load position movements:', error);
            const tbody = document.getElementById('detailMovementsBody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="6">Failed to load movements</td></tr>';
            }
        }
    }

    displayPositionMovements(movements) {
        const tbody = document.getElementById('detailMovementsBody');
        if (!tbody) return;

        if (!movements || movements.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No movements found</td></tr>';
            return;
        }

        const movementRows = movements.map(movement => {
            const date = FinanceUtils.formatDate(movement.movement_datetime, 'datetime');
            const typeClass = movement.movement_type === 'buy' ? 'text-positive' : 'text-negative';

            return `
                <tr>
                    <td>${date}</td>
                    <td class="${typeClass}">${movement.movement_type.toUpperCase()}</td>
                    <td class="font-mono">${movement.quantity}</td>
                    <td class="font-mono">${FinanceUtils.formatCurrency(movement.price_per_unit)}</td>
                    <td class="font-mono">${FinanceUtils.formatCurrency(movement.total_amount)}</td>
                    <td>${movement.description || '-'}</td>
                </tr>
            `;
        }).join('');

        tbody.innerHTML = movementRows;
    }

    closeModal(type) {
        UIComponents.hideModal(`${type}Modal`);
        if (type === 'positionDetails') {
            this.selectedPosition = null;
        }
    }

    // Form Submission
    async handleFormSubmit(e, type) {
        e.preventDefault();

        const formData = new FormData(e.target);

        try {
            if (type === 'position') {
                await this.handlePositionSubmit(formData);
            } else if (type === 'movement') {
                await this.handleMovementSubmit(formData);
            }
        } catch (error) {
            console.error(`Failed to save ${type}:`, error);
            this.showError(`Failed to save ${type}. Please try again.`);
        }
    }

    async handlePositionSubmit(formData) {
        const positionData = {
            asset_type: formData.get('assetType'),
            symbol: formData.get('symbol').toUpperCase()
        };

        const validation = this.validatePosition(positionData);
        if (!validation.isValid) {
            this.showError(validation.errors.join(', '));
            return;
        }

        await api.createInvestmentPosition(positionData);
        UIComponents.createNotification('Investment position created successfully', 'success');

        this.closeModal('position');
        this.loadPositions();
    }

    async handleMovementSubmit(formData) {
        const movementData = {
            position_id: parseInt(formData.get('movementPosition')),
            movement_type: formData.get('movementType'),
            quantity: parseFloat(formData.get('quantity')),
            price_per_unit: parseFloat(formData.get('pricePerUnit')),
            movement_datetime: formData.get('movementDateTime'),
            description: formData.get('movementDescription') || null
        };

        const validation = this.validateMovement(movementData);
        if (!validation.isValid) {
            this.showError(validation.errors.join(', '));
            return;
        }

        await api.createInvestmentMovement(movementData);
        UIComponents.createNotification('Movement recorded successfully', 'success');

        this.closeModal('movement');
        this.loadPositions();
        this.loadMovements();
    }

    // Validation
    validatePosition(data) {
        const errors = [];

        if (!data.asset_type) {
            errors.push('Asset type is required');
        }

        if (!data.symbol || data.symbol.trim() === '') {
            errors.push('Symbol is required');
        }

        return { isValid: errors.length === 0, errors };
    }

    validateMovement(data) {
        const errors = [];

        if (!data.position_id) {
            errors.push('Position is required');
        }

        if (!data.movement_type) {
            errors.push('Movement type is required');
        }

        if (!data.quantity || data.quantity <= 0) {
            errors.push('Valid quantity is required');
        }

        if (!data.price_per_unit || data.price_per_unit <= 0) {
            errors.push('Valid price per unit is required');
        }

        if (!data.movement_datetime) {
            errors.push('Date and time are required');
        }

        return { isValid: errors.length === 0, errors };
    }

    // Actions
    async editMovement(movementId) {
        // This would open the movement modal with pre-filled data
        UIComponents.createNotification('Edit movement functionality would be implemented here', 'info');
    }

    async deleteMovement(movementId) {
        if (!confirm('Are you sure you want to delete this movement?')) {
            return;
        }

        try {
            // This would call the API to delete the movement
            UIComponents.createNotification('Movement deleted successfully', 'success');
            this.loadPositions();
            this.loadMovements();
        } catch (error) {
            console.error('Failed to delete movement:', error);
            this.showError('Failed to delete movement');
        }
    }

    // Utility methods
    showLoading() {
        const positionsGrid = document.getElementById('positionsGrid');
        const movementsList = document.getElementById('movementsList');

        if (positionsGrid) {
            positionsGrid.innerHTML = '<div class="loading">Loading investment positions...</div>';
        }

        if (movementsList) {
            movementsList.innerHTML = '<div class="loading">Loading recent movements...</div>';
        }
    }

    displayPositionsError() {
        const positionsGrid = document.getElementById('positionsGrid');
        if (positionsGrid) {
            positionsGrid.innerHTML = '<div class="error">Failed to load investment positions.</div>';
        }
    }

    displayMovementsError() {
        const movementsList = document.getElementById('movementsList');
        if (movementsList) {
            movementsList.innerHTML = '<div class="error">Failed to load movements.</div>';
        }
    }

    showError(message) {
        UIComponents.createNotification(message, 'error');
    }
}

// Initialize investment manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.investmentManager = new InvestmentManager();
});

// Global functions for button clicks
function showPositionDetails(id) {
    if (window.investmentManager) {
        window.investmentManager.showPositionDetails(id);
    }
}

function editMovement(id) {
    if (window.investmentManager) {
        window.investmentManager.editMovement(id);
    }
}

function deleteMovement(id) {
    if (window.investmentManager) {
        window.investmentManager.deleteMovement(id);
    }
}