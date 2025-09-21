#!/usr/bin/env python3
"""
Investment Position Model
Represents asset holdings (stocks or crypto) - simplified to track only basic info.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class InvestmentPosition:
    """Investment Position data model"""
    id: Optional[int]
    asset_type: str  # 'stock' or 'crypto'
    symbol: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def __post_init__(self):
        """Validate investment position data after initialization"""
        if self.asset_type not in ['stock', 'crypto']:
            raise ValueError("asset_type must be either 'stock' or 'crypto'")

        if not self.symbol or not self.symbol.strip():
            raise ValueError("symbol cannot be empty")

        # Normalize symbol to uppercase
        self.symbol = self.symbol.strip().upper()

    @classmethod
    def from_db_row(cls, row) -> 'InvestmentPosition':
        """Create InvestmentPosition from database row"""
        return cls(
            id=row[0],
            asset_type=row[1],
            symbol=row[2],
            created_at=datetime.fromisoformat(row[3]) if row[3] else None,
            updated_at=datetime.fromisoformat(row[4]) if row[4] else None
        )

    def to_dict(self) -> dict:
        """Convert investment position to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'asset_type': self.asset_type,
            'symbol': self.symbol,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class InvestmentPositionDB:
    """Database operations for Investment Positions"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_position(self, asset_type: str, symbol: str) -> InvestmentPosition:
        """Create a new investment position"""
        # Validate and normalize inputs
        position = InvestmentPosition(
            id=None,
            asset_type=asset_type,
            symbol=symbol,
            created_at=None,
            updated_at=None
        )

        with self._get_connection() as conn:
            # Check for duplicate position
            existing = conn.execute(
                "SELECT id FROM investment_positions WHERE asset_type = ? AND symbol = ?",
                (position.asset_type, position.symbol)
            ).fetchone()

            if existing:
                raise ValueError(f"Position for {position.asset_type} {position.symbol} already exists")

            # Insert new position
            cursor = conn.execute(
                """
                INSERT INTO investment_positions (asset_type, symbol, created_at, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (position.asset_type, position.symbol)
            )

            # Get the created position
            position_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM investment_positions WHERE id = ?",
                (position_id,)
            ).fetchone()

            return InvestmentPosition.from_db_row(row)

    def get_position(self, position_id: int) -> Optional[InvestmentPosition]:
        """Get investment position by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM investment_positions WHERE id = ?",
                (position_id,)
            ).fetchone()

            return InvestmentPosition.from_db_row(row) if row else None

    def get_position_by_symbol(self, asset_type: str, symbol: str) -> Optional[InvestmentPosition]:
        """Get investment position by asset type and symbol"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM investment_positions WHERE asset_type = ? AND symbol = ?",
                (asset_type, symbol.upper())
            ).fetchone()

            return InvestmentPosition.from_db_row(row) if row else None

    def get_all_positions(self) -> List[InvestmentPosition]:
        """Get all investment positions"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM investment_positions ORDER BY created_at DESC"
            ).fetchall()

            return [InvestmentPosition.from_db_row(row) for row in rows]

    def get_positions_by_type(self, asset_type: str) -> List[InvestmentPosition]:
        """Get investment positions by asset type"""
        if asset_type not in ['stock', 'crypto']:
            raise ValueError("asset_type must be either 'stock' or 'crypto'")

        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM investment_positions WHERE asset_type = ? ORDER BY symbol",
                (asset_type,)
            ).fetchall()

            return [InvestmentPosition.from_db_row(row) for row in rows]

    def update_position(self, position_id: int, symbol: str = None) -> Optional[InvestmentPosition]:
        """Update investment position (only symbol can be updated)"""
        with self._get_connection() as conn:
            # Check if position exists
            existing = conn.execute(
                "SELECT * FROM investment_positions WHERE id = ?",
                (position_id,)
            ).fetchone()

            if not existing:
                return None

            # Prepare update data
            updates = []
            params = []

            if symbol is not None:
                # Validate and normalize symbol
                symbol = symbol.strip().upper()
                if not symbol:
                    raise ValueError("symbol cannot be empty")

                # Check for duplicate symbol with same asset type
                duplicate = conn.execute(
                    "SELECT id FROM investment_positions WHERE asset_type = ? AND symbol = ? AND id != ?",
                    (existing[1], symbol, position_id)
                ).fetchone()

                if duplicate:
                    raise ValueError(f"Position for {existing[1]} {symbol} already exists")

                updates.append("symbol = ?")
                params.append(symbol)

            if not updates:
                # No updates needed, return existing
                return InvestmentPosition.from_db_row(existing)

            # Add updated_at
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(position_id)

            # Execute update
            conn.execute(
                f"UPDATE investment_positions SET {', '.join(updates)} WHERE id = ?",
                params
            )

            # Return updated position
            updated_row = conn.execute(
                "SELECT * FROM investment_positions WHERE id = ?",
                (position_id,)
            ).fetchone()

            return InvestmentPosition.from_db_row(updated_row)

    def delete_position(self, position_id: int) -> bool:
        """Delete investment position and all associated movements"""
        with self._get_connection() as conn:
            # Check if position exists
            existing = conn.execute(
                "SELECT id FROM investment_positions WHERE id = ?",
                (position_id,)
            ).fetchone()

            if not existing:
                return False

            # Delete associated movements first (foreign key constraint)
            conn.execute(
                "DELETE FROM movements WHERE position_id = ?",
                (position_id,)
            )

            # Delete position
            conn.execute(
                "DELETE FROM investment_positions WHERE id = ?",
                (position_id,)
            )

            return True

    def get_position_summary(self, position_id: int) -> Optional[dict]:
        """Get position summary with current holdings calculated from movements"""
        position = self.get_position(position_id)
        if not position:
            return None

        with self._get_connection() as conn:
            # Calculate current holdings from movements
            movements = conn.execute(
                """
                SELECT movement_type, SUM(quantity) as total_quantity,
                       AVG(price_per_unit) as avg_price, SUM(total_amount) as total_amount
                FROM movements
                WHERE position_id = ?
                GROUP BY movement_type
                """,
                (position_id,)
            ).fetchall()

            total_quantity = 0
            total_cost = 0
            total_proceeds = 0

            for movement in movements:
                if movement['movement_type'] == 'buy':
                    total_quantity += movement['total_quantity']
                    total_cost += movement['total_amount']
                elif movement['movement_type'] == 'sell':
                    total_quantity -= movement['total_quantity']
                    total_proceeds += movement['total_amount']

            # Calculate average cost basis for remaining shares
            cost_basis = total_cost / total_quantity if total_quantity > 0 else 0

            return {
                'position': position.to_dict(),
                'current_quantity': max(0, total_quantity),  # Can't have negative holdings
                'cost_basis': cost_basis,
                'total_invested': total_cost,
                'total_proceeds': total_proceeds,
                'realized_pnl': total_proceeds - (total_cost * (total_proceeds / total_cost) if total_cost > 0 else 0)
            }


# Utility functions for external use
def create_investment_position(asset_type: str, symbol: str, db_path: str = "./data/finance.db") -> InvestmentPosition:
    """Utility function to create an investment position"""
    db = InvestmentPositionDB(db_path)
    return db.create_position(asset_type, symbol)


def get_investment_position(position_id: int, db_path: str = "./data/finance.db") -> Optional[InvestmentPosition]:
    """Utility function to get an investment position by ID"""
    db = InvestmentPositionDB(db_path)
    return db.get_position(position_id)


def get_all_investment_positions(db_path: str = "./data/finance.db") -> List[InvestmentPosition]:
    """Utility function to get all investment positions"""
    db = InvestmentPositionDB(db_path)
    return db.get_all_positions()