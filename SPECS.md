# Personal Finance Tracker - Technical Specifications

## Project Overview
A minimalistic web-based personal finance application built with vanilla HTML, CSS, and JavaScript for tracking cash, card, stock, and cryptocurrency movements.

## File Structure
```
/finances/
├── index.html          # Main application interface
├── styles.css          # Minimalistic styling
├── app.js              # Core application logic
├── database.js         # Local storage database management
├── SPECS.md            # This file
└── README.md           # Project documentation
```

## Data Models

### 1. Transaction Types

#### Cash/Card Transactions
- `id`: Unique identifier (timestamp-based)
- `date`: Transaction date (YYYY-MM-DD format)
- `medium`: Card name or "Cash"
- `amount`: Positive for income, negative for expenses
- `description`: Transaction description
- `isTransfer`: Boolean - true if inter-bank transfer
- `type`: "cash" or "card"

#### Stock Transactions
- `id`: Unique identifier (timestamp-based)
- `date`: Transaction date (YYYY-MM-DD format)
- `symbol`: Stock symbol (e.g., "AAPL", "TSLA")
- `quantity`: Number of shares
- `price`: Price per share
- `type`: "buy" or "sell"
- `fees`: Transaction fees
- `totalValue`: Calculated total (quantity * price + fees)

#### Crypto Transactions
- `id`: Unique identifier (timestamp-based)
- `date`: Transaction date (YYYY-MM-DD format)
- `coin`: Cryptocurrency symbol (e.g., "BTC", "ETH")
- `quantity`: Amount of crypto
- `price`: Price in USD
- `type`: "buy" or "sell"
- `fees`: Transaction fees
- `totalValue`: Calculated total (quantity * price + fees)

### 2. Configuration Data
- `cards`: Array of card names for dropdown selection
- `cryptoCoins`: Array of commonly used crypto symbols
- `stockSymbols`: Array of commonly used stock symbols

## User Interface Components

### 1. Dashboard Section
- Summary cards showing:
  - Total balance (cash + cards)
  - Stock portfolio value
  - Crypto portfolio value
  - Net worth
- Date range filter controls
- Transaction type filter buttons

### 2. Transaction List
- Filterable table showing all transactions
- Sortable by date, amount, type
- Edit/delete actions for each transaction

### 3. Add Transaction Forms
- Tabbed interface for different transaction types
- Form validation for required fields
- Auto-calculation for totals

### 4. Management Section
- Add/remove cards interface
- Add/remove stock symbols
- Add/remove crypto coins
- Data export/import functionality

## Technical Implementation

### 1. Data Storage
- Uses browser's localStorage API
- Data stored as JSON strings
- Key structure:
  - `finance_transactions`: All transactions array
  - `finance_config`: Configuration settings
  - `finance_cards`: User's cards list

### 2. JavaScript Architecture
- **database.js**: CRUD operations, data validation
  - `saveTransaction(transaction)`
  - `getTransactions(filters)`
  - `updateTransaction(id, updates)`
  - `deleteTransaction(id)`
  - `getConfig()`
  - `updateConfig(config)`

- **app.js**: UI logic, event handlers
  - `initializeApp()`
  - `renderDashboard()`
  - `renderTransactionList(filters)`
  - `handleFormSubmit()`
  - `applyFilters()`
  - `exportData()`
  - `importData()`

### 3. CSS Design Principles
- Mobile-first responsive design
- CSS Grid for layout structure
- Flexbox for component alignment
- CSS variables for color theme
- Minimal color palette (3-4 colors max)
- Clean typography with system fonts

## Features Specification

### Core Features
1. **Transaction Management**
   - Add transactions for all types
   - Edit existing transactions
   - Delete transactions with confirmation
   - Bulk operations support

2. **Filtering & Search**
   - Date range filtering
   - Transaction type filtering
   - Text search in descriptions
   - Amount range filtering

3. **Dashboard Analytics**
   - Real-time balance calculations
   - Monthly/yearly summaries
   - Category breakdown
   - Portfolio performance tracking

4. **Data Management**
   - Local data persistence
   - Export to JSON/CSV
   - Import from JSON
   - Data validation and error handling

### User Experience
- Single-page application (no page reloads)
- Modal dialogs for forms
- Toast notifications for actions
- Keyboard navigation support
- Responsive design for mobile/desktop

## Security & Data Handling

### Data Validation
- Input sanitization for all form fields
- Number validation for amounts and quantities
- Date validation and formatting
- Symbol format validation for stocks/crypto

### Error Handling
- Graceful handling of localStorage limitations
- User-friendly error messages
- Data recovery mechanisms
- Input validation feedback

## Browser Compatibility
- Modern browsers supporting ES6+
- localStorage API required
- CSS Grid and Flexbox support
- No external dependencies

## Performance Considerations
- Lazy loading for large transaction lists
- Debounced search and filter inputs
- Efficient data structures for calculations
- Minimal DOM manipulation

## Future Enhancements
- Data backup to cloud storage
- Advanced charting capabilities
- Budget tracking features
- Investment performance analytics
- Multi-currency support