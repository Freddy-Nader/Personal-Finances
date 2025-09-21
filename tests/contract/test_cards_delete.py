#!/usr/bin/env python3
"""
Contract test for DELETE /api/cards/{cardId} endpoint.
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


class TestCardsDeleteContract(unittest.TestCase):
    """Test contract for DELETE /api/cards/{cardId} endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_url = f"{self.BASE_URL}/api/cards"

    def _make_delete_request(self, card_id):
        """Helper to make DELETE request."""
        req = urllib.request.Request(f"{self.api_url}/{card_id}")
        req.get_method = lambda: 'DELETE'
        return urllib.request.urlopen(req)

    def test_delete_card_existing_card(self):
        """Test DELETE /api/cards/{cardId} with existing card returns 204."""
        card_id = 1

        try:
            with self._make_delete_request(card_id) as response:
                self.assertEqual(response.getcode(), 204)

                # 204 No Content should have empty response body
                content = response.read()
                self.assertEqual(len(content), 0)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_delete_card_nonexistent_card(self):
        """Test DELETE /api/cards/{cardId} with nonexistent card returns 404."""
        nonexistent_id = 99999

        try:
            with self._make_delete_request(nonexistent_id) as response:
                self.fail("Expected 404 error for nonexistent card")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_delete_card_invalid_id_format(self):
        """Test DELETE /api/cards/{cardId} with invalid ID format returns 400."""
        invalid_id = "not_a_number"

        try:
            with self._make_delete_request(invalid_id) as response:
                self.fail("Expected 400 error for invalid ID format")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_delete_card_cascade_behavior(self):
        """Test DELETE /api/cards/{cardId} handles cascading deletes properly."""
        # This test verifies that deleting a card also deletes related sections
        # and handles transactions appropriately
        card_id = 1

        # First, verify the card exists and potentially has sections
        try:
            # Check if card exists before deletion
            with urllib.request.urlopen(f"{self.api_url}/{card_id}") as response:
                self.assertEqual(response.getcode(), 200)

            # Delete the card
            with self._make_delete_request(card_id) as response:
                self.assertEqual(response.getcode(), 204)

            # Verify card no longer exists
            try:
                with urllib.request.urlopen(f"{self.api_url}/{card_id}") as response:
                    self.fail("Card should no longer exist after deletion")
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_delete_card_with_sections(self):
        """Test DELETE /api/cards/{cardId} removes associated sections."""
        # This assumes card has sections and tests cascade behavior
        card_id = 1

        try:
            # Delete the card
            with self._make_delete_request(card_id) as response:
                self.assertEqual(response.getcode(), 204)

            # Verify sections are also deleted (if sections endpoint is available)
            # This is a forward-looking test for when sections API exists
            try:
                sections_url = f"{self.BASE_URL}/api/cards/{card_id}/sections"
                with urllib.request.urlopen(sections_url) as response:
                    self.fail("Sections should be deleted when card is deleted")
            except urllib.error.HTTPError as e:
                # Could be 404 (card not found) or 200 with empty array
                self.assertIn(e.code, [404, 200])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_delete_card_idempotent(self):
        """Test DELETE /api/cards/{cardId} is idempotent."""
        card_id = 99998  # Use different ID to avoid conflicts

        # First delete attempt
        try:
            with self._make_delete_request(card_id) as response:
                first_status = response.getcode()
        except urllib.error.HTTPError as e:
            first_status = e.code

        # Second delete attempt should behave consistently
        try:
            with self._make_delete_request(card_id) as response:
                second_status = response.getcode()
        except urllib.error.HTTPError as e:
            second_status = e.code

        # Both attempts should return same status (either 204 or 404)
        self.assertEqual(first_status, second_status)

    def test_delete_card_transaction_handling(self):
        """Test DELETE /api/cards/{cardId} handles transactions appropriately."""
        # This test verifies business logic for transactions when card is deleted
        # Transactions might be soft-deleted, moved to "deleted card", or prevented
        card_id = 1

        try:
            with self._make_delete_request(card_id) as response:
                # Should succeed regardless of transaction handling approach
                self.assertIn(response.getcode(), [204, 400])

                if response.getcode() == 400:
                    # If deletion is prevented due to existing transactions
                    response_data = json.loads(response.read().decode('utf-8'))
                    self.assertIn('error', response_data)
                    # Error message should indicate transaction conflict

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    print("Testing DELETE /api/cards/{cardId} contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)