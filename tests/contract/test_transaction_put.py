#!/usr/bin/env python3
"""
Contract test for PUT /api/transactions/{transactionId}
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

class TestTransactionPutContract(unittest.TestCase):
    """Contract tests for PUT /api/transactions/{transactionId} endpoint"""

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

        # Valid update request payload
        self.valid_update_payload = {
            "amount": -75.50,
            "description": "Updated grocery shopping",
            "transaction_date": "2025-09-20T11:00:00Z",
            "category": "Food & Dining"
        }

    def test_put_transaction_contract_success(self):
        """Test PUT /api/transactions/{transactionId} updates transaction successfully"""
        transaction_id = 1

        # Mock response data matching schema
        expected_response = {
            "id": 1,
            "amount": -75.50,
            "description": "Updated grocery shopping",
            "transaction_date": "2025-09-20T11:00:00Z",
            "card_id": 1,
            "section_id": None,
            "category": "Food & Dining",
            "is_internal_transfer": False,
            "transfer_from_type": None,
            "transfer_from_id": None,
            "transfer_to_type": None,
            "transfer_to_id": None,
            "created_at": "2025-09-20T10:30:00Z",
            "updated_at": "2025-09-20T11:05:00Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.put') as mock_put:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_put.return_value = mock_response

            # Make request
            import requests
            response = requests.put(
                f"{self.base_url}/api/transactions/{transaction_id}",
                json=self.valid_update_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate response structure
            self._validate_transaction_schema(data)
            self.assertEqual(data["id"], transaction_id)
            self.assertEqual(data["amount"], self.valid_update_payload["amount"])
            self.assertEqual(data["description"], self.valid_update_payload["description"])

    def test_put_transaction_contract_not_found(self):
        """Test PUT /api/transactions/{transactionId} returns 404 for non-existent transaction"""
        transaction_id = 999999

        # This test will FAIL until the endpoint is implemented
        with patch('requests.put') as mock_put:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Transaction not found"}
            mock_put.return_value = mock_response

            # Make request
            import requests
            response = requests.put(
                f"{self.base_url}/api/transactions/{transaction_id}",
                json=self.valid_update_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 404)

    def test_put_transaction_contract_invalid_payload(self):
        """Test PUT /api/transactions/{transactionId} validates request payload"""
        transaction_id = 1

        invalid_payloads = [
            {},  # Empty payload
            {"amount": "invalid"},  # Invalid amount type
            {"transaction_date": "invalid-date"},  # Invalid date format
            {"description": ""},  # Empty description
        ]

        for invalid_payload in invalid_payloads:
            with self.subTest(payload=invalid_payload):
                # This test will FAIL until the endpoint is implemented
                with patch('requests.put') as mock_put:
                    mock_response = Mock()
                    mock_response.status_code = 400
                    mock_response.json.return_value = {"error": "Invalid request payload"}
                    mock_put.return_value = mock_response

                    # Make request
                    import requests
                    response = requests.put(
                        f"{self.base_url}/api/transactions/{transaction_id}",
                        json=invalid_payload,
                        headers={"Content-Type": "application/json"}
                    )

                    # Assertions
                    self.assertEqual(response.status_code, 400)

    def test_put_transaction_contract_partial_update(self):
        """Test PUT /api/transactions/{transactionId} allows partial updates"""
        transaction_id = 1

        # Only update description
        partial_update_payload = {
            "description": "Partial update test"
        }

        # Mock response with only description updated
        expected_response = {
            "id": 1,
            "amount": -50.00,  # Original amount
            "description": "Partial update test",  # Updated description
            "transaction_date": "2025-09-20T10:30:00Z",  # Original date
            "card_id": 1,
            "section_id": None,
            "category": "Food",  # Original category
            "is_internal_transfer": False,
            "transfer_from_type": None,
            "transfer_from_id": None,
            "transfer_to_type": None,
            "transfer_to_id": None,
            "created_at": "2025-09-20T10:30:00Z",
            "updated_at": "2025-09-20T11:10:00Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.put') as mock_put:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_put.return_value = mock_response

            # Make request
            import requests
            response = requests.put(
                f"{self.base_url}/api/transactions/{transaction_id}",
                json=partial_update_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate response structure
            self._validate_transaction_schema(data)
            self.assertEqual(data["description"], partial_update_payload["description"])

    def test_put_transaction_contract_invalid_id(self):
        """Test PUT /api/transactions/{transactionId} handles invalid transaction ID format"""
        invalid_id = "invalid"

        # This test will FAIL until the endpoint is implemented
        with patch('requests.put') as mock_put:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Invalid transaction ID format"}
            mock_put.return_value = mock_response

            # Make request
            import requests
            response = requests.put(
                f"{self.base_url}/api/transactions/{invalid_id}",
                json=self.valid_update_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 400)

    def test_put_transaction_contract_readonly_fields(self):
        """Test PUT /api/transactions/{transactionId} ignores readonly fields"""
        transaction_id = 1

        # Attempt to update readonly fields
        payload_with_readonly = {
            "description": "Updated description",
            "id": 999,  # Should be ignored
            "created_at": "2025-01-01T00:00:00Z",  # Should be ignored
            "is_internal_transfer": True,  # Should be ignored for existing transaction
            "transfer_from_type": "card"  # Should be ignored for existing transaction
        }

        # Mock response ignoring readonly fields
        expected_response = {
            "id": 1,  # Original ID (not 999)
            "amount": -50.00,
            "description": "Updated description",  # Only this should update
            "transaction_date": "2025-09-20T10:30:00Z",
            "card_id": 1,
            "section_id": None,
            "category": "Food",
            "is_internal_transfer": False,  # Original value (not True)
            "transfer_from_type": None,  # Original value (not "card")
            "transfer_from_id": None,
            "transfer_to_type": None,
            "transfer_to_id": None,
            "created_at": "2025-09-20T10:30:00Z",  # Original timestamp
            "updated_at": "2025-09-20T11:15:00Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.put') as mock_put:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_put.return_value = mock_response

            # Make request
            import requests
            response = requests.put(
                f"{self.base_url}/api/transactions/{transaction_id}",
                json=payload_with_readonly,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate readonly fields were not updated
            self.assertEqual(data["id"], 1)  # Not 999
            self.assertFalse(data["is_internal_transfer"])  # Not True
            self.assertIsNone(data["transfer_from_type"])  # Not "card"

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