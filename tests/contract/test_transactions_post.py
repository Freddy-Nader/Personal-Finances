#!/usr/bin/env python3
"""
Contract test for POST /api/transactions endpoint.
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


class TestTransactionsPostContract(unittest.TestCase):
    """Test contract for POST /api/transactions endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_url = f"{self.BASE_URL}/api/transactions"

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

    def test_post_transaction_basic_expense(self):
        """Test POST /api/transactions with basic expense transaction."""
        transaction_data = {
            'amount': -50.00,
            'description': 'Grocery shopping',
            'transaction_date': '2024-09-20T10:30:00Z',
            'card_id': 1,
            'category': 'Food'
        }

        try:
            with self._make_post_request(transaction_data) as response:
                self.assertEqual(response.getcode(), 201)

                response_data = json.loads(response.read().decode('utf-8'))
                self.assertIsInstance(response_data, dict)
                self.assertIn('id', response_data)
                self.assertEqual(response_data['amount'], transaction_data['amount'])
                self.assertEqual(response_data['description'], transaction_data['description'])
                self.assertEqual(response_data['card_id'], transaction_data['card_id'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_transaction_basic_income(self):
        """Test POST /api/transactions with income transaction."""
        transaction_data = {
            'amount': 2500.00,
            'description': 'Salary deposit',
            'transaction_date': '2024-09-20T09:00:00Z',
            'card_id': 1
        }

        try:
            with self._make_post_request(transaction_data) as response:
                self.assertEqual(response.getcode(), 201)

                response_data = json.loads(response.read().decode('utf-8'))
                self.assertEqual(response_data['amount'], transaction_data['amount'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_transaction_cash_transaction(self):
        """Test POST /api/transactions with cash transaction (no card_id)."""
        transaction_data = {
            'amount': -20.00,
            'description': 'Cash payment for coffee',
            'transaction_date': '2024-09-20T14:15:00Z'
        }

        try:
            with self._make_post_request(transaction_data) as response:
                self.assertEqual(response.getcode(), 201)

                response_data = json.loads(response.read().decode('utf-8'))
                self.assertIsNone(response_data.get('card_id'))

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_transaction_with_section(self):
        """Test POST /api/transactions with section assignment."""
        transaction_data = {
            'amount': -100.00,
            'description': 'Emergency expense',
            'transaction_date': '2024-09-20T16:00:00Z',
            'card_id': 1,
            'section_id': 1
        }

        try:
            with self._make_post_request(transaction_data) as response:
                self.assertEqual(response.getcode(), 201)

                response_data = json.loads(response.read().decode('utf-8'))
                self.assertEqual(response_data['section_id'], transaction_data['section_id'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_transaction_internal_transfer(self):
        """Test POST /api/transactions with internal transfer."""
        transaction_data = {
            'amount': 200.00,
            'description': 'Transfer from checking to savings',
            'transaction_date': '2024-09-20T11:00:00Z',
            'is_internal_transfer': True,
            'transfer_from_type': 'card',
            'transfer_from_id': 1,
            'transfer_to_type': 'card',
            'transfer_to_id': 2
        }

        try:
            with self._make_post_request(transaction_data) as response:
                self.assertEqual(response.getcode(), 201)

                response_data = json.loads(response.read().decode('utf-8'))
                self.assertTrue(response_data['is_internal_transfer'])
                self.assertEqual(response_data['transfer_from_type'], 'card')
                self.assertEqual(response_data['transfer_from_id'], 1)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_transaction_missing_required_fields(self):
        """Test POST /api/transactions with missing required fields."""
        incomplete_data = {
            'amount': -30.00
            # Missing description and transaction_date
        }

        try:
            with self._make_post_request(incomplete_data) as response:
                self.fail("Expected 400 error for missing required fields")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_post_transaction_invalid_card_id(self):
        """Test POST /api/transactions with nonexistent card_id."""
        transaction_data = {
            'amount': -25.00,
            'description': 'Test transaction',
            'transaction_date': '2024-09-20T12:00:00Z',
            'card_id': 99999  # Nonexistent card
        }

        try:
            with self._make_post_request(transaction_data) as response:
                self.fail("Expected 400 error for invalid card_id")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_post_transaction_invalid_transfer_data(self):
        """Test POST /api/transactions with incomplete internal transfer data."""
        transaction_data = {
            'amount': 100.00,
            'description': 'Incomplete transfer',
            'transaction_date': '2024-09-20T13:00:00Z',
            'is_internal_transfer': True,
            'transfer_from_type': 'card'
            # Missing transfer_from_id, transfer_to_type, transfer_to_id
        }

        try:
            with self._make_post_request(transaction_data) as response:
                self.fail("Expected 400 error for incomplete transfer data")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_post_transaction_returns_timestamps(self):
        """Test POST /api/transactions includes created_at and updated_at."""
        transaction_data = {
            'amount': -15.00,
            'description': 'Timestamp test',
            'transaction_date': '2024-09-20T15:30:00Z'
        }

        try:
            with self._make_post_request(transaction_data) as response:
                response_data = json.loads(response.read().decode('utf-8'))

                self.assertIn('created_at', response_data)
                self.assertIn('updated_at', response_data)
                self.assertIsInstance(response_data['created_at'], str)
                self.assertIsInstance(response_data['updated_at'], str)

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    print("Testing POST /api/transactions contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)