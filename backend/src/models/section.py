#!/usr/bin/env python3
"""
Section model for Personal Finance Management Application.
Represents categories/sections within cards (e.g., "emergency", "birthday").
"""

import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pathlib import Path


class Section:
    """Model representing a section within a card."""

    def __init__(self, id=None, card_id=None, name=None, initial_balance=0.00, created_at=None):
        self.id = id
        self.card_id = card_id
        self.name = name
        self.initial_balance = Decimal(str(initial_balance)) if initial_balance is not None else Decimal('0.00')
        self.created_at = created_at or datetime.now()

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
        """Validate section data."""
        errors = []

        if not self.name or not self.name.strip():
            errors.append("Section name is required")

        if self.card_id is None:
            errors.append("Card ID is required")

        if self.initial_balance is not None and not isinstance(self.initial_balance, (int, float, Decimal)):
            errors.append("Initial balance must be a number")

        # Check if card exists
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

        return errors

    def save(self):
        """Save section to database."""
        errors = self.validate()
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if self.id is None:
                # Check for duplicate section name within the same card
                cursor.execute('''
                    SELECT id FROM sections WHERE card_id = ? AND name = ?
                ''', (self.card_id, self.name))

                if cursor.fetchone():
                    raise ValueError(f"Section '{self.name}' already exists for this card")

                # Insert new section
                cursor.execute('''
                    INSERT INTO sections (card_id, name, initial_balance, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    self.card_id,
                    self.name,
                    float(self.initial_balance),
                    self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
                ))
                self.id = cursor.lastrowid
            else:
                # Update existing section
                # Check for duplicate name (excluding current section)
                cursor.execute('''
                    SELECT id FROM sections WHERE card_id = ? AND name = ? AND id != ?
                ''', (self.card_id, self.name, self.id))

                if cursor.fetchone():
                    raise ValueError(f"Section '{self.name}' already exists for this card")

                cursor.execute('''
                    UPDATE sections
                    SET name = ?, initial_balance = ?
                    WHERE id = ?
                ''', (
                    self.name,
                    float(self.initial_balance),
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
    def find_by_id(cls, section_id):
        """Find section by ID."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM sections WHERE id = ?', (section_id,))
            row = cursor.fetchone()

            if row:
                return cls._from_row(row)
            return None
        finally:
            conn.close()

    @classmethod
    def find_by_card_id(cls, card_id):
        """Find all sections for a specific card."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT * FROM sections WHERE card_id = ? ORDER BY created_at ASC
            ''', (card_id,))
            rows = cursor.fetchall()
            return [cls._from_row(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def find_all(cls):
        """Find all sections."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM sections ORDER BY card_id, created_at ASC')
            rows = cursor.fetchall()
            return [cls._from_row(row) for row in rows]
        finally:
            conn.close()

    def delete(self):
        """Delete section from database."""
        if self.id is None:
            raise ValueError("Cannot delete section without ID")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM sections WHERE id = ?', (self.id,))
            conn.commit()

            deleted_count = cursor.rowcount
            if deleted_count == 0:
                raise ValueError(f"Section with ID {self.id} not found")

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_card(self):
        """Get the associated card."""
        if self.card_id is None:
            return None

        # Import here to avoid circular import
        from .card import Card
        return Card.find_by_id(self.card_id)

    def get_current_balance(self):
        """Calculate current balance based on transactions."""
        # This would calculate the current balance by summing transactions
        # For now, return initial balance (can be enhanced with transaction model)
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as transaction_sum
                FROM transactions
                WHERE section_id = ?
            ''', (self.id,))
            result = cursor.fetchone()
            transaction_sum = Decimal(str(result['transaction_sum'])) if result['transaction_sum'] else Decimal('0.00')

            return self.initial_balance + transaction_sum
        except Exception:
            # If transactions table doesn't exist yet, return initial balance
            return self.initial_balance
        finally:
            conn.close()

    @classmethod
    def _from_row(cls, row):
        """Create Section instance from database row."""
        return cls(
            id=row['id'],
            card_id=row['card_id'],
            name=row['name'],
            initial_balance=Decimal(str(row['initial_balance'])) if row['initial_balance'] is not None else Decimal('0.00'),
            created_at=row['created_at']
        )

    def to_dict(self):
        """Convert section to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'card_id': self.card_id,
            'name': self.name,
            'initial_balance': float(self.initial_balance),
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create Section instance from dictionary."""
        return cls(
            id=data.get('id'),
            card_id=data.get('card_id'),
            name=data.get('name'),
            initial_balance=data.get('initial_balance', 0.00),
            created_at=data.get('created_at')
        )

    def __str__(self):
        """String representation of section."""
        return f"Section(id={self.id}, card_id={self.card_id}, name='{self.name}', balance={self.initial_balance})"

    def __repr__(self):
        """Developer representation of section."""
        return (f"Section(id={self.id}, card_id={self.card_id}, name='{self.name}', "
                f"initial_balance={self.initial_balance})")