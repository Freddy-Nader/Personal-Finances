#!/usr/bin/env python3
"""
Database initialization script for Personal Finance Management Application.
Creates SQLite database with schema from data-model.md.
"""

import sqlite3
import os
from pathlib import Path


def get_database_path():
    """Get database path from environment or default."""
    try:
        # Try to load from .env file
        env_path = Path(__file__).parent.parent.parent.parent / '.env'
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith('DATABASE_PATH='):
                        return line.split('=', 1)[1].strip()
    except Exception:
        pass

    # Default path
    return './data/finance.db'


def create_database_schema(db_path):
    """Create database schema with all tables and indexes."""

    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Cards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('credit', 'debit')),
                currency TEXT NOT NULL DEFAULT 'MXN',
                balance DECIMAL(15,2) DEFAULT 0.00,
                credit_limit DECIMAL(15,2) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Sections table (user requirement)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                initial_balance DECIMAL(15,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
                UNIQUE(card_id, name)
            )
        ''')

        # Transactions table with internal transfer support
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount DECIMAL(15,2) NOT NULL,
                description TEXT NOT NULL,
                transaction_date TIMESTAMP NOT NULL,
                card_id INTEGER NULL,
                section_id INTEGER NULL,
                category TEXT NULL,
                is_internal_transfer BOOLEAN DEFAULT FALSE,
                transfer_from_type TEXT NULL CHECK (transfer_from_type IN ('card', 'cash', 'stock', 'crypto')),
                transfer_from_id INTEGER NULL,
                transfer_to_type TEXT NULL CHECK (transfer_to_type IN ('card', 'cash', 'stock', 'crypto')),
                transfer_to_id INTEGER NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards(id),
                FOREIGN KEY (section_id) REFERENCES sections(id)
            )
        ''')

        # Investment positions (simplified - no stored prices)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investment_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_type TEXT NOT NULL CHECK (asset_type IN ('stock', 'crypto')),
                symbol TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(asset_type, symbol)
            )
        ''')

        # Investment movements with exact timing and price redundancy
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id INTEGER NOT NULL,
                movement_type TEXT NOT NULL CHECK (movement_type IN ('buy', 'sell')),
                quantity DECIMAL(18,8) NOT NULL,
                price_per_unit DECIMAL(15,2) NOT NULL,
                total_amount DECIMAL(15,2) NOT NULL,
                movement_datetime TIMESTAMP NOT NULL,
                description TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (position_id) REFERENCES investment_positions(id)
            )
        ''')

        # Card interests and fees with detailed compounding
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS card_fees_interests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                rate DECIMAL(8,4) NOT NULL,
                is_fee BOOLEAN DEFAULT FALSE,
                payment_frequency TEXT NOT NULL DEFAULT 'annually'
                    CHECK (payment_frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'annually')),
                compound_frequency TEXT NOT NULL DEFAULT 'daily_365'
                    CHECK (compound_frequency IN ('daily_365', 'daily_360', 'semi_weekly_104', 'weekly_52', 'bi_weekly_26', 'semi_monthly_24', 'monthly_12', 'bi_monthly_6', 'quarterly_4', 'half_yearly_2', 'yearly_1')),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
            )
        ''')

        # Indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_card ON transactions(card_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_movements_position ON movements(position_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_movements_datetime ON movements(movement_datetime)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sections_card ON sections(card_id)')

        conn.commit()
        print(f"Database schema created successfully at: {db_path}")

        # Print table info for verification
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Created tables: {[table[0] for table in tables]}")

    except Exception as e:
        conn.rollback()
        print(f"Error creating database schema: {e}")
        raise
    finally:
        conn.close()


def main():
    """Main function to initialize database."""
    db_path = get_database_path()
    print(f"Initializing database at: {db_path}")
    create_database_schema(db_path)


if __name__ == '__main__':
    main()