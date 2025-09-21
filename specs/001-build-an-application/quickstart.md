# Quickstart Guide: Personal Finance Management Application

## Overview
This guide walks through setting up and testing the complete Personal Finance Management Application, validating all core user stories from the feature specification.

## Prerequisites
- Python 3.11+
- Modern web browser
- Command line access

## Setup Instructions

### 1. Environment Setup
```bash
# Navigate to project root
cd Personal-Finances

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (minimal approach)
# No external dependencies required for core functionality

# Copy environment configuration
cp .env.example .env
```

### 2. Database Initialization
```bash
# Initialize SQLite database
python backend/src/database/init_db.py
```

### 3. Start the Application
```bash
# Start backend server
python backend/src/server.py

# Server will start on http://localhost:8000
# Frontend files served from frontend/ directory
```

## Core User Story Validation

### Story 1: Dashboard Analytics
**Given** a user has multiple financial accounts
**When** they access the dashboard
**Then** they see consolidated statistics, graphs, and metrics

#### Test Steps:
1. Navigate to `http://localhost:8000/`
2. Verify dashboard loads with placeholder data
3. Check that the following sections are visible:
   - Total balance summary
   - Recent transactions widget
   - Investment portfolio overview
   - Period-based profit/loss metrics
4. Test time period filters (week, month, quarter, year)
5. Verify charts render correctly (balance trends, spending categories)

#### Expected Results:
- Dashboard loads within 3 seconds (constitutional requirement)
- All interactive elements respond within 100ms
- Charts display financial data appropriately
- Time period filtering updates data correctly

### Story 2: Transaction Management
**Given** a user wants to record a purchase
**When** they access the transactions tab
**Then** they can add new transactions for cards or cash

#### Test Steps:
1. Navigate to `/transactions.html`
2. Click "Add New Transaction" button
3. Fill out transaction form:
   - Amount: -50.00 (expense)
   - Description: "Grocery shopping"
   - Date: Today's date
   - Card: Select existing card
   - Category: "Food"
4. Submit transaction
5. Verify transaction appears in transaction list
6. Test internal transfer functionality:
   - Create transfer from Card A to Card B
   - Verify paired transactions created
   - Check balances updated correctly

#### Expected Results:
- Transaction form validates input correctly
- New transactions save and display immediately
- Internal transfers create proper debit/credit pairs
- Transaction list pagination works for large datasets

### Story 3: Card Management
**Given** a user has credit and debit cards
**When** they access the manage tab
**Then** they can add/modify cards, sections, and interests/fees

#### Test Steps:
1. Navigate to `/manage.html`
2. Test card creation:
   - Click "Add New Card"
   - Name: "Main Checking"
   - Type: Debit
   - Currency: MXN (default)
   - Initial Balance: 1000.00
   - Submit form
3. Test section creation:
   - Select created card
   - Add section: "Emergency Fund"
   - Set initial balance: 500.00
   - Submit section
4. Test interest/fee setup:
   - Add interest: 2.5% annual, compounded daily
   - Add fee: $10 monthly maintenance
   - Verify calculation previews

#### Expected Results:
- Cards save with correct default currency (MXN)
- Sections properly associate with parent cards
- Interest/fee calculations display correctly
- Edit functionality works for all fields

### Story 4: Investment Tracking
**Given** a user invests in stocks or crypto
**When** they access the movements tab
**Then** they can record investments and track portfolio

#### Test Steps:
1. Navigate to `/movements.html`
2. Create new investment position:
   - Asset type: Stock
   - Symbol: AAPL
   - Submit position
3. Add buy movement:
   - Quantity: 10 shares
   - Price per unit: $150.00
   - Date/time: Specific timestamp
   - Description: "Initial investment"
4. Test portfolio calculations:
   - Verify current holdings calculation
   - Check cost basis calculation
   - Test profit/loss display (mock current prices)

#### Expected Results:
- Investment positions save correctly
- Movement history tracks exact purchase times
- Portfolio calculations accurate
- Price fetching placeholder works

### Story 5: Time-based Analytics
**Given** a user has recorded transactions over time
**When** they view dashboard analytics
**Then** they can see profit/loss trends by time periods

#### Test Steps:
1. Create sample data spanning multiple months
2. Navigate to dashboard
3. Test time period filters:
   - Weekly view: Last 4 weeks
   - Monthly view: Last 6 months
   - Quarterly view: Last 4 quarters
   - Yearly view: Last 3 years
4. Verify chart data updates correctly
5. Test profit/loss calculations for each period

#### Expected Results:
- Time filtering works correctly
- Charts update smoothly without full page reload
- Profit/loss calculations accurate for all periods
- Performance remains under 100ms for filter changes

## Integration Testing

### Database Operations
```bash
# Run database integration tests
python tests/integration/test_database.py
```

### API Contract Testing
```bash
# Test all API endpoints match contracts
python tests/contract/test_api_contracts.py
```

### End-to-End Testing (Playwright)
```bash
# Run full user workflow tests
playwright test tests/frontend/
```

## Performance Validation

### Constitutional Requirements Check
- [ ] Page load times < 3 seconds
- [ ] Interactive response < 100ms
- [ ] Bundle size < 500KB
- [ ] Memory usage < 100MB

### Load Testing
```bash
# Test with large datasets
python tests/performance/test_large_dataset.py
```

## Troubleshooting

### Common Issues
1. **Database not found**: Run `python backend/src/database/init_db.py`
2. **Port already in use**: Change SERVER_PORT in .env file
3. **Charts not loading**: Verify Chart.js is accessible
4. **Slow performance**: Check browser dev tools for bottlenecks

### Debug Mode
```bash
# Enable debug logging
export DEBUG_MODE=true
python backend/src/server.py
```

## Success Criteria
✅ All user stories validated
✅ All API contracts tested
✅ Constitutional requirements met
✅ Integration tests pass
✅ End-to-end workflows complete
✅ Performance benchmarks achieved

## Next Steps
1. Run automated test suite: `python -m pytest`
2. Performance profiling: Monitor real usage patterns
3. Security review: Input validation and local app security
4. User acceptance: Validate with real financial data

This quickstart validates that the application meets all functional requirements while adhering to constitutional principles of minimal framework usage, testing standards, and performance requirements.