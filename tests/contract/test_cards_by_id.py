#!/usr/bin/env python3
"""
Contract test for GET /api/cards/{cardId} endpoint.
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


class TestCardsByIdGetContract(unittest.TestCase):
    """Test contract for GET /api/cards/{cardId} endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_url = f"{self.BASE_URL}/api/cards"

    def test_get_card_by_id_existing_card(self):
        """Test GET /api/cards/{cardId} with existing card returns 200."""
        card_id = 1  # Assume card with ID 1 exists

        try:
            with urllib.request.urlopen(f"{self.api_url}/{card_id}") as response:
                self.assertEqual(response.getcode(), 200)

                # Check response content
                response_data = json.loads(response.read().decode('utf-8'))
                self.assertIsInstance(response_data, dict)

                # Validate card structure
                required_fields = {'id', 'name', 'type', 'currency'}
                actual_fields = set(response_data.keys())
                self.assertTrue(required_fields.issubset(actual_fields),
                              f"Missing required fields: {required_fields - actual_fields}")

                # Validate field types
                self.assertEqual(response_data['id'], card_id)
                self.assertIsInstance(response_data['name'], str)
                self.assertIn(response_data['type'], ['credit', 'debit'])
                self.assertIsInstance(response_data['currency'], str)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_card_by_id_nonexistent_card(self):
        """Test GET /api/cards/{cardId} with nonexistent card returns 404."""
        nonexistent_id = 99999

        try:
            with urllib.request.urlopen(f"{self.api_url}/{nonexistent_id}") as response:
                self.fail("Expected 404 error for nonexistent card")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_get_card_by_id_invalid_id_format(self):
        """Test GET /api/cards/{cardId} with invalid ID format returns 400."""
        invalid_id = "not_a_number"

        try:
            with urllib.request.urlopen(f"{self.api_url}/{invalid_id}") as response:
                self.fail("Expected 400 error for invalid ID format")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_get_card_by_id_returns_json(self):
        """Test that GET /api/cards/{cardId} returns JSON content type."""
        card_id = 1

        try:
            with urllib.request.urlopen(f"{self.api_url}/{card_id}") as response:
                content_type = response.headers.get('Content-Type', '')
                self.assertIn('application/json', content_type)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_card_by_id_includes_timestamps(self):
        """Test GET /api/cards/{cardId} includes created_at and updated_at."""
        card_id = 1

        try:
            with urllib.request.urlopen(f"{self.api_url}/{card_id}") as response:
                response_data = json.loads(response.read().decode('utf-8'))

                self.assertIn('created_at', response_data)
                self.assertIn('updated_at', response_data)
                self.assertIsInstance(response_data['created_at'], str)
                self.assertIsInstance(response_data['updated_at'], str)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_card_by_id_debit_card_structure(self):
        """Test GET /api/cards/{cardId} for debit card has balance field."""
        # This test assumes we can identify a debit card (ID 1 for example)
        card_id = 1

        try:
            with urllib.request.urlopen(f"{self.api_url}/{card_id}") as response:
                response_data = json.loads(response.read().decode('utf-8'))

                if response_data.get('type') == 'debit':
                    self.assertIn('balance', response_data)
                    self.assertIsInstance(response_data['balance'], (int, float))

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_card_by_id_credit_card_structure(self):
        """Test GET /api/cards/{cardId} for credit card has credit_limit field."""
        # This test assumes we can identify a credit card
        card_id = 2  # Assume card with ID 2 is a credit card

        try:
            with urllib.request.urlopen(f"{self.api_url}/{card_id}") as response:
                response_data = json.loads(response.read().decode('utf-8'))

                if response_data.get('type') == 'credit':
                    # Credit limit can be null or a number
                    credit_limit = response_data.get('credit_limit')
                    self.assertTrue(credit_limit is None or isinstance(credit_limit, (int, float)))

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    print("Testing GET /api/cards/{cardId} contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)