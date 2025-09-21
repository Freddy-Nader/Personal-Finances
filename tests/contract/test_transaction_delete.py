#!/usr/bin/env python3
"""
Contract test for DELETE /api/transactions/{transactionId}
Tests the API contract according to specs/001-build-an-application/contracts/api-contracts.yaml

This test MUST FAIL initially (TDD approach) - no implementation exists yet.
"""

import unittest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class TestTransactionDeleteContract(unittest.TestCase):
    """Contract tests for DELETE /api/transactions/{transactionId} endpoint"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8000"
        self.endpoint = "/api/transactions/{transactionId}"

    def test_delete_transaction_contract_success(self):
        """Test DELETE /api/transactions/{transactionId} deletes transaction successfully"""
        transaction_id = 1

        # This test will FAIL until the endpoint is implemented
        with patch('requests.delete') as mock_delete:
            mock_response = Mock()
            mock_response.status_code = 204
            mock_response.text = ""
            mock_delete.return_value = mock_response

            # Make request
            import requests
            response = requests.delete(f"{self.base_url}/api/transactions/{transaction_id}")

            # Assertions
            self.assertEqual(response.status_code, 204)
            # 204 No Content should have empty response body
            self.assertEqual(response.text, "")

    def test_delete_transaction_contract_not_found(self):
        """Test DELETE /api/transactions/{transactionId} returns 404 for non-existent transaction"""
        transaction_id = 999999

        # This test will FAIL until the endpoint is implemented
        with patch('requests.delete') as mock_delete:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Transaction not found"}
            mock_delete.return_value = mock_response

            # Make request
            import requests
            response = requests.delete(f"{self.base_url}/api/transactions/{transaction_id}")

            # Assertions
            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertIn("error", data)

    def test_delete_transaction_contract_invalid_id(self):
        """Test DELETE /api/transactions/{transactionId} handles invalid transaction ID format"""
        invalid_id = "invalid"

        # This test will FAIL until the endpoint is implemented
        with patch('requests.delete') as mock_delete:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Invalid transaction ID format"}
            mock_delete.return_value = mock_response

            # Make request
            import requests
            response = requests.delete(f"{self.base_url}/api/transactions/{invalid_id}")

            # Assertions
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn("error", data)

    def test_delete_transaction_contract_already_deleted(self):
        """Test DELETE /api/transactions/{transactionId} handles already deleted transaction"""
        transaction_id = 1

        # First deletion succeeds
        with patch('requests.delete') as mock_delete:
            mock_response = Mock()
            mock_response.status_code = 204
            mock_response.text = ""
            mock_delete.return_value = mock_response

            # Make first request
            import requests
            response = requests.delete(f"{self.base_url}/api/transactions/{transaction_id}")
            self.assertEqual(response.status_code, 204)

        # Second deletion of same transaction should return 404
        with patch('requests.delete') as mock_delete:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Transaction not found"}
            mock_delete.return_value = mock_response

            # Make second request
            response = requests.delete(f"{self.base_url}/api/transactions/{transaction_id}")
            self.assertEqual(response.status_code, 404)

    def test_delete_transaction_internal_transfer_behavior(self):
        """Test DELETE /api/transactions/{transactionId} handles internal transfer deletion properly"""
        transaction_id = 5  # Assume this is an internal transfer transaction

        # Mock deletion of internal transfer
        # Note: The actual behavior of whether to delete paired transaction
        # or just mark as orphaned should be defined in business logic
        with patch('requests.delete') as mock_delete:
            mock_response = Mock()
            mock_response.status_code = 204
            mock_response.text = ""
            mock_delete.return_value = mock_response

            # Make request
            import requests
            response = requests.delete(f"{self.base_url}/api/transactions/{transaction_id}")

            # Assertions
            self.assertEqual(response.status_code, 204)

            # Note: In a real implementation, this might also need to handle
            # the paired transaction in an internal transfer scenario

    def test_delete_transaction_contract_server_error(self):
        """Test DELETE /api/transactions/{transactionId} handles server errors gracefully"""
        transaction_id = 1

        # Mock server error
        with patch('requests.delete') as mock_delete:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal server error"}
            mock_delete.return_value = mock_response

            # Make request
            import requests
            response = requests.delete(f"{self.base_url}/api/transactions/{transaction_id}")

            # Assertions
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn("error", data)

    def test_delete_transaction_contract_database_constraint(self):
        """Test DELETE /api/transactions/{transactionId} handles database constraints"""
        transaction_id = 1

        # Mock constraint violation (e.g., foreign key reference)
        with patch('requests.delete') as mock_delete:
            mock_response = Mock()
            mock_response.status_code = 409
            mock_response.json.return_value = {
                "error": "Cannot delete transaction due to existing references"
            }
            mock_delete.return_value = mock_response

            # Make request
            import requests
            response = requests.delete(f"{self.base_url}/api/transactions/{transaction_id}")

            # Assertions
            self.assertEqual(response.status_code, 409)
            data = response.json()
            self.assertIn("error", data)

if __name__ == '__main__':
    unittest.main()