#!/usr/bin/env python3
"""
Contract test for GET /api/cards endpoint.
This test MUST FAIL until the endpoint is implemented.
"""

import unittest
import json
import urllib.request
import urllib.error
from pathlib import Path
import sys

# Add backend path to sys.path for imports
backend_path = Path(__file__).parent.parent.parent / 'backend' / 'src'
sys.path.insert(0, str(backend_path))


class TestCardsGetContract(unittest.TestCase):
    """Test contract for GET /api/cards endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_url = f"{self.BASE_URL}/api/cards"

    def test_get_cards_returns_200(self):
        """Test that GET /api/cards returns 200 status code."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                self.assertEqual(response.getcode(), 200)
        except urllib.error.HTTPError as e:
            self.fail(f"Expected 200, got {e.code}: {e.reason}")
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_cards_returns_json(self):
        """Test that GET /api/cards returns JSON content type."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                content_type = response.headers.get('Content-Type', '')
                self.assertIn('application/json', content_type)
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_cards_returns_array(self):
        """Test that GET /api/cards returns an array of cards."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))
                self.assertIsInstance(data, list, "Response should be an array")
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_cards_empty_response_structure(self):
        """Test structure of response when no cards exist."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))
                # Should be empty array initially
                self.assertEqual(data, [])
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_cards_with_data_structure(self):
        """Test structure of response when cards exist (contract validation)."""
        # This test validates the contract structure
        # It will pass once the endpoint returns proper card objects
        expected_card_fields = {
            'id', 'name', 'type', 'currency', 'balance',
            'credit_limit', 'created_at', 'updated_at'
        }

        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))

                if len(data) > 0:
                    # Validate first card structure
                    card = data[0]
                    actual_fields = set(card.keys())

                    # Check required fields exist
                    required_fields = {'id', 'name', 'type', 'currency'}
                    self.assertTrue(required_fields.issubset(actual_fields),
                                  f"Missing required fields: {required_fields - actual_fields}")

                    # Check type field values
                    self.assertIn(card['type'], ['credit', 'debit'],
                                f"Invalid card type: {card['type']}")

                    # Check currency field (should default to MXN)
                    self.assertIsInstance(card['currency'], str)

                    # Check numeric fields
                    if 'balance' in card:
                        self.assertIsInstance(card['balance'], (int, float))
                    if 'credit_limit' in card:
                        self.assertTrue(card['credit_limit'] is None or
                                      isinstance(card['credit_limit'], (int, float)))

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    # Print test information
    print("Testing GET /api/cards contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)