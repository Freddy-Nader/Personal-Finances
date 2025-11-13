#!/usr/bin/env python3
"""
Quick test of API functionality
"""

import sys
import os
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

try:
    from services.card_service import CardService
    print("✅ CardService import successful")

    # Test creating a card
    card_data = {
        'name': 'Test Card',
        'type': 'debit',
        'currency': 'MXN',
        'balance': 1000.00
    }

    card = CardService.create_card(card_data)
    print(f"✅ Card creation successful: {card}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()