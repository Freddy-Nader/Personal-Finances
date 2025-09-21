# Research Phase: Personal Finance Management Application

## Backend Framework Decision

### Decision: Python http.server + custom routing
**Rationale**:
- Minimal external dependencies (constitutional requirement)
- Python standard library sufficient for local application
- Simple HTTP server with custom request router
- JSON handling with standard library `json` module

**Alternatives considered**:
- FastAPI: Rejected - unnecessary framework dependency for local app
- Flask: Rejected - framework dependency, overkill for simple API
- Django: Rejected - massive framework for simple requirements
- wsgiref: Considered but http.server simpler for local use

### Implementation Pattern:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
from urllib.parse import urlparse, parse_qs

class FinanceAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Route handling logic
    def do_POST(self):
        # Route handling logic
```

## Database Integration

### Decision: sqlite3 standard library
**Rationale**:
- Python standard library module
- Perfect for single-user local application
- No additional database server needed
- Built-in transaction support

**Pattern**:
```python
import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="finance.db"):
        self.db_path = db_path
        self.init_database()
```

## Frontend Architecture

### Decision: Vanilla HTML/CSS/JavaScript with modular structure
**Rationale**:
- Constitutional requirement to avoid frameworks
- Notion-inspired styling from existing reference
- Multiple pages as separate HTML files
- Shared CSS and JavaScript modules

**Structure**:
```
frontend/
├── pages/
│   ├── dashboard.html
│   ├── transactions.html
│   ├── manage.html
│   └── movements.html
├── css/
│   ├── notion-base.css (from reference)
│   └── finance-app.css
├── js/
│   ├── api.js (fetch wrapper)
│   ├── components.js (reusable UI)
│   └── utils.js
└── assets/
```

## Routing and Static File Serving

### Decision: Custom router with static file fallback
**Rationale**:
- API routes: `/api/*` -> handler methods
- Static files: everything else -> serve from frontend/
- Simple URL parsing with standard library

**Pattern**:
```python
def route_request(self, path, method):
    if path.startswith('/api/'):
        return self.handle_api_request(path, method)
    else:
        return self.serve_static_file(path)
```

## Chart and Graph Generation

### Decision: Chart.js (minimal framework exception)
**Rationale**:
- Financial dashboard requires data visualization
- Pure CSS/Canvas charts would be complex to implement
- Chart.js is lightweight and well-established
- Constitutional exception: "unless application cannot run without them"

**Alternatives considered**:
- D3.js: Too heavy, complex for simple charts
- Canvas API: Too low-level, time-consuming to implement
- CSS-only charts: Limited functionality for financial data

## Security for Local Application

### Decision: Basic CORS and input validation
**Rationale**:
- Local-only application reduces security concerns
- Still need input validation for data integrity
- Basic CORS for browser security
- No authentication needed (single user)

**Implementation**:
- Validate all JSON inputs
- Sanitize database inputs
- Basic rate limiting for API calls
- CORS headers for localhost

## Testing Strategy

### Decision: Playwright MCP + Python unittest
**Rationale**:
- Constitutional requirement for Playwright MCP
- Python unittest sufficient for backend logic
- End-to-end testing covers full user workflows
- 80%+ coverage requirement from constitution

**Test Structure**:
```
tests/
├── backend/
│   ├── test_database.py
│   ├── test_api.py
│   └── test_calculations.py
├── frontend/
│   └── playwright_tests/
└── integration/
    └── test_full_workflows.py
```

## Environment Configuration

### Decision: Simple .env file with python-dotenv if needed
**Rationale**:
- Minimal configuration needed for local app
- Database path and port configuration
- Development/production environment distinction

**Configuration needs**:
- Database file path
- Server port
- Default currency (MXN per user requirement)
- Debug mode flag

## Performance Considerations

### Decision: SQLite optimizations and minimal JavaScript
**Rationale**:
- Constitutional requirements: <3s page loads, <100ms interactions
- SQLite indexes for financial queries
- Minimal JavaScript bundle size
- Lazy loading for large transaction lists

**Optimizations**:
- Database indexes on frequently queried columns
- Pagination for transaction lists
- Local storage for UI preferences
- Minified CSS/JS for production