#!/usr/bin/env python3
"""
Contract test for POST /api/cards endpoint.
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


class TestCardsPostContract(unittest.TestCase):
    """Test contract for POST /api/cards endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_url = f"{self.BASE_URL}/api/cards"

    def _make_post_request(self, data):
        """Helper to make POST request with JSON data."""
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            self.api_url,
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        req.get_method = lambda: 'POST'
        return urllib.request.urlopen(req)

    def test_post_cards_valid_debit_card(self):
        """Test POST /api/cards with valid debit card data."""
        card_data = {
            'name': 'Test Debit Card',
            'type': 'debit',
            'currency': 'MXN',
            'balance': 1000.00
        }

        try:
            with self._make_post_request(card_data) as response:
                self.assertEqual(response.getcode(), 201)

                # Check response content
                response_data = json.loads(response.read().decode('utf-8'))
                self.assertIsInstance(response_data, dict)

                # Validate response structure
                self.assertIn('id', response_data)
                self.assertEqual(response_data['name'], card_data['name'])
                self.assertEqual(response_data['type'], card_data['type'])
                self.assertEqual(response_data['currency'], card_data['currency'])
                self.assertEqual(response_data['balance'], card_data['balance'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_cards_valid_credit_card(self):
        """Test POST /api/cards with valid credit card data."""
        card_data = {
            'name': 'Test Credit Card',
            'type': 'credit',
            'currency': 'MXN',
            'credit_limit': 5000.00
        }

        try:
            with self._make_post_request(card_data) as response:
                self.assertEqual(response.getcode(), 201)

                response_data = json.loads(response.read().decode('utf-8'))
                self.assertEqual(response_data['name'], card_data['name'])
                self.assertEqual(response_data['type'], card_data['type'])
                self.assertEqual(response_data['credit_limit'], card_data['credit_limit'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_cards_default_currency(self):
        """Test POST /api/cards defaults to MXN currency."""
        card_data = {
            'name': 'Default Currency Card',
            'type': 'debit'
        }

        try:
            with self._make_post_request(card_data) as response:
                self.assertEqual(response.getcode(), 201)

                response_data = json.loads(response.read().decode('utf-8'))
                self.assertEqual(response_data['currency'], 'MXN')

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_cards_missing_required_fields(self):
        """Test POST /api/cards with missing required fields returns 400."""
        invalid_data = {
            'name': 'Incomplete Card'
            # Missing 'type' field
        }

        try:
            with self._make_post_request(invalid_data) as response:
                self.fail("Expected 400 error for missing required fields")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_post_cards_invalid_type(self):
        """Test POST /api/cards with invalid card type returns 400."""
        invalid_data = {
            'name': 'Invalid Type Card',
            'type': 'invalid_type'
        }

        try:
            with self._make_post_request(invalid_data) as response:
                self.fail("Expected 400 error for invalid card type")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_post_cards_response_has_timestamps(self):
        """Test POST /api/cards response includes created_at and updated_at."""
        card_data = {
            'name': 'Timestamp Test Card',
            'type': 'debit'
        }

        try:
            with self._make_post_request(card_data) as response:
                response_data = json.loads(response.read().decode('utf-8'))

                self.assertIn('created_at', response_data)
                self.assertIn('updated_at', response_data)
                self.assertIsInstance(response_data['created_at'], str)
                self.assertIsInstance(response_data['updated_at'], str)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_cards_returns_json(self):
        """Test that POST /api/cards returns JSON content type."""
        card_data = {
            'name': 'JSON Test Card',
            'type': 'debit'
        }

        try:
            with self._make_post_request(card_data) as response:
                content_type = response.headers.get('Content-Type', '')
                self.assertIn('application/json', content_type)

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    print("Testing POST /api/cards contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)