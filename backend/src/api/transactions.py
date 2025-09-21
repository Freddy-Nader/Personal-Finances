#!/usr/bin/env python3
"""
Transaction API handlers
Implements GET, POST, PUT, DELETE endpoints for transactions.
"""

import json
import sys
import os
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from pathlib import Path

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.transaction_service import TransactionService


class TransactionAPI:
    """Transaction API endpoint handlers"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.transaction_service = TransactionService(db_path)

    def handle_request(self, method: str, path: str, query_params: dict, data: dict) -> tuple:
        """Route transaction API requests to appropriate handlers"""

        # Remove /transactions prefix
        api_path = path[13:] if path.startswith('/transactions') else path

        try:
            if api_path == '' or api_path == '/':
                if method == 'GET':
                    return self._get_transactions(query_params)
                elif method == 'POST':
                    return self._create_transaction(data)
                else:
                    return 405, {'error': 'Method not allowed'}

            elif api_path.startswith('/') and api_path.count('/') == 1:
                # Path like /123
                try:
                    transaction_id = int(api_path.strip('/'))
                except ValueError:
                    return 400, {'error': 'Invalid transaction ID format'}

                if method == 'GET':
                    return self._get_transaction_by_id(transaction_id)
                elif method == 'PUT':
                    return self._update_transaction(transaction_id, data)
                elif method == 'DELETE':
                    return self._delete_transaction(transaction_id)
                else:
                    return 405, {'error': 'Method not allowed'}

            else:
                return 404, {'error': 'Transaction endpoint not found'}

        except Exception as e:
            return 500, {'error': f'Internal server error: {str(e)}'}

    def _get_transactions(self, query_params: dict) -> tuple:
        """GET /api/transactions - Get transactions with optional filtering"""
        try:
            # Parse query parameters
            card_id = None
            start_date = None
            end_date = None
            page = 1
            limit = 100

            if 'cardId' in query_params:
                try:
                    card_id = int(query_params['cardId'][0])
                except (ValueError, IndexError):
                    return 400, {'error': 'Invalid cardId parameter'}

            if 'startDate' in query_params:
                try:
                    start_date = datetime.fromisoformat(query_params['startDate'][0])
                except (ValueError, IndexError):
                    return 400, {'error': 'Invalid startDate format (use ISO format)'}

            if 'endDate' in query_params:
                try:
                    end_date = datetime.fromisoformat(query_params['endDate'][0])
                except (ValueError, IndexError):
                    return 400, {'error': 'Invalid endDate format (use ISO format)'}

            if 'page' in query_params:
                try:
                    page = int(query_params['page'][0])
                    if page < 1:
                        page = 1
                except (ValueError, IndexError):
                    page = 1

            if 'limit' in query_params:
                try:
                    limit = int(query_params['limit'][0])
                    if limit < 1 or limit > 1000:
                        limit = 100
                except (ValueError, IndexError):
                    limit = 100

            # Get transactions based on filters
            if start_date or end_date or card_id:
                result = self.transaction_service.get_transactions_by_date_range(
                    start_date, end_date, card_id, page, limit
                )
            else:
                result = self.transaction_service.get_all_transactions(page, limit)

            return 200, result

        except Exception as e:
            return 500, {'error': f'Failed to get transactions: {str(e)}'}

    def _create_transaction(self, data: dict) -> tuple:
        """POST /api/transactions - Create a new transaction"""
        try:
            # Validate required fields
            required_fields = ['amount', 'description', 'transaction_date']
            errors = []

            for field in required_fields:
                if field not in data:
                    errors.append(f'Missing required field: {field}')

            if errors:
                return 400, {'error': 'Validation errors', 'details': errors}

            # Parse and validate data
            try:
                amount = float(data['amount'])
            except (ValueError, TypeError):
                return 400, {'error': 'Invalid amount format'}

            try:
                transaction_date = datetime.fromisoformat(data['transaction_date'])
            except (ValueError, TypeError):
                return 400, {'error': 'Invalid transaction_date format (use ISO format)'}

            description = str(data['description']).strip()
            if not description:
                return 400, {'error': 'Description cannot be empty'}

            # Optional fields
            card_id = data.get('card_id')
            if card_id is not None:
                try:
                    card_id = int(card_id)
                except (ValueError, TypeError):
                    return 400, {'error': 'Invalid card_id format'}

            section_id = data.get('section_id')
            if section_id is not None:
                try:
                    section_id = int(section_id)
                except (ValueError, TypeError):
                    return 400, {'error': 'Invalid section_id format'}

            category = data.get('category')
            is_internal_transfer = bool(data.get('is_internal_transfer', False))

            # Internal transfer fields
            transfer_from_type = data.get('transfer_from_type')
            transfer_from_id = data.get('transfer_from_id')
            transfer_to_type = data.get('transfer_to_type')
            transfer_to_id = data.get('transfer_to_id')

            # Validate internal transfer fields
            if is_internal_transfer:
                if not all([transfer_from_type, transfer_from_id, transfer_to_type, transfer_to_id]):
                    return 400, {'error': 'Internal transfers require all transfer fields'}

                try:
                    transfer_from_id = int(transfer_from_id)
                    transfer_to_id = int(transfer_to_id)
                except (ValueError, TypeError):
                    return 400, {'error': 'Invalid transfer ID format'}

                valid_types = ['card', 'cash', 'stock', 'crypto']
                if transfer_from_type not in valid_types or transfer_to_type not in valid_types:
                    return 400, {'error': f'Transfer types must be one of: {valid_types}'}

            # Create transaction
            transaction = self.transaction_service.create_transaction(
                amount, description, transaction_date, card_id, section_id,
                category, is_internal_transfer, transfer_from_type,
                transfer_from_id, transfer_to_type, transfer_to_id
            )

            return 201, transaction.to_dict()

        except ValueError as e:
            return 400, {'error': str(e)}
        except Exception as e:
            return 500, {'error': f'Failed to create transaction: {str(e)}'}

    def _get_transaction_by_id(self, transaction_id: int) -> tuple:
        """GET /api/transactions/{transactionId} - Get transaction by ID"""
        try:
            transaction = self.transaction_service.get_transaction(transaction_id)

            if not transaction:
                return 404, {'error': f'Transaction {transaction_id} not found'}

            return 200, transaction.to_dict()

        except Exception as e:
            return 500, {'error': f'Failed to get transaction: {str(e)}'}

    def _update_transaction(self, transaction_id: int, data: dict) -> tuple:
        """PUT /api/transactions/{transactionId} - Update transaction"""
        try:
            # Check if transaction exists
            existing = self.transaction_service.get_transaction(transaction_id)
            if not existing:
                return 404, {'error': f'Transaction {transaction_id} not found'}

            # Parse update data
            amount = None
            description = None
            transaction_date = None
            category = None

            if 'amount' in data:
                try:
                    amount = float(data['amount'])
                except (ValueError, TypeError):
                    return 400, {'error': 'Invalid amount format'}

            if 'description' in data:
                description = str(data['description']).strip()
                if not description:
                    return 400, {'error': 'Description cannot be empty'}

            if 'transaction_date' in data:
                try:
                    transaction_date = datetime.fromisoformat(data['transaction_date'])
                except (ValueError, TypeError):
                    return 400, {'error': 'Invalid transaction_date format (use ISO format)'}

            if 'category' in data:
                category = str(data['category']) if data['category'] else None

            # Update transaction
            updated_transaction = self.transaction_service.update_transaction(
                transaction_id, amount, description, transaction_date, category
            )

            if not updated_transaction:
                return 500, {'error': 'Failed to update transaction'}

            return 200, updated_transaction.to_dict()

        except ValueError as e:
            return 400, {'error': str(e)}
        except Exception as e:
            return 500, {'error': f'Failed to update transaction: {str(e)}'}

    def _delete_transaction(self, transaction_id: int) -> tuple:
        """DELETE /api/transactions/{transactionId} - Delete transaction"""
        try:
            success = self.transaction_service.delete_transaction(transaction_id)

            if not success:
                return 404, {'error': f'Transaction {transaction_id} not found'}

            return 204, None

        except Exception as e:
            return 500, {'error': f'Failed to delete transaction: {str(e)}'}


# Utility function for server integration
def handle_transactions_api(method: str, path: str, query_params: dict, data: dict,
                           db_path: str = "./data/finance.db") -> tuple:
    """Handle transactions API requests - for use in server.py"""
    api = TransactionAPI(db_path)
    return api.handle_request(method, path, query_params, data)