#!/usr/bin/env python3
"""
Card Fees and Interests Model
Represents interests (positive) and fees (negative) associated with cards with detailed compounding.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import math


@dataclass
class CardFeesInterests:
    """Card Fees and Interests data model"""
    id: Optional[int]
    card_id: int
    name: str
    rate: float  # Interest rate as percentage (e.g., 5.0000 for 5%)
    is_fee: bool  # True for fees, False for interests
    payment_frequency: str  # How often interest/fee is applied
    compound_frequency: str  # How often interest compounds
    is_active: bool
    created_at: Optional[datetime]

    def __post_init__(self):
        """Validate card fees/interests data after initialization"""
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")

        if self.rate < 0:
            raise ValueError("rate must be non-negative (use is_fee flag for fees)")

        valid_payment_frequencies = ['daily', 'weekly', 'monthly', 'quarterly', 'annually']
        if self.payment_frequency not in valid_payment_frequencies:
            raise ValueError(f"payment_frequency must be one of: {valid_payment_frequencies}")

        valid_compound_frequencies = [
            'daily_365', 'daily_360', 'semi_weekly_104', 'weekly_52',
            'bi_weekly_26', 'semi_monthly_24', 'monthly_12', 'bi_monthly_6',
            'quarterly_4', 'half_yearly_2', 'yearly_1'
        ]
        if self.compound_frequency not in valid_compound_frequencies:
            raise ValueError(f"compound_frequency must be one of: {valid_compound_frequencies}")

        # Normalize name
        self.name = self.name.strip()

    @classmethod
    def from_db_row(cls, row) -> 'CardFeesInterests':
        """Create CardFeesInterests from database row"""
        return cls(
            id=row[0],
            card_id=row[1],
            name=row[2],
            rate=float(row[3]),
            is_fee=bool(row[4]),
            payment_frequency=row[5],
            compound_frequency=row[6],
            is_active=bool(row[7]),
            created_at=datetime.fromisoformat(row[8]) if row[8] else None
        )

    def to_dict(self) -> dict:
        """Convert card fees/interests to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'card_id': self.card_id,
            'name': self.name,
            'rate': self.rate,
            'is_fee': self.is_fee,
            'payment_frequency': self.payment_frequency,
            'compound_frequency': self.compound_frequency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_compound_periods_per_year(self) -> int:
        """Get number of compound periods per year from compound_frequency"""
        frequency_map = {
            'daily_365': 365,
            'daily_360': 360,
            'semi_weekly_104': 104,  # Twice per week
            'weekly_52': 52,
            'bi_weekly_26': 26,  # Every two weeks
            'semi_monthly_24': 24,  # Twice per month
            'monthly_12': 12,
            'bi_monthly_6': 6,  # Every two months
            'quarterly_4': 4,
            'half_yearly_2': 2,
            'yearly_1': 1
        }
        return frequency_map[self.compound_frequency]

    def get_payment_periods_per_year(self) -> int:
        """Get number of payment periods per year from payment_frequency"""
        frequency_map = {
            'daily': 365,
            'weekly': 52,
            'monthly': 12,
            'quarterly': 4,
            'annually': 1
        }
        return frequency_map[self.payment_frequency]

    def calculate_compound_amount(self, principal: float, time_years: float) -> float:
        """
        Calculate compound interest amount using the formula:
        A = P(1 + r/n)^(nt)
        Where:
        - A = final amount
        - P = principal
        - r = annual interest rate (as decimal)
        - n = number of times interest compounds per year
        - t = time in years
        """
        if principal <= 0 or time_years <= 0:
            return 0

        annual_rate = self.rate / 100.0  # Convert percentage to decimal
        compound_periods = self.get_compound_periods_per_year()

        # Compound interest formula
        final_amount = principal * math.pow(1 + annual_rate / compound_periods, compound_periods * time_years)

        # For fees, return negative amount
        if self.is_fee:
            return -(final_amount - principal)
        else:
            return final_amount - principal

    def calculate_effective_annual_rate(self) -> float:
        """Calculate effective annual rate accounting for compounding"""
        annual_rate = self.rate / 100.0
        compound_periods = self.get_compound_periods_per_year()

        # Effective annual rate formula: (1 + r/n)^n - 1
        effective_rate = math.pow(1 + annual_rate / compound_periods, compound_periods) - 1
        return effective_rate * 100.0  # Convert back to percentage


class CardFeesInterestsDB:
    """Database operations for Card Fees and Interests"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_fee_interest(self, card_id: int, name: str, rate: float, is_fee: bool = False,
                           payment_frequency: str = 'annually',
                           compound_frequency: str = 'daily_365') -> CardFeesInterests:
        """Create a new card fee or interest"""
        # Create and validate fee/interest
        fee_interest = CardFeesInterests(
            id=None,
            card_id=card_id,
            name=name,
            rate=rate,
            is_fee=is_fee,
            payment_frequency=payment_frequency,
            compound_frequency=compound_frequency,
            is_active=True,
            created_at=None
        )

        with self._get_connection() as conn:
            # Verify card exists
            card_exists = conn.execute(
                "SELECT id FROM cards WHERE id = ?",
                (card_id,)
            ).fetchone()

            if not card_exists:
                raise ValueError(f"Card {card_id} does not exist")

            # Check for duplicate name for the same card
            existing = conn.execute(
                "SELECT id FROM card_fees_interests WHERE card_id = ? AND name = ?",
                (card_id, fee_interest.name)
            ).fetchone()

            if existing:
                raise ValueError(f"Fee/Interest '{fee_interest.name}' already exists for this card")

            # Insert new fee/interest
            cursor = conn.execute(
                """
                INSERT INTO card_fees_interests
                (card_id, name, rate, is_fee, payment_frequency, compound_frequency, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (fee_interest.card_id, fee_interest.name, fee_interest.rate, fee_interest.is_fee,
                 fee_interest.payment_frequency, fee_interest.compound_frequency, fee_interest.is_active)
            )

            # Get the created fee/interest
            fee_interest_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM card_fees_interests WHERE id = ?",
                (fee_interest_id,)
            ).fetchone()

            return CardFeesInterests.from_db_row(row)

    def get_fee_interest(self, fee_interest_id: int) -> Optional[CardFeesInterests]:
        """Get card fee/interest by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM card_fees_interests WHERE id = ?",
                (fee_interest_id,)
            ).fetchone()

            return CardFeesInterests.from_db_row(row) if row else None

    def get_fees_interests_by_card(self, card_id: int, active_only: bool = True) -> List[CardFeesInterests]:
        """Get all fees/interests for a card"""
        query = "SELECT * FROM card_fees_interests WHERE card_id = ?"
        params = [card_id]

        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY created_at ASC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [CardFeesInterests.from_db_row(row) for row in rows]

    def get_all_fees_interests(self, active_only: bool = True) -> List[CardFeesInterests]:
        """Get all fees/interests"""
        query = "SELECT * FROM card_fees_interests"
        params = []

        if active_only:
            query += " WHERE is_active = 1"

        query += " ORDER BY card_id, created_at ASC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [CardFeesInterests.from_db_row(row) for row in rows]

    def get_fees_by_card(self, card_id: int, active_only: bool = True) -> List[CardFeesInterests]:
        """Get only fees for a card"""
        query = "SELECT * FROM card_fees_interests WHERE card_id = ? AND is_fee = 1"
        params = [card_id]

        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY created_at ASC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [CardFeesInterests.from_db_row(row) for row in rows]

    def get_interests_by_card(self, card_id: int, active_only: bool = True) -> List[CardFeesInterests]:
        """Get only interests for a card"""
        query = "SELECT * FROM card_fees_interests WHERE card_id = ? AND is_fee = 0"
        params = [card_id]

        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY created_at ASC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [CardFeesInterests.from_db_row(row) for row in rows]

    def update_fee_interest(self, fee_interest_id: int, name: str = None, rate: float = None,
                           payment_frequency: str = None, compound_frequency: str = None,
                           is_active: bool = None) -> Optional[CardFeesInterests]:
        """Update card fee/interest"""
        with self._get_connection() as conn:
            # Get existing fee/interest
            existing = conn.execute(
                "SELECT * FROM card_fees_interests WHERE id = ?",
                (fee_interest_id,)
            ).fetchone()

            if not existing:
                return None

            # Prepare update data
            updates = []
            params = []

            if name is not None:
                name = name.strip()
                if not name:
                    raise ValueError("name cannot be empty")

                # Check for duplicate name
                duplicate = conn.execute(
                    "SELECT id FROM card_fees_interests WHERE card_id = ? AND name = ? AND id != ?",
                    (existing['card_id'], name, fee_interest_id)
                ).fetchone()

                if duplicate:
                    raise ValueError(f"Fee/Interest '{name}' already exists for this card")

                updates.append("name = ?")
                params.append(name)

            if rate is not None:
                if rate < 0:
                    raise ValueError("rate must be non-negative")
                updates.append("rate = ?")
                params.append(rate)

            if payment_frequency is not None:
                valid_frequencies = ['daily', 'weekly', 'monthly', 'quarterly', 'annually']
                if payment_frequency not in valid_frequencies:
                    raise ValueError(f"payment_frequency must be one of: {valid_frequencies}")
                updates.append("payment_frequency = ?")
                params.append(payment_frequency)

            if compound_frequency is not None:
                valid_frequencies = [
                    'daily_365', 'daily_360', 'semi_weekly_104', 'weekly_52',
                    'bi_weekly_26', 'semi_monthly_24', 'monthly_12', 'bi_monthly_6',
                    'quarterly_4', 'half_yearly_2', 'yearly_1'
                ]
                if compound_frequency not in valid_frequencies:
                    raise ValueError(f"compound_frequency must be one of: {valid_frequencies}")
                updates.append("compound_frequency = ?")
                params.append(compound_frequency)

            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)

            if not updates:
                # No updates needed, return existing
                return CardFeesInterests.from_db_row(existing)

            # Execute update
            params.append(fee_interest_id)
            conn.execute(
                f"UPDATE card_fees_interests SET {', '.join(updates)} WHERE id = ?",
                params
            )

            # Return updated fee/interest
            updated_row = conn.execute(
                "SELECT * FROM card_fees_interests WHERE id = ?",
                (fee_interest_id,)
            ).fetchone()

            return CardFeesInterests.from_db_row(updated_row)

    def delete_fee_interest(self, fee_interest_id: int) -> bool:
        """Delete card fee/interest"""
        with self._get_connection() as conn:
            # Check if fee/interest exists
            existing = conn.execute(
                "SELECT id FROM card_fees_interests WHERE id = ?",
                (fee_interest_id,)
            ).fetchone()

            if not existing:
                return False

            # Delete fee/interest
            conn.execute(
                "DELETE FROM card_fees_interests WHERE id = ?",
                (fee_interest_id,)
            )

            return True

    def calculate_card_interest_projection(self, card_id: int, principal: float, months: int = 12) -> dict:
        """Calculate interest projection for a card over time"""
        fees_interests = self.get_fees_interests_by_card(card_id, active_only=True)

        if not fees_interests:
            return {
                'card_id': card_id,
                'principal': principal,
                'months': months,
                'total_interest': 0,
                'total_fees': 0,
                'final_amount': principal,
                'breakdown': []
            }

        time_years = months / 12.0
        total_interest = 0
        total_fees = 0
        breakdown = []

        for item in fees_interests:
            amount = item.calculate_compound_amount(principal, time_years)

            if item.is_fee:
                total_fees += abs(amount)  # Fees are negative, make positive for totals
            else:
                total_interest += amount

            breakdown.append({
                'name': item.name,
                'type': 'fee' if item.is_fee else 'interest',
                'rate': item.rate,
                'payment_frequency': item.payment_frequency,
                'compound_frequency': item.compound_frequency,
                'amount': amount,
                'effective_annual_rate': item.calculate_effective_annual_rate()
            })

        return {
            'card_id': card_id,
            'principal': principal,
            'months': months,
            'total_interest': total_interest,
            'total_fees': total_fees,
            'final_amount': principal + total_interest - total_fees,
            'breakdown': breakdown
        }


# Utility functions for external use
def create_card_fee_interest(card_id: int, name: str, rate: float, is_fee: bool = False,
                            payment_frequency: str = 'annually',
                            compound_frequency: str = 'daily_365',
                            db_path: str = "./data/finance.db") -> CardFeesInterests:
    """Utility function to create a card fee or interest"""
    db = CardFeesInterestsDB(db_path)
    return db.create_fee_interest(card_id, name, rate, is_fee, payment_frequency, compound_frequency)


def get_card_fees_interests(card_id: int, db_path: str = "./data/finance.db") -> List[CardFeesInterests]:
    """Utility function to get all fees/interests for a card"""
    db = CardFeesInterestsDB(db_path)
    return db.get_fees_interests_by_card(card_id)