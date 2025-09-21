# Tasks: Personal Finance Management Application

**Input**: Design documents from `/specs/001-build-an-application/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/api-contracts.yaml, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   -> Tech stack: Python 3.11+ backend, vanilla HTML/CSS/JavaScript frontend
   -> Structure: Web application (backend/ + frontend/)
   -> Storage: SQLite database
2. Load design documents:
   -> data-model.md: 6 entities (Card, Section, Transaction, InvestmentPosition, Movement, CardFeesInterests)
   -> contracts/api-contracts.yaml: 14 API endpoints across 4 groups
   -> quickstart.md: 5 user stories with test scenarios
3. Generate tasks by category:
   -> Setup: project structure, dependencies, environment
   -> Tests: contract tests, integration tests (TDD)
   -> Core: models, services, API endpoints
   -> Integration: database, server, frontend
   -> Polish: unit tests, performance validation
4. Apply task rules:
   -> Different files = [P] for parallel execution
   -> Tests before implementation (TDD principle)
   -> Dependencies: Models -> Services -> Endpoints -> Frontend
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup
- [x] T001 Create project structure per implementation plan (backend/, frontend/, tests/, data/)
- [x] T002 Initialize Python virtual environment (.venv) and create .env from data-model.md
- [x] T003 [P] Create database initialization script in backend/src/database/init_db.py
- [x] T004 [P] Set up minimal HTTP server foundation in backend/src/server.py

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests [P] - All can run in parallel
- [x] T005 [P] Contract test GET /api/cards in tests/contract/test_cards_get.py
- [x] T006 [P] Contract test POST /api/cards in tests/contract/test_cards_post.py
- [x] T007 [P] Contract test GET /api/cards/{cardId} in tests/contract/test_cards_by_id.py
- [x] T008 [P] Contract test PUT /api/cards/{cardId} in tests/contract/test_cards_put.py
- [x] T009 [P] Contract test DELETE /api/cards/{cardId} in tests/contract/test_cards_delete.py
- [x] T010 [P] Contract test GET /api/cards/{cardId}/sections in tests/contract/test_sections_get.py
- [x] T011 [P] Contract test POST /api/cards/{cardId}/sections in tests/contract/test_sections_post.py
- [x] T012 [P] Contract test GET /api/transactions in tests/contract/test_transactions_get.py
- [x] T013 [P] Contract test POST /api/transactions in tests/contract/test_transactions_post.py
- [x] T014 [P] Contract test GET /api/transactions/{transactionId} in tests/contract/test_transaction_by_id.py
- [x] T015 [P] Contract test PUT /api/transactions/{transactionId} in tests/contract/test_transaction_put.py
- [x] T016 [P] Contract test DELETE /api/transactions/{transactionId} in tests/contract/test_transaction_delete.py
- [x] T017 [P] Contract test GET /api/investments/positions in tests/contract/test_positions_get.py
- [x] T018 [P] Contract test POST /api/investments/positions in tests/contract/test_positions_post.py
- [x] T019 [P] Contract test GET /api/investments/movements in tests/contract/test_movements_get.py
- [x] T020 [P] Contract test POST /api/investments/movements in tests/contract/test_movements_post.py
- [x] T021 [P] Contract test GET /api/dashboard/summary in tests/contract/test_dashboard_summary.py
- [x] T022 [P] Contract test GET /api/dashboard/charts in tests/contract/test_dashboard_charts.py

### Integration Tests [P] - Based on quickstart user stories
- [x] T023 [P] Integration test dashboard analytics workflow in tests/integration/test_dashboard_analytics.py
- [ ] T024 [P] Integration test transaction management workflow in tests/integration/test_transaction_management.py
- [ ] T025 [P] Integration test card management workflow in tests/integration/test_card_management.py
- [ ] T026 [P] Integration test investment tracking workflow in tests/integration/test_investment_tracking.py
- [ ] T027 [P] Integration test time-based analytics workflow in tests/integration/test_time_analytics.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Database Models [P] - All can run in parallel
- [x] T028 [P] Card model with MXN default currency in backend/src/models/card.py
- [x] T029 [P] Section model with card relationship in backend/src/models/section.py
- [x] T030 [P] Transaction model with internal transfer support in backend/src/models/transaction.py
- [ ] T031 [P] InvestmentPosition model in backend/src/models/investment_position.py
- [ ] T032 [P] Movement model with exact timing in backend/src/models/movement.py
- [ ] T033 [P] CardFeesInterests model with compound frequencies in backend/src/models/card_fees_interests.py

### Database Services [P] - All can run in parallel (depend on models)
- [x] T034 [P] CardService CRUD operations in backend/src/services/card_service.py
- [x] T035 [P] SectionService CRUD operations in backend/src/services/section_service.py
- [ ] T036 [P] TransactionService with internal transfer logic in backend/src/services/transaction_service.py
- [ ] T037 [P] InvestmentService with portfolio calculations in backend/src/services/investment_service.py
- [ ] T038 [P] DashboardService with analytics in backend/src/services/dashboard_service.py

### API Endpoints - Sequential (share server.py file)
- [x] T039 Implement GET /api/cards endpoint in backend/src/server.py
- [x] T040 Implement POST /api/cards endpoint in backend/src/server.py
- [x] T041 Implement GET /api/cards/{cardId} endpoint in backend/src/server.py
- [x] T042 Implement PUT /api/cards/{cardId} endpoint in backend/src/server.py
- [x] T043 Implement DELETE /api/cards/{cardId} endpoint in backend/src/server.py
- [x] T044 Implement GET /api/cards/{cardId}/sections endpoint in backend/src/server.py
- [x] T045 Implement POST /api/cards/{cardId}/sections endpoint in backend/src/server.py
- [ ] T046 Implement GET /api/transactions endpoint in backend/src/api/transactions.py
- [ ] T047 Implement POST /api/transactions endpoint in backend/src/api/transactions.py
- [ ] T048 Implement GET /api/transactions/{transactionId} endpoint in backend/src/api/transactions.py
- [ ] T049 Implement PUT /api/transactions/{transactionId} endpoint in backend/src/api/transactions.py
- [ ] T050 Implement DELETE /api/transactions/{transactionId} endpoint in backend/src/api/transactions.py
- [ ] T051 Implement GET /api/investments/positions endpoint in backend/src/api/investments.py
- [ ] T052 Implement POST /api/investments/positions endpoint in backend/src/api/investments.py
- [ ] T053 Implement GET /api/investments/movements endpoint in backend/src/api/investments.py
- [ ] T054 Implement POST /api/investments/movements endpoint in backend/src/api/investments.py
- [ ] T055 Implement GET /api/dashboard/summary endpoint in backend/src/api/dashboard.py
- [ ] T056 Implement GET /api/dashboard/charts endpoint in backend/src/api/dashboard.py

## Phase 3.4: Frontend Implementation
### Frontend Core [P] - All can run in parallel
- [ ] T057 [P] Create dashboard page with Notion-inspired styling in frontend/pages/dashboard.html
- [ ] T058 [P] Create transactions page in frontend/pages/transactions.html
- [ ] T059 [P] Create manage page in frontend/pages/manage.html
- [ ] T060 [P] Create movements page in frontend/pages/movements.html
- [ ] T061 [P] Create shared CSS with Notion styling in frontend/css/finance-app.css
- [ ] T062 [P] Create API wrapper utility in frontend/js/api.js
- [ ] T063 [P] Create reusable UI components in frontend/js/components.js
- [ ] T064 [P] Create utility functions in frontend/js/utils.js

### Frontend JavaScript - Sequential (shared across pages)
- [ ] T065 Implement dashboard JavaScript with Chart.js integration in frontend/js/dashboard.js
- [ ] T066 Implement transaction form and list JavaScript in frontend/js/transactions.js
- [ ] T067 Implement card/section management JavaScript in frontend/js/manage.js
- [ ] T068 Implement investment tracking JavaScript in frontend/js/movements.js

## Phase 3.5: Integration & Testing
- [ ] T069 Connect database to API endpoints with error handling
- [ ] T070 Add CORS headers and basic security for local app
- [ ] T071 Implement static file serving in backend/src/server.py
- [ ] T072 Add input validation and error responses across all endpoints
- [ ] T073 Implement Chart.js dashboard visualizations
- [ ] T074 Add pagination support for transaction lists

## Phase 3.6: Polish & Validation
### Performance Tests [P]
- [ ] T075 [P] Performance test page load times (<3s) in tests/performance/test_load_times.py
- [ ] T076 [P] Performance test interaction response (<100ms) in tests/performance/test_interactions.py
- [ ] T077 [P] Performance test bundle size (<500KB) in tests/performance/test_bundle_size.py

### End-to-End Tests with Playwright MCP [P]
- [ ] T078 [P] E2E test dashboard user story in tests/frontend/test_dashboard_e2e.py
- [ ] T079 [P] E2E test transaction management in tests/frontend/test_transactions_e2e.py
- [ ] T080 [P] E2E test card management in tests/frontend/test_cards_e2e.py
- [ ] T081 [P] E2E test investment tracking in tests/frontend/test_investments_e2e.py

### Final Validation
- [ ] T082 Run complete quickstart validation per quickstart.md
- [ ] T083 Validate constitutional requirements (performance, testing, UX)
- [ ] T084 Clean up code and remove any duplication

## Dependencies
- Setup (T001-T004) before everything
- Contract tests (T005-T022) before models (T028-T033)
- Integration tests (T023-T027) before services (T034-T038)
- Models (T028-T033) before services (T034-T038)
- Services (T034-T038) before API endpoints (T039-T056)
- API endpoints (T039-T056) before frontend (T057-T074)
- Core implementation before performance tests (T075-T081)
- All implementation before final validation (T082-T084)

## Parallel Execution Examples
```bash
# Launch contract tests together (T005-T022):
# All 18 contract tests can run simultaneously as they're in different files

# Launch integration tests together (T023-T027):
# All 5 integration tests can run simultaneously

# Launch model creation together (T028-T033):
# All 6 models can be created simultaneously

# Launch service creation together (T034-T038):
# All 5 services can be created simultaneously

# Launch frontend pages together (T057-T064):
# All frontend files can be created simultaneously
```

## Validation Checklist
*GATE: Checked before considering tasks complete*

- [x] All 14 API endpoints have corresponding contract tests
- [x] All 6 entities have model creation tasks
- [x] All 5 user stories have integration tests
- [x] All tests come before implementation (TDD)
- [x] Parallel tasks ([P]) are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Dependencies properly ordered: Setup -> Tests -> Models -> Services -> Endpoints -> Frontend -> Polish

## Notes
- [P] tasks = different files, no dependencies, can run in parallel
- Verify ALL tests fail before implementing (TDD principle)
- Default currency MXN per user requirement
- Chart.js justified as minimal framework exception
- Constitutional requirements: <3s loads, <100ms interactions, <500KB bundles
- Internal transfers create paired transactions (debit/credit)
- Investment prices fetched on-demand, not stored
- Commit after each completed task