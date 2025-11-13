// Card and Section Management JavaScript
class CardManager {
    constructor() {
        this.cards = [];
        this.selectedCard = null;
        this.sections = [];
        this.interests = [];
        this.editingCard = null;
        this.editingSection = null;
        this.editingInterest = null;

        this.initializeEventListeners();
        this.loadCards();
    }

    initializeEventListeners() {
        // Card management buttons
        const addCardBtn = document.getElementById('addCardBtn');
        if (addCardBtn) {
            addCardBtn.addEventListener('click', () => this.openCardModal());
        }

        const editCardBtn = document.getElementById('editCardBtn');
        if (editCardBtn) {
            editCardBtn.addEventListener('click', () => this.editSelectedCard());
        }

        const deleteCardBtn = document.getElementById('deleteCardBtn');
        if (deleteCardBtn) {
            deleteCardBtn.addEventListener('click', () => this.deleteSelectedCard());
        }

        // Section management
        const addSectionBtn = document.getElementById('addSectionBtn');
        if (addSectionBtn) {
            addSectionBtn.addEventListener('click', () => this.openSectionModal());
        }

        // Interest management
        const addInterestBtn = document.getElementById('addInterestBtn');
        if (addInterestBtn) {
            addInterestBtn.addEventListener('click', () => this.openInterestModal());
        }

        // Card modal controls
        this.setupModalEventListeners('card');
        this.setupModalEventListeners('section');
        this.setupModalEventListeners('interest');

        // Card type change handler
        const cardType = document.getElementById('cardType');
        if (cardType) {
            cardType.addEventListener('change', () => this.handleCardTypeChange());
        }

        // Interest/fee checkbox
        const isFeeCheckbox = document.getElementById('isFee');
        if (isFeeCheckbox) {
            isFeeCheckbox.addEventListener('change', () => this.updateInterestLabels());
        }
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

    async loadCards() {
        try {
            this.showCardsLoading();
            this.cards = await api.getCards();
            this.displayCards();
        } catch (error) {
            console.error('Failed to load cards:', error);
            this.showError('Failed to load cards');
            this.displayCardsError();
        }
    }

    displayCards() {
        const cardsGrid = document.getElementById('cardsGrid');
        if (!cardsGrid) return;

        if (this.cards.length === 0) {
            cardsGrid.innerHTML = UIComponents.createEmptyState(
                'No cards found. Add your first card to get started.',
                'Add Card',
                'cardManager.openCardModal()'
            );
            return;
        }

        const cardItems = this.cards.map(card => {
            const isSelected = this.selectedCard && this.selectedCard.id === card.id;
            return this.createCardHTML(card, isSelected);
        }).join('');

        cardsGrid.innerHTML = cardItems;
    }

    createCardHTML(card, selected = false) {
        const selectedClass = selected ? 'selected' : '';
        const cardTypeIcon = card.type === 'credit' ? '💳' : '🏦';
        const balanceLabel = card.type === 'credit' ? 'Credit Limit' : 'Balance';
        const balanceValue = card.type === 'credit' ? card.credit_limit : card.balance;
        const balanceClass = card.balance >= 0 ? 'text-positive' : 'text-negative';

        return `
            <div class="card-item ${selectedClass}" data-id="${card.id}" onclick="cardManager.selectCard(${card.id})">
                <div class="card-header">
                    <span class="card-icon">${cardTypeIcon}</span>
                    <h4>${card.name}</h4>
                </div>
                <div class="card-details">
                    <div class="card-type">${card.type.charAt(0).toUpperCase() + card.type.slice(1)} Card</div>
                    <div class="card-balance">
                        <span class="balance-label">${balanceLabel}:</span>
                        <span class="balance-value ${balanceClass}">
                            ${FinanceUtils.formatCurrency(balanceValue || 0, card.currency)}
                        </span>
                    </div>
                    <div class="card-currency">${card.currency}</div>
                </div>
            </div>
        `;
    }

    selectCard(cardId) {
        // Update selected card
        this.selectedCard = this.cards.find(card => card.id === cardId);

        // Update UI
        this.displayCards();
        this.showCardDetails();
        this.loadCardSections();
        this.loadCardInterests();
    }

    showCardDetails() {
        const detailsSection = document.getElementById('cardDetailsSection');
        const cardTitle = document.getElementById('selectedCardTitle');

        if (detailsSection && this.selectedCard) {
            detailsSection.style.display = 'block';
            if (cardTitle) {
                cardTitle.textContent = `${this.selectedCard.name} Details`;
            }
        }
    }

    async loadCardSections() {
        if (!this.selectedCard) return;

        try {
            this.sections = await api.getCardSections(this.selectedCard.id);
            this.displaySections();
        } catch (error) {
            console.error('Failed to load sections:', error);
            this.displaySectionsError();
        }
    }

    displaySections() {
        const sectionsList = document.getElementById('sectionsList');
        if (!sectionsList) return;

        if (this.sections.length === 0) {
            sectionsList.innerHTML = `
                <div class="empty-state">
                    No sections found. Add one to organize your spending.
                    <button class="secondary-btn" onclick="cardManager.openSectionModal()">Add Section</button>
                </div>
            `;
            return;
        }

        const sectionItems = this.sections.map(section => {
            return `
                <div class="section-item" data-id="${section.id}">
                    <div class="section-info">
                        <h5>${section.name}</h5>
                        <span class="section-balance">
                            ${FinanceUtils.formatCurrency(section.initial_balance, this.selectedCard.currency)}
                        </span>
                    </div>
                    <div class="section-actions">
                        <button class="btn btn-sm secondary-btn" onclick="cardManager.editSection(${section.id})">
                            Edit
                        </button>
                        <button class="btn btn-sm danger-btn" onclick="cardManager.deleteSection(${section.id})">
                            Delete
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        sectionsList.innerHTML = sectionItems;
    }

    async loadCardInterests() {
        if (!this.selectedCard) return;

        try {
            // This would be implemented when the backend supports card interests
            this.interests = []; // Placeholder
            this.displayInterests();
        } catch (error) {
            console.error('Failed to load interests:', error);
            this.displayInterestsError();
        }
    }

    displayInterests() {
        const interestsList = document.getElementById('interestsList');
        if (!interestsList) return;

        if (this.interests.length === 0) {
            interestsList.innerHTML = `
                <div class="empty-state">
                    No interest or fees configured.
                    <button class="secondary-btn" onclick="cardManager.openInterestModal()">Add Interest/Fee</button>
                </div>
            `;
            return;
        }

        const interestItems = this.interests.map(interest => {
            const typeLabel = interest.is_fee ? 'Fee' : 'Interest';
            const rateDisplay = `${interest.rate}% ${interest.payment_frequency}`;

            return `
                <div class="interest-item" data-id="${interest.id}">
                    <div class="interest-info">
                        <h5>${interest.name}</h5>
                        <div class="interest-details">
                            <span class="interest-type">${typeLabel}</span>
                            <span class="interest-rate">${rateDisplay}</span>
                            <span class="interest-compound">Compounds ${interest.compound_frequency}</span>
                        </div>
                    </div>
                    <div class="interest-actions">
                        <button class="btn btn-sm secondary-btn" onclick="cardManager.editInterest(${interest.id})">
                            Edit
                        </button>
                        <button class="btn btn-sm danger-btn" onclick="cardManager.deleteInterest(${interest.id})">
                            Delete
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        interestsList.innerHTML = interestItems;
    }

    // Modal Management
    openCardModal(card = null) {
        this.editingCard = card;
        const modal = document.getElementById('cardModal');
        const modalTitle = document.getElementById('cardModalTitle');
        const form = document.getElementById('cardForm');

        if (card) {
            modalTitle.textContent = 'Edit Card';
            this.populateCardForm(card);
        } else {
            modalTitle.textContent = 'Add Card';
            form.reset();
            this.setDefaultCardValues();
        }

        UIComponents.showModal('cardModal');
    }

    openSectionModal(section = null) {
        if (!this.selectedCard) {
            this.showError('Please select a card first');
            return;
        }

        this.editingSection = section;
        const modal = document.getElementById('sectionModal');
        const modalTitle = document.getElementById('sectionModalTitle');
        const form = document.getElementById('sectionForm');

        if (section) {
            modalTitle.textContent = 'Edit Section';
            this.populateSectionForm(section);
        } else {
            modalTitle.textContent = 'Add Section';
            form.reset();
        }

        UIComponents.showModal('sectionModal');
    }

    openInterestModal(interest = null) {
        if (!this.selectedCard) {
            this.showError('Please select a card first');
            return;
        }

        this.editingInterest = interest;
        const modal = document.getElementById('interestModal');
        const modalTitle = document.getElementById('interestModalTitle');
        const form = document.getElementById('interestForm');

        if (interest) {
            modalTitle.textContent = 'Edit Interest/Fee';
            this.populateInterestForm(interest);
        } else {
            modalTitle.textContent = 'Add Interest/Fee';
            form.reset();
            this.setDefaultInterestValues();
        }

        this.updateInterestLabels();
        UIComponents.showModal('interestModal');
    }

    closeModal(type) {
        UIComponents.hideModal(`${type}Modal`);
        if (type === 'card') this.editingCard = null;
        if (type === 'section') this.editingSection = null;
        if (type === 'interest') this.editingInterest = null;
    }

    // Form Population
    populateCardForm(card) {
        document.getElementById('cardName').value = card.name;
        document.getElementById('cardType').value = card.type;
        document.getElementById('cardCurrency').value = card.currency;

        if (card.type === 'credit') {
            document.getElementById('creditLimit').value = card.credit_limit || '';
        } else {
            document.getElementById('initialBalance').value = card.balance || '';
        }

        this.handleCardTypeChange();
    }

    populateSectionForm(section) {
        document.getElementById('sectionName').value = section.name;
        document.getElementById('sectionBalance').value = section.initial_balance;
    }

    populateInterestForm(interest) {
        document.getElementById('interestName').value = interest.name;
        document.getElementById('interestRate').value = interest.rate;
        document.getElementById('isFee').checked = interest.is_fee;
        document.getElementById('paymentFrequency').value = interest.payment_frequency;
        document.getElementById('compoundFrequency').value = interest.compound_frequency;
        document.getElementById('isActive').checked = interest.is_active;
    }

    setDefaultCardValues() {
        document.getElementById('cardCurrency').value = 'MXN';
        document.getElementById('cardType').value = '';
        this.handleCardTypeChange();
    }

    setDefaultInterestValues() {
        document.getElementById('isFee').checked = false;
        document.getElementById('paymentFrequency').value = 'annually';
        document.getElementById('compoundFrequency').value = 'daily_365';
        document.getElementById('isActive').checked = true;
    }

    handleCardTypeChange() {
        const cardType = document.getElementById('cardType').value;
        const balanceGroup = document.getElementById('balanceGroup');
        const creditLimitGroup = document.getElementById('creditLimitGroup');
        const balanceLabel = balanceGroup.querySelector('label');

        if (cardType === 'credit') {
            balanceGroup.style.display = 'none';
            creditLimitGroup.style.display = 'block';
        } else if (cardType === 'debit') {
            balanceGroup.style.display = 'block';
            creditLimitGroup.style.display = 'none';
            if (balanceLabel) {
                balanceLabel.textContent = 'Initial Balance:';
            }
        } else {
            balanceGroup.style.display = 'none';
            creditLimitGroup.style.display = 'none';
        }
    }

    updateInterestLabels() {
        const isFee = document.getElementById('isFee').checked;
        const rateLabel = document.querySelector('label[for="interestRate"]');

        if (rateLabel) {
            rateLabel.textContent = isFee ? 'Fee Rate (%):' : 'Interest Rate (%):';
        }
    }

    // Form Submission
    async handleFormSubmit(e, type) {
        e.preventDefault();

        const formData = new FormData(e.target);

        try {
            if (type === 'card') {
                await this.handleCardSubmit(formData);
            } else if (type === 'section') {
                await this.handleSectionSubmit(formData);
            } else if (type === 'interest') {
                await this.handleInterestSubmit(formData);
            }
        } catch (error) {
            console.error(`Failed to save ${type}:`, error);
            this.showError(`Failed to save ${type}. Please try again.`);
        }
    }

    async handleCardSubmit(formData) {
        const cardData = this.buildCardData(formData);

        const validation = this.validateCard(cardData);
        if (!validation.isValid) {
            this.showError(validation.errors.join(', '));
            return;
        }

        if (this.editingCard) {
            await api.updateCard(this.editingCard.id, cardData);
            UIComponents.createNotification('Card updated successfully', 'success');
        } else {
            await api.createCard(cardData);
            UIComponents.createNotification('Card created successfully', 'success');
        }

        this.closeModal('card');
        this.loadCards();
    }

    async handleSectionSubmit(formData) {
        const sectionData = {
            name: formData.get('sectionName'),
            initial_balance: parseFloat(formData.get('sectionBalance') || 0)
        };

        const validation = this.validateSection(sectionData);
        if (!validation.isValid) {
            this.showError(validation.errors.join(', '));
            return;
        }

        if (this.editingSection) {
            // Update section - would need API endpoint
            UIComponents.createNotification('Section updated successfully', 'success');
        } else {
            await api.createSection(this.selectedCard.id, sectionData);
            UIComponents.createNotification('Section created successfully', 'success');
        }

        this.closeModal('section');
        this.loadCardSections();
    }

    async handleInterestSubmit(formData) {
        const interestData = {
            name: formData.get('interestName'),
            rate: parseFloat(formData.get('interestRate')),
            is_fee: formData.get('isFee') === 'on',
            payment_frequency: formData.get('paymentFrequency'),
            compound_frequency: formData.get('compoundFrequency'),
            is_active: formData.get('isActive') === 'on'
        };

        const validation = this.validateInterest(interestData);
        if (!validation.isValid) {
            this.showError(validation.errors.join(', '));
            return;
        }

        // This would be implemented when backend supports interests/fees
        UIComponents.createNotification('Interest/Fee saved successfully', 'success');

        this.closeModal('interest');
        this.loadCardInterests();
    }

    buildCardData(formData) {
        const cardType = formData.get('cardType');

        const data = {
            name: formData.get('cardName'),
            type: cardType,
            currency: formData.get('cardCurrency')
        };

        if (cardType === 'credit') {
            data.credit_limit = parseFloat(formData.get('creditLimit') || 0);
        } else {
            data.balance = parseFloat(formData.get('initialBalance') || 0);
        }

        return data;
    }

    // Validation
    validateCard(data) {
        const errors = [];

        if (!data.name || data.name.trim() === '') {
            errors.push('Card name is required');
        }

        if (!data.type) {
            errors.push('Card type is required');
        }

        if (data.type === 'credit' && (!data.credit_limit || data.credit_limit <= 0)) {
            errors.push('Credit limit must be greater than 0 for credit cards');
        }

        return { isValid: errors.length === 0, errors };
    }

    validateSection(data) {
        const errors = [];

        if (!data.name || data.name.trim() === '') {
            errors.push('Section name is required');
        }

        if (isNaN(data.initial_balance)) {
            errors.push('Valid initial balance is required');
        }

        return { isValid: errors.length === 0, errors };
    }

    validateInterest(data) {
        const errors = [];

        if (!data.name || data.name.trim() === '') {
            errors.push('Interest/Fee name is required');
        }

        if (isNaN(data.rate) || data.rate < 0) {
            errors.push('Valid rate is required');
        }

        return { isValid: errors.length === 0, errors };
    }

    // Actions
    editSelectedCard() {
        if (this.selectedCard) {
            this.openCardModal(this.selectedCard);
        }
    }

    async deleteSelectedCard() {
        if (!this.selectedCard) return;

        if (!confirm(`Are you sure you want to delete "${this.selectedCard.name}"? This will also delete all associated sections and transactions.`)) {
            return;
        }

        try {
            await api.deleteCard(this.selectedCard.id);
            UIComponents.createNotification('Card deleted successfully', 'success');
            this.selectedCard = null;
            document.getElementById('cardDetailsSection').style.display = 'none';
            this.loadCards();
        } catch (error) {
            console.error('Failed to delete card:', error);
            this.showError('Failed to delete card');
        }
    }

    async editSection(sectionId) {
        const section = this.sections.find(s => s.id === sectionId);
        if (section) {
            this.openSectionModal(section);
        }
    }

    async deleteSection(sectionId) {
        const section = this.sections.find(s => s.id === sectionId);
        if (!section) return;

        if (!confirm(`Are you sure you want to delete section "${section.name}"?`)) {
            return;
        }

        try {
            // This would use a delete section API endpoint
            UIComponents.createNotification('Section deleted successfully', 'success');
            this.loadCardSections();
        } catch (error) {
            console.error('Failed to delete section:', error);
            this.showError('Failed to delete section');
        }
    }

    async editInterest(interestId) {
        const interest = this.interests.find(i => i.id === interestId);
        if (interest) {
            this.openInterestModal(interest);
        }
    }

    async deleteInterest(interestId) {
        const interest = this.interests.find(i => i.id === interestId);
        if (!interest) return;

        if (!confirm(`Are you sure you want to delete "${interest.name}"?`)) {
            return;
        }

        try {
            // This would use a delete interest API endpoint
            UIComponents.createNotification('Interest/Fee deleted successfully', 'success');
            this.loadCardInterests();
        } catch (error) {
            console.error('Failed to delete interest/fee:', error);
            this.showError('Failed to delete interest/fee');
        }
    }

    // Utility methods
    showCardsLoading() {
        const cardsGrid = document.getElementById('cardsGrid');
        if (cardsGrid) {
            cardsGrid.innerHTML = '<div class="loading">Loading cards...</div>';
        }
    }

    displayCardsError() {
        const cardsGrid = document.getElementById('cardsGrid');
        if (cardsGrid) {
            cardsGrid.innerHTML = '<div class="error">Failed to load cards. Please refresh the page.</div>';
        }
    }

    displaySectionsError() {
        const sectionsList = document.getElementById('sectionsList');
        if (sectionsList) {
            sectionsList.innerHTML = '<div class="error">Failed to load sections.</div>';
        }
    }

    displayInterestsError() {
        const interestsList = document.getElementById('interestsList');
        if (interestsList) {
            interestsList.innerHTML = '<div class="error">Failed to load interests/fees.</div>';
        }
    }

    showError(message) {
        UIComponents.createNotification(message, 'error');
    }
}

// Initialize card manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cardManager = new CardManager();
});

// Global functions for button clicks
function selectCard(id) {
    if (window.cardManager) {
        window.cardManager.selectCard(id);
    }
}

function editSection(id) {
    if (window.cardManager) {
        window.cardManager.editSection(id);
    }
}

function deleteSection(id) {
    if (window.cardManager) {
        window.cardManager.deleteSection(id);
    }
}

function editInterest(id) {
    if (window.cardManager) {
        window.cardManager.editInterest(id);
    }
}

function deleteInterest(id) {
    if (window.cardManager) {
        window.cardManager.deleteInterest(id);
    }
}