#!/usr/bin/env python3
"""
Contract test for POST /api/cards/{cardId}/sections endpoint.
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


class TestSectionsPostContract(unittest.TestCase):
    """Test contract for POST /api/cards/{cardId}/sections endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_base = f"{self.BASE_URL}/api/cards"

    def _make_post_request(self, card_id, data):
        """Helper to make POST request with JSON data."""
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            f"{self.api_base}/{card_id}/sections",
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        req.get_method = lambda: 'POST'
        return urllib.request.urlopen(req)

    def test_post_section_valid_data(self):
        """Test POST /api/cards/{cardId}/sections with valid section data."""
        card_id = 1
        section_data = {
            'name': 'Emergency Fund',
            'initial_balance': 500.00
        }

        try:
            with self._make_post_request(card_id, section_data) as response:
                self.assertEqual(response.getcode(), 201)

                # Check response content
                response_data = json.loads(response.read().decode('utf-8'))
                self.assertIsInstance(response_data, dict)

                # Validate response structure
                self.assertIn('id', response_data)
                self.assertEqual(response_data['card_id'], card_id)
                self.assertEqual(response_data['name'], section_data['name'])
                self.assertEqual(response_data['initial_balance'], section_data['initial_balance'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_section_minimal_data(self):
        """Test POST /api/cards/{cardId}/sections with minimal required data."""
        card_id = 1
        section_data = {
            'name': 'Minimal Section'
        }

        try:
            with self._make_post_request(card_id, section_data) as response:
                self.assertEqual(response.getcode(), 201)

                response_data = json.loads(response.read().decode('utf-8'))
                self.assertEqual(response_data['name'], section_data['name'])
                # Should default to 0.00 initial balance
                self.assertEqual(response_data['initial_balance'], 0.00)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_section_missing_name(self):
        """Test POST /api/cards/{cardId}/sections with missing required name field."""
        card_id = 1
        section_data = {
            'initial_balance': 100.00
            # Missing 'name' field
        }

        try:
            with self._make_post_request(card_id, section_data) as response:
                self.fail("Expected 400 error for missing name field")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_post_section_duplicate_name(self):
        """Test POST /api/cards/{cardId}/sections with duplicate section name."""
        card_id = 1
        section_data = {
            'name': 'Duplicate Section',
            'initial_balance': 100.00
        }

        try:
            # First creation should succeed
            with self._make_post_request(card_id, section_data) as response:
                self.assertEqual(response.getcode(), 201)

            # Second creation with same name should fail
            with self._make_post_request(card_id, section_data) as response:
                self.fail("Expected 409 error for duplicate section name")

        except urllib.error.HTTPError as e:
            # Should be 409 Conflict for duplicate name
            self.assertEqual(e.code, 409)
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_section_nonexistent_card(self):
        """Test POST /api/cards/{cardId}/sections with nonexistent card."""
        nonexistent_id = 99999
        section_data = {
            'name': 'Test Section'
        }

        try:
            with self._make_post_request(nonexistent_id, section_data) as response:
                self.fail("Expected 404 error for nonexistent card")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_post_section_invalid_card_id(self):
        """Test POST /api/cards/{cardId}/sections with invalid card ID format."""
        invalid_id = "not_a_number"
        section_data = {
            'name': 'Test Section'
        }

        try:
            with self._make_post_request(invalid_id, section_data) as response:
                self.fail("Expected 400 error for invalid card ID format")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_post_section_negative_balance(self):
        """Test POST /api/cards/{cardId}/sections with negative initial balance."""
        card_id = 1
        section_data = {
            'name': 'Negative Balance Section',
            'initial_balance': -100.00
        }

        try:
            with self._make_post_request(card_id, section_data) as response:
                # Negative balances might be allowed depending on business rules
                self.assertIn(response.getcode(), [201, 400])

                if response.getcode() == 201:
                    response_data = json.loads(response.read().decode('utf-8'))
                    self.assertEqual(response_data['initial_balance'], section_data['initial_balance'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_section_returns_json(self):
        """Test that POST /api/cards/{cardId}/sections returns JSON content type."""
        card_id = 1
        section_data = {
            'name': 'JSON Test Section'
        }

        try:
            with self._make_post_request(card_id, section_data) as response:
                content_type = response.headers.get('Content-Type', '')
                self.assertIn('application/json', content_type)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_post_section_includes_timestamps(self):
        """Test POST /api/cards/{cardId}/sections includes created_at timestamp."""
        card_id = 1
        section_data = {
            'name': 'Timestamp Test Section'
        }

        try:
            with self._make_post_request(card_id, section_data) as response:
                response_data = json.loads(response.read().decode('utf-8'))

                self.assertIn('created_at', response_data)
                self.assertIsInstance(response_data['created_at'], str)

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    print("Testing POST /api/cards/{cardId}/sections contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)