#!/usr/bin/env python3
"""
Contract test for PUT /api/cards/{cardId} endpoint.
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


class TestCardsPutContract(unittest.TestCase):
    """Test contract for PUT /api/cards/{cardId} endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_url = f"{self.BASE_URL}/api/cards"

    def _make_put_request(self, card_id, data):
        """Helper to make PUT request with JSON data."""
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            f"{self.api_url}/{card_id}",
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        req.get_method = lambda: 'PUT'
        return urllib.request.urlopen(req)

    def test_put_card_update_name(self):
        """Test PUT /api/cards/{cardId} updates card name."""
        card_id = 1
        update_data = {
            'name': 'Updated Card Name'
        }

        try:
            with self._make_put_request(card_id, update_data) as response:
                self.assertEqual(response.getcode(), 200)

                response_data = json.loads(response.read().decode('utf-8'))
                self.assertEqual(response_data['id'], card_id)
                self.assertEqual(response_data['name'], update_data['name'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_put_card_update_balance(self):
        """Test PUT /api/cards/{cardId} updates card balance."""
        card_id = 1
        update_data = {
            'balance': 2500.75
        }

        try:
            with self._make_put_request(card_id, update_data) as response:
                self.assertEqual(response.getcode(), 200)

                response_data = json.loads(response.read().decode('utf-8'))
                self.assertEqual(response_data['balance'], update_data['balance'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_put_card_update_credit_limit(self):
        """Test PUT /api/cards/{cardId} updates credit limit for credit cards."""
        card_id = 2  # Assume this is a credit card
        update_data = {
            'credit_limit': 10000.00
        }

        try:
            with self._make_put_request(card_id, update_data) as response:
                self.assertEqual(response.getcode(), 200)

                response_data = json.loads(response.read().decode('utf-8'))
                if response_data.get('type') == 'credit':
                    self.assertEqual(response_data['credit_limit'], update_data['credit_limit'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_put_card_nonexistent_card(self):
        """Test PUT /api/cards/{cardId} with nonexistent card returns 404."""
        nonexistent_id = 99999
        update_data = {
            'name': 'This should fail'
        }

        try:
            with self._make_put_request(nonexistent_id, update_data) as response:
                self.fail("Expected 404 error for nonexistent card")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_put_card_invalid_id_format(self):
        """Test PUT /api/cards/{cardId} with invalid ID format returns 400."""
        invalid_id = "not_a_number"
        update_data = {
            'name': 'This should fail'
        }

        try:
            with self._make_put_request(invalid_id, update_data) as response:
                self.fail("Expected 400 error for invalid ID format")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_put_card_empty_update(self):
        """Test PUT /api/cards/{cardId} with empty update data."""
        card_id = 1
        update_data = {}

        try:
            with self._make_put_request(card_id, update_data) as response:
                # Should return 200 with no changes
                self.assertEqual(response.getcode(), 200)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_put_card_updates_timestamp(self):
        """Test PUT /api/cards/{cardId} updates updated_at timestamp."""
        card_id = 1
        update_data = {
            'name': 'Updated for timestamp test'
        }

        try:
            with self._make_put_request(card_id, update_data) as response:
                response_data = json.loads(response.read().decode('utf-8'))

                self.assertIn('updated_at', response_data)
                self.assertIn('created_at', response_data)
                self.assertIsInstance(response_data['updated_at'], str)

                # updated_at should be different from created_at for existing cards
                # (unless updated immediately after creation)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_put_card_returns_json(self):
        """Test that PUT /api/cards/{cardId} returns JSON content type."""
        card_id = 1
        update_data = {
            'name': 'JSON Test Update'
        }

        try:
            with self._make_put_request(card_id, update_data) as response:
                content_type = response.headers.get('Content-Type', '')
                self.assertIn('application/json', content_type)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_put_card_immutable_fields(self):
        """Test PUT /api/cards/{cardId} doesn't allow updating immutable fields."""
        card_id = 1
        update_data = {
            'id': 999,  # Should not be updatable
            'type': 'credit',  # Type changes may not be allowed
            'created_at': '2020-01-01T00:00:00Z'  # Should not be updatable
        }

        try:
            with self._make_put_request(card_id, update_data) as response:
                response_data = json.loads(response.read().decode('utf-8'))

                # ID should remain unchanged
                self.assertEqual(response_data['id'], card_id)

                # created_at should remain unchanged (or be close to original)
                # Type change behavior depends on business rules

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    print("Testing PUT /api/cards/{cardId} contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)