// Reusable UI Components for Personal Finance Application

class UIComponents {
    // Create a loading spinner
    static createLoadingSpinner(text = 'Loading...') {
        return `
            <div class="loading">
                <div class="spinner"></div>
                <span>${text}</span>
            </div>
        `;
    }

    // Create an empty state message
    static createEmptyState(message, actionText = null, actionCallback = null) {
        const actionButton = actionText && actionCallback
            ? `<button class="primary-btn" onclick="${actionCallback}">${actionText}</button>`
            : '';

        return `
            <div class="empty-state">
                <p>${message}</p>
                ${actionButton}
            </div>
        `;
    }

    // Create a transaction list item
    static createTransactionItem(transaction) {
        const amount = parseFloat(transaction.amount);
        const amountClass = amount >= 0 ? 'text-positive' : 'text-negative';
        const amountPrefix = amount >= 0 ? '+' : '';
        const formattedAmount = `${amountPrefix}$${Math.abs(amount).toFixed(2)}`;
        const date = new Date(transaction.transaction_date).toLocaleDateString();

        return `
            <tr class="transaction-item" data-id="${transaction.id}">
                <td>${date}</td>
                <td>${transaction.description}</td>
                <td>${transaction.category || '-'}</td>
                <td>${transaction.card_name || 'Cash'}</td>
                <td class="${amountClass} font-mono">${formattedAmount}</td>
                <td>
                    <button class="btn btn-sm" onclick="editTransaction(${transaction.id})">Edit</button>
                    <button class="btn btn-sm danger-btn" onclick="deleteTransaction(${transaction.id})">Delete</button>
                </td>
            </tr>
        `;
    }

    // Create a card item
    static createCardItem(card, selected = false) {
        const balanceClass = card.balance >= 0 ? 'text-positive' : 'text-negative';
        const selectedClass = selected ? 'selected' : '';
        const cardTypeIcon = card.type === 'credit' ? '💳' : '🏦';

        return `
            <div class="card-item ${selectedClass}" data-id="${card.id}" onclick="selectCard(${card.id})">
                <div class="card-header">
                    <span class="card-icon">${cardTypeIcon}</span>
                    <h4>${card.name}</h4>
                </div>
                <div class="card-details">
                    <div class="card-type">${card.type.charAt(0).toUpperCase() + card.type.slice(1)} Card</div>
                    <div class="card-balance ${balanceClass}">$${Math.abs(card.balance).toFixed(2)}</div>
                    <div class="card-currency">${card.currency}</div>
                </div>
            </div>
        `;
    }

    // Create a section item
    static createSectionItem(section) {
        return `
            <div class="section-item" data-id="${section.id}">
                <div class="section-info">
                    <h5>${section.name}</h5>
                    <span class="section-balance">$${section.initial_balance.toFixed(2)}</span>
                </div>
                <div class="section-actions">
                    <button class="btn btn-sm" onclick="editSection(${section.id})">Edit</button>
                    <button class="btn btn-sm danger-btn" onclick="deleteSection(${section.id})">Delete</button>
                </div>
            </div>
        `;
    }

    // Create an investment position item
    static createPositionItem(position) {
        const profitLoss = position.profit_loss || 0;
        const plClass = profitLoss >= 0 ? 'text-positive' : 'text-negative';
        const plPrefix = profitLoss >= 0 ? '+' : '';
        const assetIcon = position.asset_type === 'stock' ? '📈' : '₿';

        return `
            <div class="position-item" data-id="${position.id}" onclick="showPositionDetails(${position.id})">
                <div class="position-header">
                    <span class="asset-icon">${assetIcon}</span>
                    <div class="position-symbol">
                        <h4>${position.symbol}</h4>
                        <span class="asset-type">${position.asset_type}</span>
                    </div>
                </div>
                <div class="position-details">
                    <div class="position-quantity">${position.current_quantity || 0} units</div>
                    <div class="position-value">$${(position.current_value || 0).toFixed(2)}</div>
                    <div class="position-pl ${plClass}">${plPrefix}$${Math.abs(profitLoss).toFixed(2)}</div>
                </div>
            </div>
        `;
    }

    // Create a movement item
    static createMovementItem(movement) {
        const typeClass = movement.movement_type === 'buy' ? 'text-positive' : 'text-negative';
        const typeIcon = movement.movement_type === 'buy' ? '📈' : '📉';
        const date = new Date(movement.movement_datetime).toLocaleDateString();
        const time = new Date(movement.movement_datetime).toLocaleTimeString();

        return `
            <div class="movement-item" data-id="${movement.id}">
                <div class="movement-info">
                    <div class="movement-header">
                        <span class="movement-icon ${typeClass}">${typeIcon}</span>
                        <div class="movement-details">
                            <span class="movement-type ${typeClass}">${movement.movement_type.toUpperCase()}</span>
                            <span class="movement-symbol">${movement.symbol}</span>
                        </div>
                    </div>
                    <div class="movement-data">
                        <div class="movement-quantity">${movement.quantity} @ $${movement.price_per_unit}</div>
                        <div class="movement-total">$${movement.total_amount}</div>
                        <div class="movement-datetime">${date} ${time}</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Create pagination controls
    static createPagination(currentPage, totalPages, onPageChange) {
        if (totalPages <= 1) return '';

        let pagination = '<div class="pagination">';

        // Previous button
        const prevDisabled = currentPage === 1 ? 'disabled' : '';
        pagination += `
            <button class="pagination-btn ${prevDisabled}" onclick="${onPageChange}(${currentPage - 1})" ${prevDisabled ? 'disabled' : ''}>
                Previous
            </button>
        `;

        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);

        if (startPage > 1) {
            pagination += `<button class="pagination-btn" onclick="${onPageChange}(1)">1</button>`;
            if (startPage > 2) {
                pagination += '<span class="pagination-ellipsis">...</span>';
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === currentPage ? 'active' : '';
            pagination += `
                <button class="pagination-btn ${activeClass}" onclick="${onPageChange}(${i})">
                    ${i}
                </button>
            `;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                pagination += '<span class="pagination-ellipsis">...</span>';
            }
            pagination += `<button class="pagination-btn" onclick="${onPageChange}(${totalPages})">${totalPages}</button>`;
        }

        // Next button
        const nextDisabled = currentPage === totalPages ? 'disabled' : '';
        pagination += `
            <button class="pagination-btn ${nextDisabled}" onclick="${onPageChange}(${currentPage + 1})" ${nextDisabled ? 'disabled' : ''}>
                Next
            </button>
        `;

        pagination += '</div>';
        return pagination;
    }

    // Create a notification/toast
    static createNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">&times;</button>
        `;

        // Add to body
        document.body.appendChild(notification);

        // Auto remove after duration
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);

        return notification;
    }

    // Show/hide modal
    static showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            modal.style.display = 'flex';
        }
    }

    static hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
        }
    }

    // Form validation helpers
    static validateForm(formElement) {
        const formData = new FormData(formElement);
        const errors = [];

        // Check required fields
        const requiredFields = formElement.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                errors.push(`${field.name || field.id} is required`);
                field.classList.add('error');
            } else {
                field.classList.remove('error');
            }
        });

        // Validate email fields
        const emailFields = formElement.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !this.isValidEmail(field.value)) {
                errors.push(`${field.name || field.id} must be a valid email`);
                field.classList.add('error');
            }
        });

        // Validate number fields
        const numberFields = formElement.querySelectorAll('input[type="number"]');
        numberFields.forEach(field => {
            if (field.value && isNaN(field.value)) {
                errors.push(`${field.name || field.id} must be a valid number`);
                field.classList.add('error');
            }
        });

        return { isValid: errors.length === 0, errors };
    }

    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Format currency
    static formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    // Format date
    static formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        return new Date(date).toLocaleDateString('en-US', { ...defaultOptions, ...options });
    }

    // Format relative time
    static formatRelativeTime(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'Just now';
    }

    // Debounce function for search inputs
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
}

// Make UIComponents available globally
if (typeof window !== 'undefined') {
    window.UIComponents = UIComponents;
}

// Export for ES6 modules
try {
    export { UIComponents };
} catch (e) {
    // Fallback for environments without ES6 module support
}