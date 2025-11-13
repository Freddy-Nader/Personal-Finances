#!/usr/bin/env python3
"""
Transaction Service
Handles CRUD operations for transactions with internal transfer logic.
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import sys
import os

# Add models to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.transaction import Transaction, TransactionDB
from models.card import CardDB
from models.section import SectionDB


class TransactionService:
    """Service for transaction operations with business logic"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.db_path = db_path
        self.transaction_db = TransactionDB(db_path)
        self.card_db = CardDB(db_path)
        self.section_db = SectionDB(db_path)

    def create_transaction(self, amount: float, description: str, transaction_date: datetime,
                          card_id: int = None, section_id: int = None, category: str = None,
                          is_internal_transfer: bool = False, transfer_from_type: str = None,
                          transfer_from_id: int = None, transfer_to_type: str = None,
                          transfer_to_id: int = None) -> Transaction:
        """Create a new transaction with validation and internal transfer handling"""

        # Validate internal transfer requirements
        if is_internal_transfer:
            if not all([transfer_from_type, transfer_from_id, transfer_to_type, transfer_to_id]):
                raise ValueError("Internal transfers require all transfer fields to be specified")

            # Create paired transactions for internal transfers
            return self._create_internal_transfer(
                amount, description, transaction_date, transfer_from_type,
                transfer_from_id, transfer_to_type, transfer_to_id, category
            )

        # Validate card/section relationship
        if section_id and card_id:
            section = self.section_db.get_section(section_id)
            if not section or section.card_id != card_id:
                raise ValueError("Section does not belong to the specified card")

        # Create regular transaction
        return self.transaction_db.create_transaction(
            amount, description, transaction_date, card_id, section_id,
            category, is_internal_transfer, transfer_from_type, transfer_from_id,
            transfer_to_type, transfer_to_id
        )

    def _create_internal_transfer(self, amount: float, description: str, transaction_date: datetime,
                                 transfer_from_type: str, transfer_from_id: int,
                                 transfer_to_type: str, transfer_to_id: int,
                                 category: str = None) -> Transaction:
        """Create paired transactions for internal transfers"""

        # Ensure amount is positive for transfer logic
        transfer_amount = abs(amount)

        # Create debit transaction (from account)
        debit_card_id = transfer_from_id if transfer_from_type == 'card' else None
        debit_transaction = self.transaction_db.create_transaction(
            -transfer_amount,  # Negative for debit
            f"{description} (Transfer out to {transfer_to_type})",
            transaction_date,
            card_id=debit_card_id,
            section_id=None,
            category=category,
            is_internal_transfer=True,
            transfer_from_type=transfer_from_type,
            transfer_from_id=transfer_from_id,
            transfer_to_type=transfer_to_type,
            transfer_to_id=transfer_to_id
        )

        # Create credit transaction (to account)
        credit_card_id = transfer_to_id if transfer_to_type == 'card' else None
        credit_transaction = self.transaction_db.create_transaction(
            transfer_amount,  # Positive for credit
            f"{description} (Transfer in from {transfer_from_type})",
            transaction_date,
            card_id=credit_card_id,
            section_id=None,
            category=category,
            is_internal_transfer=True,
            transfer_from_type=transfer_from_type,
            transfer_from_id=transfer_from_id,
            transfer_to_type=transfer_to_type,
            transfer_to_id=transfer_to_id
        )

        # Return the credit transaction (arbitrary choice, both are created)
        return credit_transaction

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.transaction_db.get_transaction(transaction_id)

    def get_all_transactions(self, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get all transactions with pagination"""
        transactions = self.transaction_db.get_all_transactions()

        # Calculate pagination
        total = len(transactions)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        paginated_transactions = transactions[start_idx:end_idx]

        return {
            'transactions': [t.to_dict() for t in paginated_transactions],
            'total': total,
            'page': page,
            'limit': limit,
            'has_next': end_idx < total
        }

    def get_transactions_by_card(self, card_id: int, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get transactions for a specific card with pagination"""
        transactions = self.transaction_db.get_transactions_by_card(card_id)

        # Calculate pagination
        total = len(transactions)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        paginated_transactions = transactions[start_idx:end_idx]

        return {
            'transactions': [t.to_dict() for t in paginated_transactions],
            'total': total,
            'page': page,
            'limit': limit,
            'has_next': end_idx < total
        }

    def get_transactions_by_date_range(self, start_date: datetime = None, end_date: datetime = None,
                                     card_id: int = None, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get transactions filtered by date range and optionally by card"""
        transactions = self.transaction_db.get_transactions_by_date_range(start_date, end_date, card_id)

        # Calculate pagination
        total = len(transactions)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        paginated_transactions = transactions[start_idx:end_idx]

        return {
            'transactions': [t.to_dict() for t in paginated_transactions],
            'total': total,
            'page': page,
            'limit': limit,
            'has_next': end_idx < total
        }

    def get_transactions_by_category(self, category: str, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get transactions by category with pagination"""
        transactions = self.transaction_db.get_transactions_by_category(category)

        # Calculate pagination
        total = len(transactions)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        paginated_transactions = transactions[start_idx:end_idx]

        return {
            'transactions': [t.to_dict() for t in paginated_transactions],
            'total': total,
            'page': page,
            'limit': limit,
            'has_next': end_idx < total
        }

    def update_transaction(self, transaction_id: int, amount: float = None,
                          description: str = None, transaction_date: datetime = None,
                          category: str = None) -> Optional[Transaction]:
        """Update transaction (limited fields to prevent breaking internal transfers)"""

        # Get existing transaction
        existing = self.get_transaction(transaction_id)
        if not existing:
            return None

        # Prevent updating internal transfer transactions
        if existing.is_internal_transfer:
            raise ValueError("Cannot update internal transfer transactions")

        return self.transaction_db.update_transaction(
            transaction_id, amount, description, transaction_date, category
        )

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete transaction with internal transfer handling"""

        # Get existing transaction
        existing = self.get_transaction(transaction_id)
        if not existing:
            return False

        # For internal transfers, delete both paired transactions
        if existing.is_internal_transfer:
            return self._delete_internal_transfer(existing)

        return self.transaction_db.delete_transaction(transaction_id)

    def _delete_internal_transfer(self, transaction: Transaction) -> bool:
        """Delete both transactions in an internal transfer pair"""

        # Find the paired transaction
        paired_transactions = self.transaction_db.get_internal_transfer_pair(
            transaction.transfer_from_type, transaction.transfer_from_id,
            transaction.transfer_to_type, transaction.transfer_to_id,
            transaction.transaction_date
        )

        # Delete all transactions in the transfer
        success = True
        for trans in paired_transactions:
            if not self.transaction_db.delete_transaction(trans.id):
                success = False

        return success

    def get_spending_summary(self, start_date: datetime = None, end_date: datetime = None,
                           card_id: int = None) -> Dict[str, Any]:
        """Get spending summary with category breakdown"""
        transactions = self.transaction_db.get_transactions_by_date_range(start_date, end_date, card_id)

        # Filter out internal transfers for spending analysis
        transactions = [t for t in transactions if not t.is_internal_transfer]

        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(t.amount for t in transactions if t.amount < 0)

        # Category breakdown
        category_summary = {}
        for transaction in transactions:
            category = transaction.category or 'Uncategorized'
            if category not in category_summary:
                category_summary[category] = {'income': 0, 'expenses': 0, 'count': 0}

            if transaction.amount > 0:
                category_summary[category]['income'] += transaction.amount
            else:
                category_summary[category]['expenses'] += transaction.amount

            category_summary[category]['count'] += 1

        return {
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'card_id': card_id
            },
            'totals': {
                'income': total_income,
                'expenses': total_expenses,
                'net': total_income + total_expenses
            },
            'categories': category_summary,
            'transaction_count': len(transactions)
        }

    def get_monthly_trends(self, months: int = 12, card_id: int = None) -> List[Dict[str, Any]]:
        """Get monthly spending trends"""
        from datetime import datetime, timedelta
        from calendar import monthrange

        end_date = datetime.now()
        trends = []

        for i in range(months):
            # Calculate month boundaries
            month_date = datetime(end_date.year, end_date.month, 1) - timedelta(days=i*30)
            month_start = datetime(month_date.year, month_date.month, 1)
            _, last_day = monthrange(month_date.year, month_date.month)
            month_end = datetime(month_date.year, month_date.month, last_day, 23, 59, 59)

            # Get summary for the month
            summary = self.get_spending_summary(month_start, month_end, card_id)

            trends.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': month_start.strftime('%B %Y'),
                'income': summary['totals']['income'],
                'expenses': summary['totals']['expenses'],
                'net': summary['totals']['net'],
                'transaction_count': summary['transaction_count']
            })

        return list(reversed(trends))  # Return chronological order

    def validate_internal_transfer(self, transfer_from_type: str, transfer_from_id: int,
                                  transfer_to_type: str, transfer_to_id: int) -> Dict[str, Any]:
        """Validate internal transfer parameters"""

        errors = []

        # Validate transfer types
        valid_types = ['card', 'cash', 'stock', 'crypto']
        if transfer_from_type not in valid_types:
            errors.append(f"Invalid transfer_from_type: {transfer_from_type}")
        if transfer_to_type not in valid_types:
            errors.append(f"Invalid transfer_to_type: {transfer_to_type}")

        # Prevent transferring to the same account
        if (transfer_from_type == transfer_to_type and
            transfer_from_id == transfer_to_id):
            errors.append("Cannot transfer to the same account")

        # Validate card IDs exist
        if transfer_from_type == 'card':
            if not self.card_db.get_card(transfer_from_id):
                errors.append(f"Source card {transfer_from_id} does not exist")

        if transfer_to_type == 'card':
            if not self.card_db.get_card(transfer_to_id):
                errors.append(f"Destination card {transfer_to_id} does not exist")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def get_balance_history(self, card_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get balance history for a card over time"""
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get card current balance
        card = self.card_db.get_card(card_id)
        if not card:
            return []

        # Get all transactions for the period
        transactions = self.transaction_db.get_transactions_by_date_range(start_date, end_date, card_id)
        transactions.sort(key=lambda t: t.transaction_date)

        # Calculate daily balances
        current_balance = card.balance
        daily_balances = []

        # Work backwards from current balance
        for transaction in reversed(transactions):
            # Subtract transaction to get previous balance
            current_balance -= transaction.amount

        # Now work forwards to build history
        for i in range(days + 1):
            date = start_date + timedelta(days=i)

            # Apply transactions for this day
            day_transactions = [t for t in transactions
                              if t.transaction_date.date() == date.date()]

            for transaction in day_transactions:
                current_balance += transaction.amount

            daily_balances.append({
                'date': date.strftime('%Y-%m-%d'),
                'balance': round(current_balance, 2),
                'transaction_count': len(day_transactions)
            })

        return daily_balances


# Utility functions for external use
def create_transaction_service(db_path: str = "./data/finance.db") -> TransactionService:
    """Create a transaction service instance"""
    return TransactionService(db_path)