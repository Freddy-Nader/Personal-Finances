# Data Model: Personal Finance Management Application

## Core Entities

### Card
Represents credit or debit cards managed by the user.

**Fields**:
- `id`: INTEGER PRIMARY KEY
- `name`: TEXT NOT NULL (user-defined name for the card)
- `type`: TEXT NOT NULL ('credit' | 'debit')
- `currency`: TEXT NOT NULL DEFAULT 'MXN' (per user requirement)
- `balance`: DECIMAL(15,2) DEFAULT 0.00 (current balance for debit cards)
- `credit_limit`: DECIMAL(15,2) NULL (credit limit for credit cards, NULL for debit)
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

**Validation Rules**:
- `type` must be either 'credit' or 'debit'
- `currency` should support MXN, USD, and other common currencies
- `credit_limit` should only be set for credit cards
- `balance` represents available balance for debit, used balance for credit

### Section
Represents categories/sections within cards (e.g., "emergency", "birthday").

**Fields**:
- `id`: INTEGER PRIMARY KEY
- `card_id`: INTEGER NOT NULL REFERENCES Card(id) ON DELETE CASCADE
- `name`: TEXT NOT NULL (section name like "emergency", "birthday")
- `initial_balance`: DECIMAL(15,2) DEFAULT 0.00 (starting balance for this section)
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

**Validation Rules**:
- `card_id` must reference existing card
- `name` must be unique within the same card
- For credit cards, `initial_balance` inherits from card's credit_limit proportionally

### Transaction
Represents financial movements (income/expense) for cards, cash, or between accounts.

**Fields**:
- `id`: INTEGER PRIMARY KEY
- `amount`: DECIMAL(15,2) NOT NULL
- `description`: TEXT NOT NULL
- `transaction_date`: TIMESTAMP NOT NULL
- `card_id`: INTEGER NULL REFERENCES Card(id) (NULL for cash transactions)
- `section_id`: INTEGER NULL REFERENCES Section(id) (specific section if applicable)
- `category`: TEXT NULL (optional categorization)
- `is_internal_transfer`: BOOLEAN DEFAULT FALSE (user requirement)
- `transfer_from_type`: TEXT NULL ('card', 'cash', 'stock', 'crypto')
- `transfer_from_id`: INTEGER NULL (ID of source account/asset)
- `transfer_to_type`: TEXT NULL ('card', 'cash', 'stock', 'crypto')
- `transfer_to_id`: INTEGER NULL (ID of destination account/asset)
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

**Validation Rules**:
- `amount` can be positive (income) or negative (expense)
- When `is_internal_transfer` is TRUE, both transfer_from and transfer_to fields must be populated
- Internal transfers create paired transactions (debit/credit)
- Either `card_id` or cash transaction must be specified

### Investment Position
Represents asset holdings (stocks or crypto) - simplified to track only basic info.

**Fields**:
- `id`: INTEGER PRIMARY KEY
- `asset_type`: TEXT NOT NULL ('stock' | 'crypto')
- `symbol`: TEXT NOT NULL (stock ticker or crypto symbol)
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

**Validation Rules**:
- `asset_type` must be either 'stock' or 'crypto'
- `symbol` should be valid ticker/symbol
- Current holdings calculated from movements table
- Prices fetched on-demand when displaying portfolio

### Movement
Represents buy/sell transactions for stocks and cryptocurrencies with exact timing.

**Fields**:
- `id`: INTEGER PRIMARY KEY
- `position_id`: INTEGER NOT NULL REFERENCES InvestmentPosition(id)
- `movement_type`: TEXT NOT NULL ('buy' | 'sell')
- `quantity`: DECIMAL(18,8) NOT NULL
- `price_per_unit`: DECIMAL(15,2) NOT NULL (price paid per unit for redundancy)
- `total_amount`: DECIMAL(15,2) NOT NULL (quantity * price_per_unit)
- `movement_datetime`: TIMESTAMP NOT NULL (exact date and time of purchase/sale)
- `description`: TEXT NULL
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

**Validation Rules**:
- `movement_type` must be either 'buy' or 'sell'
- `quantity` must be positive
- `total_amount` should equal quantity * price_per_unit
- `movement_datetime` stores exact purchase/sale time for price verification
- Selling quantity cannot exceed total held quantity (calculated from all movements)

### Card Interest/Fee
Represents interests (positive) and fees (negative) associated with cards with detailed compounding.

**Fields**:
- `id`: INTEGER PRIMARY KEY
- `card_id`: INTEGER NOT NULL REFERENCES Card(id) ON DELETE CASCADE
- `name`: TEXT NOT NULL (description of interest/fee)
- `rate`: DECIMAL(8,4) NOT NULL (interest rate as percentage, e.g., 5.0000 for 5%)
- `is_fee`: BOOLEAN DEFAULT FALSE (TRUE for fees, FALSE for interests)
- `payment_frequency`: TEXT NOT NULL DEFAULT 'annually' ('daily', 'weekly', 'monthly', 'quarterly', 'annually')
- `compound_frequency`: TEXT NOT NULL DEFAULT 'daily_365' ('daily_365', 'daily_360', 'semi_weekly_104', 'weekly_52', 'bi_weekly_26', 'semi_monthly_24', 'monthly_12', 'bi_monthly_6', 'quarterly_4', 'half_yearly_2', 'yearly_1')
- `is_active`: BOOLEAN DEFAULT TRUE
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

**Validation Rules**:
- `card_id` must reference existing card
- `payment_frequency` determines when interest/fee is received/charged
- `compound_frequency` determines how often interest compounds (with frequency per year)
- Default: yearly payment with daily compounding (365 times per year)
- `rate` should be positive; `is_fee` determines if it's added to or subtracted from balance

## Database Schema (SQLite)

```sql
-- Cards table
CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('credit', 'debit')),
    currency TEXT NOT NULL DEFAULT 'MXN',
    balance DECIMAL(15,2) DEFAULT 0.00,
    credit_limit DECIMAL(15,2) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sections table (user requirement)
CREATE TABLE sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    initial_balance DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    UNIQUE(card_id, name)
);

-- Transactions table with internal transfer support
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount DECIMAL(15,2) NOT NULL,
    description TEXT NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    card_id INTEGER NULL,
    section_id INTEGER NULL,
    category TEXT NULL,
    is_internal_transfer BOOLEAN DEFAULT FALSE,
    transfer_from_type TEXT NULL CHECK (transfer_from_type IN ('card', 'cash', 'stock', 'crypto')),
    transfer_from_id INTEGER NULL,
    transfer_to_type TEXT NULL CHECK (transfer_to_type IN ('card', 'cash', 'stock', 'crypto')),
    transfer_to_id INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES cards(id),
    FOREIGN KEY (section_id) REFERENCES sections(id)
);

-- Investment positions (simplified - no stored prices)
CREATE TABLE investment_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_type TEXT NOT NULL CHECK (asset_type IN ('stock', 'crypto')),
    symbol TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asset_type, symbol)
);

-- Investment movements with exact timing and price redundancy
CREATE TABLE movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id INTEGER NOT NULL,
    movement_type TEXT NOT NULL CHECK (movement_type IN ('buy', 'sell')),
    quantity DECIMAL(18,8) NOT NULL,
    price_per_unit DECIMAL(15,2) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    movement_datetime TIMESTAMP NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES investment_positions(id)
);

-- Card interests and fees with detailed compounding
CREATE TABLE card_fees_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    rate DECIMAL(8,4) NOT NULL,
    is_fee BOOLEAN DEFAULT FALSE,
    payment_frequency TEXT NOT NULL DEFAULT 'annually' CHECK (payment_frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'annually')),
    compound_frequency TEXT NOT NULL DEFAULT 'daily_365' CHECK (compound_frequency IN ('daily_365', 'daily_360', 'semi_weekly_104', 'weekly_52', 'bi_weekly_26', 'semi_monthly_24', 'monthly_12', 'bi_monthly_6', 'quarterly_4', 'half_yearly_2', 'yearly_1')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_card ON transactions(card_id);
CREATE INDEX idx_movements_position ON movements(position_id);
CREATE INDEX idx_movements_datetime ON movements(movement_datetime);
CREATE INDEX idx_sections_card ON sections(card_id);
```

## Relationships

- **Card -> Section**: One-to-many (a card can have multiple sections)
- **Card -> Transaction**: One-to-many (a card can have multiple transactions)
- **Section -> Transaction**: One-to-many (a section can have multiple transactions)
- **InvestmentPosition -> Movement**: One-to-many (a position can have multiple buy/sell movements)
- **Card -> CardFeesInterests**: One-to-many (a card can have multiple fees/interests)

## Key Business Rules

1. **Internal Transfers**: When `is_internal_transfer` is TRUE, the system must create paired transactions showing money movement between accounts
2. **Default Currency**: All new cards default to MXN currency as specified
3. **Section Balance**: Sections inherit credit limits from their parent card proportionally
4. **Investment Calculations**:
   - Current holdings calculated by summing all buy movements minus sell movements
   - Current portfolio value fetched on-demand using live/historical price APIs
   - Cost basis calculated from actual purchase prices and dates
5. **Card Types**: Credit cards use credit_limit, debit cards use balance field
6. **Price Fetching**: Prices fetched based on `movement_datetime` for historical accuracy, `price_per_unit` stored as redundancy
7. **Interest/Fee Calculations**:
   - Interest rate stored as percentage (e.g., 5.0000 for 5%)
   - Payment frequency determines when interest/fee is applied to account
   - Compound frequency determines calculation intervals (default: daily compounding, yearly payment)
   - Formula: Final Amount = Principal × (1 + rate/compound_periods)^(compound_periods × time)

## Environment Configuration (.env.example)

```bash
# Database Configuration
DATABASE_PATH=./data/finance.db
DATABASE_BACKUP_PATH=./data/backups/

# Server Configuration
SERVER_PORT=8000
SERVER_HOST=localhost
DEBUG_MODE=true

# Application Settings
DEFAULT_CURRENCY=MXN
SUPPORTED_CURRENCIES=MXN,USD,EUR,CAD

# Performance Settings
MAX_TRANSACTIONS_PER_PAGE=100
CHART_DATA_MAX_POINTS=1000

# Development Settings
AUTO_RELOAD=true
LOG_LEVEL=INFO
LOG_FILE=./logs/finance-app.log

# Testing Configuration
TEST_DATABASE_PATH=./test_data/test_finance.db
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000

# Security Settings (for local app)
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Price API Configuration (optional - for fetching current/historical prices)
ENABLE_STOCK_PRICES=false
ENABLE_CRYPTO_PRICES=false
STOCK_API_KEY=your_api_key_here
CRYPTO_API_KEY=your_api_key_here

# Feature Flags
ENABLE_ANALYTICS_EXPORT=true
ENABLE_PRICE_ALERTS=false

# Interest Calculation Settings
DEFAULT_COMPOUND_FREQUENCY=daily_365
DEFAULT_PAYMENT_FREQUENCY=annually
```