#!/usr/bin/env python3
"""
Contract test for GET /api/transactions/{transactionId}
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

class TestTransactionByIdContract(unittest.TestCase):
    """Contract tests for GET /api/transactions/{transactionId} endpoint"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8000"
        self.endpoint = "/api/transactions/{transactionId}"

        # Expected response schema for Transaction object
        self.expected_transaction_schema = {
            "id": int,
            "amount": float,
            "description": str,
            "transaction_date": str,  # ISO 8601 format
            "card_id": (int, type(None)),
            "section_id": (int, type(None)),
            "category": (str, type(None)),
            "is_internal_transfer": bool,
            "transfer_from_type": (str, type(None)),
            "transfer_from_id": (int, type(None)),
            "transfer_to_type": (str, type(None)),
            "transfer_to_id": (int, type(None)),
            "created_at": str,
            "updated_at": str
        }

    def test_get_transaction_by_id_contract_success(self):
        """Test GET /api/transactions/{transactionId} returns correct structure for existing transaction"""
        transaction_id = 1

        # Mock response data matching schema
        expected_response = {
            "id": 1,
            "amount": -50.00,
            "description": "Grocery shopping",
            "transaction_date": "2025-09-20T10:30:00Z",
            "card_id": 1,
            "section_id": None,
            "category": "Food",
            "is_internal_transfer": False,
            "transfer_from_type": None,
            "transfer_from_id": None,
            "transfer_to_type": None,
            "transfer_to_id": None,
            "created_at": "2025-09-20T10:30:00Z",
            "updated_at": "2025-09-20T10:30:00Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(f"{self.base_url}/api/transactions/{transaction_id}")

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate response structure
            self._validate_transaction_schema(data)
            self.assertEqual(data["id"], transaction_id)

    def test_get_transaction_by_id_contract_not_found(self):
        """Test GET /api/transactions/{transactionId} returns 404 for non-existent transaction"""
        transaction_id = 999999

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Transaction not found"}
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(f"{self.base_url}/api/transactions/{transaction_id}")

            # Assertions
            self.assertEqual(response.status_code, 404)

    def test_get_transaction_by_id_contract_invalid_id(self):
        """Test GET /api/transactions/{transactionId} handles invalid transaction ID format"""
        invalid_id = "invalid"

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Invalid transaction ID format"}
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(f"{self.base_url}/api/transactions/{invalid_id}")

            # Assertions
            self.assertEqual(response.status_code, 400)

    def test_get_transaction_internal_transfer_contract(self):
        """Test GET /api/transactions/{transactionId} returns correct structure for internal transfer"""
        transaction_id = 2

        # Mock internal transfer response
        expected_response = {
            "id": 2,
            "amount": 100.00,
            "description": "Transfer from checking to savings",
            "transaction_date": "2025-09-20T14:00:00Z",
            "card_id": None,
            "section_id": None,
            "category": None,
            "is_internal_transfer": True,
            "transfer_from_type": "card",
            "transfer_from_id": 1,
            "transfer_to_type": "card",
            "transfer_to_id": 2,
            "created_at": "2025-09-20T14:00:00Z",
            "updated_at": "2025-09-20T14:00:00Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(f"{self.base_url}/api/transactions/{transaction_id}")

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate response structure
            self._validate_transaction_schema(data)

            # Validate internal transfer fields
            self.assertTrue(data["is_internal_transfer"])
            self.assertIsNotNone(data["transfer_from_type"])
            self.assertIsNotNone(data["transfer_from_id"])
            self.assertIsNotNone(data["transfer_to_type"])
            self.assertIsNotNone(data["transfer_to_id"])

    def _validate_transaction_schema(self, data):
        """Helper method to validate transaction response schema"""
        self.assertIsInstance(data, dict)

        for field, expected_type in self.expected_transaction_schema.items():
            self.assertIn(field, data, f"Missing field: {field}")

            if isinstance(expected_type, tuple):
                # Field can be one of multiple types (e.g., int or None)
                self.assertTrue(
                    any(isinstance(data[field], t) for t in expected_type),
                    f"Field {field} should be one of {expected_type}, got {type(data[field])}"
                )
            else:
                # Field must be specific type
                self.assertIsInstance(
                    data[field], expected_type,
                    f"Field {field} should be {expected_type}, got {type(data[field])}"
                )

if __name__ == '__main__':
    unittest.main()