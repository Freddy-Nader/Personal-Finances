#!/usr/bin/env python3
"""
Contract test for GET /api/transactions endpoint.
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


class TestTransactionsGetContract(unittest.TestCase):
    """Test contract for GET /api/transactions endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_url = f"{self.BASE_URL}/api/transactions"

    def test_get_transactions_returns_200(self):
        """Test that GET /api/transactions returns 200 status code."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                self.assertEqual(response.getcode(), 200)
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_transactions_returns_json(self):
        """Test that GET /api/transactions returns JSON content type."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                content_type = response.headers.get('Content-Type', '')
                self.assertIn('application/json', content_type)
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_transactions_pagination_structure(self):
        """Test GET /api/transactions returns paginated response structure."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))

                # Should have pagination structure
                required_fields = {'transactions', 'total', 'page', 'limit', 'has_next'}
                actual_fields = set(data.keys())
                self.assertTrue(required_fields.issubset(actual_fields))

                # Validate field types
                self.assertIsInstance(data['transactions'], list)
                self.assertIsInstance(data['total'], int)
                self.assertIsInstance(data['page'], int)
                self.assertIsInstance(data['limit'], int)
                self.assertIsInstance(data['has_next'], bool)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_transactions_with_pagination_params(self):
        """Test GET /api/transactions with pagination parameters."""
        try:
            url_with_params = f"{self.api_url}?page=1&limit=50"
            with urllib.request.urlopen(url_with_params) as response:
                self.assertEqual(response.getcode(), 200)

                data = json.loads(response.read().decode('utf-8'))
                self.assertEqual(data['page'], 1)
                self.assertEqual(data['limit'], 50)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_transactions_with_card_filter(self):
        """Test GET /api/transactions with cardId filter."""
        try:
            card_id = 1
            url_with_filter = f"{self.api_url}?cardId={card_id}"
            with urllib.request.urlopen(url_with_filter) as response:
                self.assertEqual(response.getcode(), 200)

                data = json.loads(response.read().decode('utf-8'))
                # All transactions should belong to specified card
                for transaction in data['transactions']:
                    if transaction.get('card_id') is not None:
                        self.assertEqual(transaction['card_id'], card_id)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_transactions_with_date_filter(self):
        """Test GET /api/transactions with date range filter."""
        try:
            start_date = "2024-01-01"
            end_date = "2024-12-31"
            url_with_dates = f"{self.api_url}?startDate={start_date}&endDate={end_date}"

            with urllib.request.urlopen(url_with_dates) as response:
                self.assertEqual(response.getcode(), 200)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_transactions_structure_validation(self):
        """Test structure of transaction objects in response."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))

                if len(data['transactions']) > 0:
                    transaction = data['transactions'][0]

                    # Required fields
                    required_fields = {
                        'id', 'amount', 'description', 'transaction_date',
                        'created_at', 'updated_at'
                    }
                    actual_fields = set(transaction.keys())
                    self.assertTrue(required_fields.issubset(actual_fields))

                    # Field type validation
                    self.assertIsInstance(transaction['id'], int)
                    self.assertIsInstance(transaction['amount'], (int, float))
                    self.assertIsInstance(transaction['description'], str)
                    self.assertIsInstance(transaction['transaction_date'], str)

                    # Optional fields type validation
                    if 'card_id' in transaction:
                        self.assertTrue(transaction['card_id'] is None or
                                      isinstance(transaction['card_id'], int))

                    if 'is_internal_transfer' in transaction:
                        self.assertIsInstance(transaction['is_internal_transfer'], bool)

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    print("Testing GET /api/transactions contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)