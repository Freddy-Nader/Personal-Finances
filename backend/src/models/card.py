#!/usr/bin/env python3
"""
Card model for Personal Finance Management Application.
Represents credit or debit cards with MXN default currency.
"""

import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pathlib import Path


class Card:
    """Model representing a credit or debit card."""

    def __init__(self, id=None, name=None, type=None, currency='MXN',
                 balance=0.00, credit_limit=None, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.type = type  # 'credit' or 'debit'
        self.currency = currency or 'MXN'  # Default MXN per requirement
        self.balance = Decimal(str(balance)) if balance is not None else Decimal('0.00')
        self.credit_limit = Decimal(str(credit_limit)) if credit_limit is not None else None
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
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def validate(self):
        """Validate card data."""
        errors = []

        if not self.name or not self.name.strip():
            errors.append("Card name is required")

        if self.type not in ['credit', 'debit']:
            errors.append("Card type must be 'credit' or 'debit'")

        if self.type == 'credit' and self.credit_limit is not None and self.credit_limit < 0:
            errors.append("Credit limit cannot be negative")

        if self.type == 'debit' and self.credit_limit is not None:
            errors.append("Debit cards should not have a credit limit")

        if self.balance is not None and not isinstance(self.balance, (int, float, Decimal)):
            errors.append("Balance must be a number")

        return errors

    def save(self):
        """Save card to database."""
        errors = self.validate()
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if self.id is None:
                # Insert new card
                cursor.execute('''
                    INSERT INTO cards (name, type, currency, balance, credit_limit, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.name,
                    self.type,
                    self.currency,
                    float(self.balance),
                    float(self.credit_limit) if self.credit_limit is not None else None,
                    self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
                    self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
                ))
                self.id = cursor.lastrowid
            else:
                # Update existing card
                self.updated_at = datetime.now()
                cursor.execute('''
                    UPDATE cards
                    SET name = ?, balance = ?, credit_limit = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    self.name,
                    float(self.balance),
                    float(self.credit_limit) if self.credit_limit is not None else None,
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
    def find_by_id(cls, card_id):
        """Find card by ID."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM cards WHERE id = ?', (card_id,))
            row = cursor.fetchone()

            if row:
                return cls._from_row(row)
            return None
        finally:
            conn.close()

    @classmethod
    def find_all(cls):
        """Find all cards."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM cards ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [cls._from_row(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def find_by_type(cls, card_type):
        """Find cards by type (credit/debit)."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM cards WHERE type = ? ORDER BY created_at DESC', (card_type,))
            rows = cursor.fetchall()
            return [cls._from_row(row) for row in rows]
        finally:
            conn.close()

    def delete(self):
        """Delete card from database."""
        if self.id is None:
            raise ValueError("Cannot delete card without ID")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Note: Foreign key constraints will handle cascading deletes for sections
            cursor.execute('DELETE FROM cards WHERE id = ?', (self.id,))
            conn.commit()

            deleted_count = cursor.rowcount
            if deleted_count == 0:
                raise ValueError(f"Card with ID {self.id} not found")

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @classmethod
    def _from_row(cls, row):
        """Create Card instance from database row."""
        return cls(
            id=row['id'],
            name=row['name'],
            type=row['type'],
            currency=row['currency'],
            balance=Decimal(str(row['balance'])) if row['balance'] is not None else Decimal('0.00'),
            credit_limit=Decimal(str(row['credit_limit'])) if row['credit_limit'] is not None else None,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Convert card to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'currency': self.currency,
            'balance': float(self.balance),
            'credit_limit': float(self.credit_limit) if self.credit_limit is not None else None,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create Card instance from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            type=data.get('type'),
            currency=data.get('currency', 'MXN'),
            balance=data.get('balance', 0.00),
            credit_limit=data.get('credit_limit'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def get_available_credit(self):
        """Get available credit for credit cards."""
        if self.type != 'credit' or self.credit_limit is None:
            return None

        # For credit cards, balance represents used credit
        # Available credit = credit_limit - balance
        return self.credit_limit - self.balance

    def get_total_balance(self):
        """Get effective balance for dashboard calculations."""
        if self.type == 'debit':
            return self.balance
        elif self.type == 'credit':
            # For credit cards, return negative balance (debt)
            return -self.balance
        return self.balance

    def __str__(self):
        """String representation of card."""
        return f"Card(id={self.id}, name='{self.name}', type='{self.type}', balance={self.balance})"

    def __repr__(self):
        """Developer representation of card."""
        return (f"Card(id={self.id}, name='{self.name}', type='{self.type}', "
                f"currency='{self.currency}', balance={self.balance}, "
                f"credit_limit={self.credit_limit})")