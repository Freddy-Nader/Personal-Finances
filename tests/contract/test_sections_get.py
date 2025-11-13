#!/usr/bin/env python3
"""
Contract test for GET /api/cards/{cardId}/sections endpoint.
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


class TestSectionsGetContract(unittest.TestCase):
    """Test contract for GET /api/cards/{cardId}/sections endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_base = f"{self.BASE_URL}/api/cards"

    def test_get_sections_existing_card(self):
        """Test GET /api/cards/{cardId}/sections with existing card returns 200."""
        card_id = 1

        try:
            with urllib.request.urlopen(f"{self.api_base}/{card_id}/sections") as response:
                self.assertEqual(response.getcode(), 200)

                # Check response content
                response_data = json.loads(response.read().decode('utf-8'))
                self.assertIsInstance(response_data, list)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_sections_nonexistent_card(self):
        """Test GET /api/cards/{cardId}/sections with nonexistent card returns 404."""
        nonexistent_id = 99999

        try:
            with urllib.request.urlopen(f"{self.api_base}/{nonexistent_id}/sections") as response:
                self.fail("Expected 404 error for nonexistent card")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_get_sections_returns_json(self):
        """Test that GET /api/cards/{cardId}/sections returns JSON content type."""
        card_id = 1

        try:
            with urllib.request.urlopen(f"{self.api_base}/{card_id}/sections") as response:
                content_type = response.headers.get('Content-Type', '')
                self.assertIn('application/json', content_type)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_sections_empty_response(self):
        """Test structure when card has no sections."""
        card_id = 1

        try:
            with urllib.request.urlopen(f"{self.api_base}/{card_id}/sections") as response:
                response_data = json.loads(response.read().decode('utf-8'))

                # Should be empty array if no sections
                self.assertIsInstance(response_data, list)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_sections_with_data_structure(self):
        """Test structure of sections when they exist."""
        card_id = 1

        try:
            with urllib.request.urlopen(f"{self.api_base}/{card_id}/sections") as response:
                response_data = json.loads(response.read().decode('utf-8'))

                if len(response_data) > 0:
                    section = response_data[0]

                    # Validate section structure
                    required_fields = {'id', 'card_id', 'name', 'initial_balance', 'created_at'}
                    actual_fields = set(section.keys())
                    self.assertTrue(required_fields.issubset(actual_fields),
                                  f"Missing required fields: {required_fields - actual_fields}")

                    # Validate field types
                    self.assertIsInstance(section['id'], int)
                    self.assertEqual(section['card_id'], card_id)
                    self.assertIsInstance(section['name'], str)
                    self.assertIsInstance(section['initial_balance'], (int, float))
                    self.assertIsInstance(section['created_at'], str)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_sections_invalid_card_id(self):
        """Test GET /api/cards/{cardId}/sections with invalid card ID format."""
        invalid_id = "not_a_number"

        try:
            with urllib.request.urlopen(f"{self.api_base}/{invalid_id}/sections") as response:
                self.fail("Expected 400 error for invalid card ID format")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_get_sections_unique_names_per_card(self):
        """Test that section names are unique within a card."""
        card_id = 1

        try:
            with urllib.request.urlopen(f"{self.api_base}/{card_id}/sections") as response:
                response_data = json.loads(response.read().decode('utf-8'))

                if len(response_data) > 1:
                    # Check that all section names are unique
                    section_names = [section['name'] for section in response_data]
                    unique_names = set(section_names)
                    self.assertEqual(len(section_names), len(unique_names),
                                   "Section names should be unique within a card")

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_sections_card_id_consistency(self):
        """Test that all sections belong to the requested card."""
        card_id = 1

        try:
            with urllib.request.urlopen(f"{self.api_base}/{card_id}/sections") as response:
                response_data = json.loads(response.read().decode('utf-8'))

                for section in response_data:
                    self.assertEqual(section['card_id'], card_id,
                                   f"Section {section['id']} should belong to card {card_id}")

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    print("Testing GET /api/cards/{cardId}/sections contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)