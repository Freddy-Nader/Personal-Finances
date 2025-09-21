# Claude Code Context: Personal Finance Management Application

## Project Overview
Personal Finance Management Application - A local, single-user web application for tracking finances including cards, transactions, and investments. Built with minimal framework approach using Python backend and vanilla HTML/CSS/JavaScript frontend.

## Current Implementation Status
- **Phase**: Design complete, ready for implementation
- **Branch**: `001-build-an-application`
- **Structure**: Web application (frontend + backend)

## Technology Stack
- **Backend**: Python 3.11+ with standard library (http.server, sqlite3)
- **Frontend**: Vanilla HTML, CSS (Notion-inspired), JavaScript
- **Database**: SQLite (local file)
- **Testing**: Playwright MCP (required), Python unittest
- **Charts**: Chart.js (minimal framework exception for financial visualization)

## Key Constitutional Requirements
1. **Minimal Framework Dependency**: Avoid frameworks unless absolutely necessary
2. **Testing Standards**: 80%+ coverage, Playwright MCP required
3. **Performance**: <3s page loads, <100ms interactions, <500KB bundles
4. **UX Consistency**: Notion-inspired design from `docs/notion-reference.md`
5. **Code Quality**: Pure functions, clear naming, financial logic documentation

## Project Structure
```
Personal-Finances/
├── backend/
│   ├── src/
│   │   ├── models/          # Data models and database operations
│   │   ├── services/        # Business logic services
│   │   ├── api/            # API handlers and routing
│   │   └── database/       # Database initialization and schema
│   └── tests/
├── frontend/
│   ├── pages/              # HTML pages (dashboard, transactions, manage, movements)
│   ├── css/               # Styling (notion-base.css, finance-app.css)
│   ├── js/                # JavaScript modules (api.js, components.js, utils.js)
│   └── assets/
├── tests/
│   ├── contract/          # API contract tests
│   ├── integration/       # Integration tests
│   └── frontend/          # Playwright end-to-end tests
├── specs/001-build-an-application/  # Current feature specification
└── docs/notion-reference.md         # UI design reference
```

## Database Schema (Key Tables)
- **cards**: Credit/debit cards with MXN default currency
- **sections**: Card categories (emergency, birthday, etc.)
- **transactions**: Financial movements with internal transfer support
- **investment_positions**: Stock/crypto holdings (prices fetched on-demand)
- **movements**: Buy/sell transactions with exact timestamps
- **card_fees_interests**: Interest rates with compound frequency options

## API Design Patterns
- RESTful endpoints under `/api/*`
- JSON request/response format
- Standard HTTP status codes
- Pagination for large datasets
- Time-based filtering support

## Key Business Rules
1. **Default Currency**: MXN for all new cards
2. **Internal Transfers**: Paired transactions (debit/credit) when `is_internal_transfer=true`
3. **Investment Pricing**: Fetch on-demand, store purchase prices for redundancy
4. **Interest Calculations**: Configurable payment frequency + compound frequency
5. **Section Inheritance**: Sections inherit card credit limits proportionally

## Recent Changes
- Updated schema with detailed compound frequency options
- Added internal transfer support to transactions
- Separated investment price storage (on-demand fetching)
- Enhanced interest/fee model with payment + compound frequencies

## Development Guidelines
- Use relative paths in all file references
- Virtual environment: `.venv`
- Follow Notion CSS patterns from `docs/notion-reference.md`
- Implement TDD: tests before implementation
- Keep bundle sizes minimal, avoid unnecessary dependencies
- Financial calculations must be pure, documented functions

## Testing Requirements
- Unit tests for all business logic
- Contract tests for API endpoints
- Integration tests for database operations
- End-to-end tests with Playwright MCP
- Performance tests for constitutional compliance

## Environment Configuration
Key `.env` variables:
- `DATABASE_PATH=./data/finance.db`
- `SERVER_PORT=8000`
- `DEFAULT_CURRENCY=MXN`
- `DEBUG_MODE=true`

## Next Phase: Implementation
Ready to execute task generation and begin TDD implementation following constitutional principles.