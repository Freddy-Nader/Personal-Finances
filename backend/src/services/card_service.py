#!/usr/bin/env python3
"""
Card service for Personal Finance Management Application.
Provides business logic for card operations.
"""

from typing import List, Optional, Dict, Any
import sys
from pathlib import Path

# Add the backend/src directory to Python path for absolute imports
backend_src_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_src_path))

from models.card import Card


class CardService:
    """Service class for card business logic."""

    @staticmethod
    def create_card(data: Dict[str, Any]) -> Card:
        """Create a new card."""
        # Extract and validate data
        name = data.get('name')
        card_type = data.get('type')
        currency = data.get('currency', 'MXN')  # Default to MXN
        balance = data.get('balance', 0.00)
        credit_limit = data.get('credit_limit')

        # Create card instance
        card = Card(
            name=name,
            type=card_type,
            currency=currency,
            balance=balance,
            credit_limit=credit_limit
        )

        # Validate and save
        return card.save()

    @staticmethod
    def get_card_by_id(card_id: int) -> Optional[Card]:
        """Get a card by ID."""
        try:
            card_id = int(card_id)
        except (ValueError, TypeError):
            raise ValueError("Invalid card ID format")

        return Card.find_by_id(card_id)

    @staticmethod
    def get_all_cards() -> List[Card]:
        """Get all cards."""
        return Card.find_all()

    @staticmethod
    def get_cards_by_type(card_type: str) -> List[Card]:
        """Get cards by type (credit/debit)."""
        if card_type not in ['credit', 'debit']:
            raise ValueError("Card type must be 'credit' or 'debit'")

        return Card.find_by_type(card_type)

    @staticmethod
    def update_card(card_id: int, data: Dict[str, Any]) -> Card:
        """Update an existing card."""
        try:
            card_id = int(card_id)
        except (ValueError, TypeError):
            raise ValueError("Invalid card ID format")

        # Find existing card
        card = Card.find_by_id(card_id)
        if not card:
            raise ValueError(f"Card with ID {card_id} not found")

        # Update allowed fields
        if 'name' in data:
            card.name = data['name']
        if 'balance' in data:
            card.balance = data['balance']
        if 'credit_limit' in data:
            card.credit_limit = data['credit_limit']

        # Save updated card
        return card.save()

    @staticmethod
    def delete_card(card_id: int) -> bool:
        """Delete a card."""
        try:
            card_id = int(card_id)
        except (ValueError, TypeError):
            raise ValueError("Invalid card ID format")

        # Find existing card
        card = Card.find_by_id(card_id)
        if not card:
            raise ValueError(f"Card with ID {card_id} not found")

        # Check for dependent data (transactions, sections)
        # This is a business rule - you might want to prevent deletion
        # if there are related transactions or sections
        card.delete()
        return True

    @staticmethod
    def get_card_summary() -> Dict[str, Any]:
        """Get summary statistics for all cards."""
        cards = Card.find_all()

        total_balance = 0
        total_credit_available = 0
        debit_cards = []
        credit_cards = []

        for card in cards:
            if card.type == 'debit':
                debit_cards.append(card)
                total_balance += float(card.balance)
            elif card.type == 'credit':
                credit_cards.append(card)
                if card.credit_limit and card.balance:
                    available_credit = float(card.credit_limit) - float(card.balance)
                    total_credit_available += max(0, available_credit)

        return {
            'total_cards': len(cards),
            'total_balance': total_balance,
            'total_credit_available': total_credit_available,
            'debit_cards_count': len(debit_cards),
            'credit_cards_count': len(credit_cards),
            'cards': [card.to_dict() for card in cards]
        }

    @staticmethod
    def validate_card_data(data: Dict[str, Any], is_update: bool = False) -> List[str]:
        """Validate card data and return list of errors."""
        errors = []

        if not is_update:
            # Required fields for creation
            if not data.get('name'):
                errors.append("Card name is required")
            if not data.get('type'):
                errors.append("Card type is required")

        # Validate type if provided
        if 'type' in data and data['type'] not in ['credit', 'debit']:
            errors.append("Card type must be 'credit' or 'debit'")

        # Validate numeric fields
        if 'balance' in data:
            try:
                float(data['balance'])
            except (ValueError, TypeError):
                errors.append("Balance must be a number")

        if 'credit_limit' in data and data['credit_limit'] is not None:
            try:
                credit_limit = float(data['credit_limit'])
                if credit_limit < 0:
                    errors.append("Credit limit cannot be negative")
            except (ValueError, TypeError):
                errors.append("Credit limit must be a number")

        # Business rule validations
        if data.get('type') == 'debit' and data.get('credit_limit') is not None:
            errors.append("Debit cards should not have a credit limit")

        return errors

    @staticmethod
    def calculate_net_worth() -> Dict[str, float]:
        """Calculate net worth from all cards."""
        cards = Card.find_all()

        total_assets = 0
        total_liabilities = 0

        for card in cards:
            if card.type == 'debit':
                # Debit card balance is an asset
                total_assets += float(card.balance)
            elif card.type == 'credit':
                # Credit card balance is a liability
                total_liabilities += float(card.balance)

        net_worth = total_assets - total_liabilities

        return {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'net_worth': net_worth
        }