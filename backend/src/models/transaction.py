#!/usr/bin/env python3
"""
Transaction model for Personal Finance Management Application.
Represents financial movements with internal transfer support.
"""

import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pathlib import Path


class Transaction:
    """Model representing a financial transaction."""

    def __init__(self, id=None, amount=None, description=None, transaction_date=None,
                 card_id=None, section_id=None, category=None, is_internal_transfer=False,
                 transfer_from_type=None, transfer_from_id=None,
                 transfer_to_type=None, transfer_to_id=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.amount = Decimal(str(amount)) if amount is not None else None
        self.description = description
        self.transaction_date = transaction_date
        self.card_id = card_id
        self.section_id = section_id
        self.category = category
        self.is_internal_transfer = is_internal_transfer
        self.transfer_from_type = transfer_from_type
        self.transfer_from_id = transfer_from_id
        self.transfer_to_type = transfer_to_type
        self.transfer_to_id = transfer_to_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def get_database_path(cls):
        """Get database path from environment or default."""
        try:
            env_path = Path(__file__).parent.parent.parent.parent / '.env'
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        if line.startswith('DATABASE_PATH='):
                            return line.split('=', 1)[1].strip()
        except Exception:
            pass
        return './data/finance.db'

    @classmethod
    def get_connection(cls):
        """Get database connection."""
        db_path = cls.get_database_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def validate(self):
        """Validate transaction data."""
        errors = []

        if self.amount is None:
            errors.append("Amount is required")

        if not self.description or not self.description.strip():
            errors.append("Description is required")

        if self.transaction_date is None:
            errors.append("Transaction date is required")

        # Validate internal transfer fields
        if self.is_internal_transfer:
            if not all([self.transfer_from_type, self.transfer_from_id,
                       self.transfer_to_type, self.transfer_to_id]):
                errors.append("Internal transfers require all transfer fields")

            if self.transfer_from_type not in ['card', 'cash', 'stock', 'crypto']:
                errors.append("Invalid transfer_from_type")

            if self.transfer_to_type not in ['card', 'cash', 'stock', 'crypto']:
                errors.append("Invalid transfer_to_type")

        # Validate card and section relationships
        if self.card_id is not None:
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT id FROM cards WHERE id = ?', (self.card_id,))
                if not cursor.fetchone():
                    errors.append(f"Card with ID {self.card_id} does not exist")
            except Exception:
                errors.append("Database error checking card existence")
            finally:
                conn.close()

        if self.section_id is not None:
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT id FROM sections WHERE id = ?', (self.section_id,))
                if not cursor.fetchone():
                    errors.append(f"Section with ID {self.section_id} does not exist")
            except Exception:
                errors.append("Database error checking section existence")
            finally:
                conn.close()

        return errors

    def save(self):
        """Save transaction to database."""
        errors = self.validate()
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if self.id is None:
                # Insert new transaction
                cursor.execute('''
                    INSERT INTO transactions (
                        amount, description, transaction_date, card_id, section_id,
                        category, is_internal_transfer, transfer_from_type, transfer_from_id,
                        transfer_to_type, transfer_to_id, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    float(self.amount),
                    self.description,
                    self.transaction_date.isoformat() if isinstance(self.transaction_date, datetime) else self.transaction_date,
                    self.card_id,
                    self.section_id,
                    self.category,
                    self.is_internal_transfer,
                    self.transfer_from_type,
                    self.transfer_from_id,
                    self.transfer_to_type,
                    self.transfer_to_id,
                    self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
                    self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
                ))
                self.id = cursor.lastrowid
            else:
                # Update existing transaction
                self.updated_at = datetime.now()
                cursor.execute('''
                    UPDATE transactions
                    SET amount = ?, description = ?, transaction_date = ?, category = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    float(self.amount),
                    self.description,
                    self.transaction_date.isoformat() if isinstance(self.transaction_date, datetime) else self.transaction_date,
                    self.category,
                    self.updated_at.isoformat(),
                    self.id
                ))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

        return self

    @classmethod
    def find_by_id(cls, transaction_id):
        """Find transaction by ID."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
            row = cursor.fetchone()
            if row:
                return cls._from_row(row)
            return None
        finally:
            conn.close()

    @classmethod
    def find_all(cls, card_id=None, start_date=None, end_date=None, page=1, limit=100):
        """Find transactions with optional filters and pagination."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            # Build query with optional filters
            where_conditions = []
            params = []

            if card_id is not None:
                where_conditions.append('card_id = ?')
                params.append(card_id)

            if start_date is not None:
                where_conditions.append('transaction_date >= ?')
                params.append(start_date)

            if end_date is not None:
                where_conditions.append('transaction_date <= ?')
                params.append(end_date)

            where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''

            # Count total records
            count_query = f'SELECT COUNT(*) as total FROM transactions {where_clause}'
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']

            # Get paginated results
            offset = (page - 1) * limit
            query = f'''
                SELECT * FROM transactions {where_clause}
                ORDER BY transaction_date DESC, created_at DESC
                LIMIT ? OFFSET ?
            '''
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            transactions = [cls._from_row(row) for row in rows]

            return {
                'transactions': transactions,
                'total': total,
                'page': page,
                'limit': limit,
                'has_next': (page * limit) < total
            }
        finally:
            conn.close()

    @classmethod
    def find_by_card_id(cls, card_id):
        """Find all transactions for a specific card."""
        return cls.find_all(card_id=card_id, limit=1000)  # High limit for card-specific queries

    def delete(self):
        """Delete transaction from database."""
        if self.id is None:
            raise ValueError("Cannot delete transaction without ID")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM transactions WHERE id = ?', (self.id,))
            conn.commit()

            deleted_count = cursor.rowcount
            if deleted_count == 0:
                raise ValueError(f"Transaction with ID {self.id} not found")

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @classmethod
    def create_internal_transfer(cls, amount, description, from_card_id, to_card_id, transaction_date=None):
        """Create paired transactions for internal transfer."""
        if transaction_date is None:
            transaction_date = datetime.now()

        # Create debit transaction (from account)
        debit_transaction = cls(
            amount=-abs(amount),  # Ensure negative amount
            description=f"Transfer to card {to_card_id}: {description}",
            transaction_date=transaction_date,
            card_id=from_card_id,
            is_internal_transfer=True,
            transfer_from_type='card',
            transfer_from_id=from_card_id,
            transfer_to_type='card',
            transfer_to_id=to_card_id
        )

        # Create credit transaction (to account)
        credit_transaction = cls(
            amount=abs(amount),  # Ensure positive amount
            description=f"Transfer from card {from_card_id}: {description}",
            transaction_date=transaction_date,
            card_id=to_card_id,
            is_internal_transfer=True,
            transfer_from_type='card',
            transfer_from_id=from_card_id,
            transfer_to_type='card',
            transfer_to_id=to_card_id
        )

        # Save both transactions
        debit_transaction.save()
        credit_transaction.save()

        return debit_transaction, credit_transaction

    @classmethod
    def _from_row(cls, row):
        """Create Transaction instance from database row."""
        return cls(
            id=row['id'],
            amount=Decimal(str(row['amount'])) if row['amount'] is not None else None,
            description=row['description'],
            transaction_date=row['transaction_date'],
            card_id=row['card_id'],
            section_id=row['section_id'],
            category=row['category'],
            is_internal_transfer=bool(row['is_internal_transfer']),
            transfer_from_type=row['transfer_from_type'],
            transfer_from_id=row['transfer_from_id'],
            transfer_to_type=row['transfer_to_type'],
            transfer_to_id=row['transfer_to_id'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Convert transaction to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'amount': float(self.amount) if self.amount is not None else None,
            'description': self.description,
            'transaction_date': self.transaction_date.isoformat() if isinstance(self.transaction_date, datetime) else self.transaction_date,
            'card_id': self.card_id,
            'section_id': self.section_id,
            'category': self.category,
            'is_internal_transfer': self.is_internal_transfer,
            'transfer_from_type': self.transfer_from_type,
            'transfer_from_id': self.transfer_from_id,
            'transfer_to_type': self.transfer_to_type,
            'transfer_to_id': self.transfer_to_id,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }

    def __str__(self):
        """String representation of transaction."""
        return f"Transaction(id={self.id}, amount={self.amount}, description='{self.description}')"