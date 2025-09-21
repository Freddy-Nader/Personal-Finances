#!/usr/bin/env python3
"""
Movement Model
Represents buy/sell transactions for stocks and cryptocurrencies with exact timing.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


@dataclass
class Movement:
    """Movement data model"""
    id: Optional[int]
    position_id: int
    movement_type: str  # 'buy' or 'sell'
    quantity: float
    price_per_unit: float
    total_amount: float
    movement_datetime: datetime
    description: Optional[str]
    created_at: Optional[datetime]

    def __post_init__(self):
        """Validate movement data after initialization"""
        if self.movement_type not in ['buy', 'sell']:
            raise ValueError("movement_type must be either 'buy' or 'sell'")

        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

        if self.price_per_unit <= 0:
            raise ValueError("price_per_unit must be positive")

        # Validate total_amount calculation
        expected_total = self.quantity * self.price_per_unit
        if abs(self.total_amount - expected_total) > 0.01:  # Allow small floating point differences
            raise ValueError(f"total_amount ({self.total_amount}) must equal quantity * price_per_unit ({expected_total})")

        # Ensure total_amount is calculated correctly
        self.total_amount = round(self.quantity * self.price_per_unit, 2)

    @classmethod
    def from_db_row(cls, row) -> 'Movement':
        """Create Movement from database row"""
        return cls(
            id=row[0],
            position_id=row[1],
            movement_type=row[2],
            quantity=float(row[3]),
            price_per_unit=float(row[4]),
            total_amount=float(row[5]),
            movement_datetime=datetime.fromisoformat(row[6]),
            description=row[7],
            created_at=datetime.fromisoformat(row[8]) if row[8] else None
        )

    def to_dict(self) -> dict:
        """Convert movement to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'position_id': self.position_id,
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'price_per_unit': self.price_per_unit,
            'total_amount': self.total_amount,
            'movement_datetime': self.movement_datetime.isoformat(),
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MovementDB:
    """Database operations for Movements"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_movement(self, position_id: int, movement_type: str, quantity: float,
                       price_per_unit: float, movement_datetime: datetime,
                       description: str = None) -> Movement:
        """Create a new movement"""
        # Create and validate movement
        movement = Movement(
            id=None,
            position_id=position_id,
            movement_type=movement_type,
            quantity=quantity,
            price_per_unit=price_per_unit,
            total_amount=quantity * price_per_unit,  # Will be recalculated in __post_init__
            movement_datetime=movement_datetime,
            description=description,
            created_at=None
        )

        with self._get_connection() as conn:
            # Verify position exists
            position_exists = conn.execute(
                "SELECT id FROM investment_positions WHERE id = ?",
                (position_id,)
            ).fetchone()

            if not position_exists:
                raise ValueError(f"Investment position {position_id} does not exist")

            # For sell movements, verify sufficient quantity is available
            if movement_type == 'sell':
                current_holdings = self._calculate_current_holdings(conn, position_id)
                if current_holdings < quantity:
                    raise ValueError(f"Insufficient holdings: trying to sell {quantity}, but only {current_holdings} available")

            # Insert movement
            cursor = conn.execute(
                """
                INSERT INTO movements
                (position_id, movement_type, quantity, price_per_unit, total_amount, movement_datetime, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (movement.position_id, movement.movement_type, movement.quantity,
                 movement.price_per_unit, movement.total_amount, movement.movement_datetime.isoformat(),
                 movement.description)
            )

            # Get the created movement
            movement_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM movements WHERE id = ?",
                (movement_id,)
            ).fetchone()

            return Movement.from_db_row(row)

    def _calculate_current_holdings(self, conn: sqlite3.Connection, position_id: int) -> float:
        """Calculate current holdings for a position"""
        result = conn.execute(
            """
            SELECT
                SUM(CASE WHEN movement_type = 'buy' THEN quantity ELSE 0 END) as total_bought,
                SUM(CASE WHEN movement_type = 'sell' THEN quantity ELSE 0 END) as total_sold
            FROM movements
            WHERE position_id = ?
            """,
            (position_id,)
        ).fetchone()

        total_bought = result['total_bought'] or 0
        total_sold = result['total_sold'] or 0

        return max(0, total_bought - total_sold)

    def get_movement(self, movement_id: int) -> Optional[Movement]:
        """Get movement by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM movements WHERE id = ?",
                (movement_id,)
            ).fetchone()

            return Movement.from_db_row(row) if row else None

    def get_movements_by_position(self, position_id: int) -> List[Movement]:
        """Get all movements for a position"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM movements WHERE position_id = ? ORDER BY movement_datetime DESC, created_at DESC",
                (position_id,)
            ).fetchall()

            return [Movement.from_db_row(row) for row in rows]

    def get_all_movements(self) -> List[Movement]:
        """Get all movements"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM movements ORDER BY movement_datetime DESC, created_at DESC"
            ).fetchall()

            return [Movement.from_db_row(row) for row in rows]

    def get_movements_by_date_range(self, start_date: datetime = None,
                                   end_date: datetime = None,
                                   position_id: int = None) -> List[Movement]:
        """Get movements filtered by date range and optionally by position"""
        query = "SELECT * FROM movements WHERE 1=1"
        params = []

        if start_date:
            query += " AND movement_datetime >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND movement_datetime <= ?"
            params.append(end_date.isoformat())

        if position_id:
            query += " AND position_id = ?"
            params.append(position_id)

        query += " ORDER BY movement_datetime DESC, created_at DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [Movement.from_db_row(row) for row in rows]

    def get_movements_by_type(self, movement_type: str, position_id: int = None) -> List[Movement]:
        """Get movements by type (buy/sell) and optionally by position"""
        if movement_type not in ['buy', 'sell']:
            raise ValueError("movement_type must be either 'buy' or 'sell'")

        query = "SELECT * FROM movements WHERE movement_type = ?"
        params = [movement_type]

        if position_id:
            query += " AND position_id = ?"
            params.append(position_id)

        query += " ORDER BY movement_datetime DESC, created_at DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [Movement.from_db_row(row) for row in rows]

    def update_movement(self, movement_id: int, quantity: float = None,
                       price_per_unit: float = None, movement_datetime: datetime = None,
                       description: str = None) -> Optional[Movement]:
        """Update movement (limited fields to maintain data integrity)"""
        with self._get_connection() as conn:
            # Get existing movement
            existing = conn.execute(
                "SELECT * FROM movements WHERE id = ?",
                (movement_id,)
            ).fetchone()

            if not existing:
                return None

            # Prepare update data
            updates = []
            params = []

            if quantity is not None:
                if quantity <= 0:
                    raise ValueError("quantity must be positive")

                # For sell movements, verify sufficient holdings
                if existing['movement_type'] == 'sell':
                    # Calculate holdings excluding this movement
                    other_holdings = self._calculate_current_holdings(conn, existing['position_id'])
                    other_holdings += existing['quantity']  # Add back the original quantity

                    if other_holdings < quantity:
                        raise ValueError(f"Insufficient holdings for update: trying to sell {quantity}, but only {other_holdings} available")

                updates.append("quantity = ?")
                params.append(quantity)

                # Recalculate total_amount if quantity changes
                new_price = price_per_unit if price_per_unit is not None else existing['price_per_unit']
                new_total = quantity * new_price
                updates.append("total_amount = ?")
                params.append(new_total)

            if price_per_unit is not None:
                if price_per_unit <= 0:
                    raise ValueError("price_per_unit must be positive")

                updates.append("price_per_unit = ?")
                params.append(price_per_unit)

                # Recalculate total_amount if price changes
                new_quantity = quantity if quantity is not None else existing['quantity']
                new_total = new_quantity * price_per_unit
                updates.append("total_amount = ?")
                params.append(new_total)

            if movement_datetime is not None:
                updates.append("movement_datetime = ?")
                params.append(movement_datetime.isoformat())

            if description is not None:
                updates.append("description = ?")
                params.append(description)

            if not updates:
                # No updates needed, return existing
                return Movement.from_db_row(existing)

            # Execute update
            params.append(movement_id)
            conn.execute(
                f"UPDATE movements SET {', '.join(updates)} WHERE id = ?",
                params
            )

            # Return updated movement
            updated_row = conn.execute(
                "SELECT * FROM movements WHERE id = ?",
                (movement_id,)
            ).fetchone()

            return Movement.from_db_row(updated_row)

    def delete_movement(self, movement_id: int) -> bool:
        """Delete movement"""
        with self._get_connection() as conn:
            # Check if movement exists
            existing = conn.execute(
                "SELECT id FROM movements WHERE id = ?",
                (movement_id,)
            ).fetchone()

            if not existing:
                return False

            # Delete movement
            conn.execute(
                "DELETE FROM movements WHERE id = ?",
                (movement_id,)
            )

            return True

    def get_position_holdings(self, position_id: int) -> dict:
        """Get current holdings summary for a position"""
        with self._get_connection() as conn:
            # Get all movements for the position
            movements = conn.execute(
                """
                SELECT movement_type, quantity, price_per_unit, total_amount, movement_datetime
                FROM movements
                WHERE position_id = ?
                ORDER BY movement_datetime ASC
                """,
                (position_id,)
            ).fetchall()

            total_quantity = 0
            total_cost = 0
            total_proceeds = 0
            fifo_cost_basis = 0
            fifo_lots = []  # For FIFO cost basis calculation

            for movement in movements:
                if movement['movement_type'] == 'buy':
                    total_quantity += movement['quantity']
                    total_cost += movement['total_amount']
                    # Add to FIFO lots
                    fifo_lots.append({
                        'quantity': movement['quantity'],
                        'price': movement['price_per_unit'],
                        'remaining': movement['quantity']
                    })
                elif movement['movement_type'] == 'sell':
                    total_quantity -= movement['quantity']
                    total_proceeds += movement['total_amount']

                    # Calculate FIFO cost for sold shares
                    shares_to_sell = movement['quantity']
                    while shares_to_sell > 0 and fifo_lots:
                        lot = fifo_lots[0]
                        if lot['remaining'] <= shares_to_sell:
                            # Use entire lot
                            shares_to_sell -= lot['remaining']
                            fifo_lots.pop(0)
                        else:
                            # Use partial lot
                            lot['remaining'] -= shares_to_sell
                            shares_to_sell = 0

            # Calculate weighted average cost basis for remaining shares
            if fifo_lots and total_quantity > 0:
                fifo_cost_basis = sum(lot['remaining'] * lot['price'] for lot in fifo_lots) / total_quantity

            return {
                'position_id': position_id,
                'current_quantity': max(0, total_quantity),
                'total_cost': total_cost,
                'total_proceeds': total_proceeds,
                'average_cost_basis': fifo_cost_basis,
                'realized_pnl': total_proceeds - (total_cost - sum(lot['remaining'] * lot['price'] for lot in fifo_lots)),
                'fifo_lots': fifo_lots
            }


# Utility functions for external use
def create_movement(position_id: int, movement_type: str, quantity: float,
                   price_per_unit: float, movement_datetime: datetime,
                   description: str = None, db_path: str = "./data/finance.db") -> Movement:
    """Utility function to create a movement"""
    db = MovementDB(db_path)
    return db.create_movement(position_id, movement_type, quantity, price_per_unit,
                             movement_datetime, description)


def get_movement(movement_id: int, db_path: str = "./data/finance.db") -> Optional[Movement]:
    """Utility function to get a movement by ID"""
    db = MovementDB(db_path)
    return db.get_movement(movement_id)


def get_all_movements(db_path: str = "./data/finance.db") -> List[Movement]:
    """Utility function to get all movements"""
    db = MovementDB(db_path)
    return db.get_all_movements()