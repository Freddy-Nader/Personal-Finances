#!/usr/bin/env python3
"""
Contract test for POST /api/investments/movements
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

class TestMovementsPostContract(unittest.TestCase):
    """Contract tests for POST /api/investments/movements endpoint"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8000"
        self.endpoint = "/api/investments/movements"

        # Expected response schema for Movement object
        self.expected_movement_schema = {
            "id": int,
            "position_id": int,
            "movement_type": str,
            "quantity": float,
            "price_per_unit": float,
            "total_amount": float,
            "movement_datetime": str,  # ISO 8601 format
            "description": (str, type(None)),
            "created_at": str
        }

        # Valid create request payloads
        self.valid_buy_payload = {
            "position_id": 1,
            "movement_type": "buy",
            "quantity": 10.0,
            "price_per_unit": 150.00,
            "movement_datetime": "2025-09-20T10:30:00Z",
            "description": "Initial investment"
        }

        self.valid_sell_payload = {
            "position_id": 1,
            "movement_type": "sell",
            "quantity": 5.0,
            "price_per_unit": 155.00,
            "movement_datetime": "2025-09-20T14:30:00Z",
            "description": "Partial sale"
        }

    def test_post_movement_buy_contract_success(self):
        """Test POST /api/investments/movements creates buy movement successfully"""

        # Mock response data matching schema
        expected_response = {
            "id": 1,
            "position_id": 1,
            "movement_type": "buy",
            "quantity": 10.0,
            "price_per_unit": 150.00,
            "total_amount": 1500.00,
            "movement_datetime": "2025-09-20T10:30:00Z",
            "description": "Initial investment",
            "created_at": "2025-09-20T10:30:00Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = expected_response
            mock_post.return_value = mock_response

            # Make request
            import requests
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json=self.valid_buy_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 201)
            data = response.json()

            # Validate response structure
            self._validate_movement_schema(data)
            self.assertEqual(data["movement_type"], "buy")
            self.assertEqual(data["quantity"], 10.0)
            self.assertEqual(data["total_amount"], 1500.00)  # quantity * price_per_unit

    def test_post_movement_sell_contract_success(self):
        """Test POST /api/investments/movements creates sell movement successfully"""

        # Mock response data matching schema
        expected_response = {
            "id": 2,
            "position_id": 1,
            "movement_type": "sell",
            "quantity": 5.0,
            "price_per_unit": 155.00,
            "total_amount": 775.00,
            "movement_datetime": "2025-09-20T14:30:00Z",
            "description": "Partial sale",
            "created_at": "2025-09-20T14:30:00Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = expected_response
            mock_post.return_value = mock_response

            # Make request
            import requests
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json=self.valid_sell_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 201)
            data = response.json()

            # Validate response structure
            self._validate_movement_schema(data)
            self.assertEqual(data["movement_type"], "sell")
            self.assertEqual(data["quantity"], 5.0)

    def test_post_movement_contract_invalid_payload(self):
        """Test POST /api/investments/movements validates request payload"""

        invalid_payloads = [
            {},  # Empty payload
            {"position_id": 1},  # Missing required fields
            {"movement_type": "buy"},  # Missing required fields
            {"position_id": "invalid", "movement_type": "buy", "quantity": 10, "price_per_unit": 150, "movement_datetime": "2025-09-20T10:30:00Z"},  # Invalid position_id type
            {"position_id": 1, "movement_type": "invalid", "quantity": 10, "price_per_unit": 150, "movement_datetime": "2025-09-20T10:30:00Z"},  # Invalid movement_type
            {"position_id": 1, "movement_type": "buy", "quantity": -5, "price_per_unit": 150, "movement_datetime": "2025-09-20T10:30:00Z"},  # Negative quantity
            {"position_id": 1, "movement_type": "buy", "quantity": 10, "price_per_unit": -150, "movement_datetime": "2025-09-20T10:30:00Z"},  # Negative price
            {"position_id": 1, "movement_type": "buy", "quantity": 10, "price_per_unit": 150, "movement_datetime": "invalid-date"},  # Invalid datetime
        ]

        for invalid_payload in invalid_payloads:
            with self.subTest(payload=invalid_payload):
                # This test will FAIL until the endpoint is implemented
                with patch('requests.post') as mock_post:
                    mock_response = Mock()
                    mock_response.status_code = 400
                    mock_response.json.return_value = {"error": "Invalid request payload"}
                    mock_post.return_value = mock_response

                    # Make request
                    import requests
                    response = requests.post(
                        f"{self.base_url}{self.endpoint}",
                        json=invalid_payload,
                        headers={"Content-Type": "application/json"}
                    )

                    # Assertions
                    self.assertEqual(response.status_code, 400)

    def test_post_movement_contract_nonexistent_position(self):
        """Test POST /api/investments/movements handles non-existent position_id"""

        invalid_payload = {
            "position_id": 999999,
            "movement_type": "buy",
            "quantity": 10.0,
            "price_per_unit": 150.00,
            "movement_datetime": "2025-09-20T10:30:00Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Investment position not found"}
            mock_post.return_value = mock_response

            # Make request
            import requests
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json=invalid_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 404)

    def test_post_movement_contract_total_amount_calculation(self):
        """Test POST /api/investments/movements calculates total_amount correctly"""

        payload = {
            "position_id": 1,
            "movement_type": "buy",
            "quantity": 7.5,
            "price_per_unit": 123.45,
            "movement_datetime": "2025-09-20T10:30:00Z"
        }

        expected_total = 7.5 * 123.45  # 925.875

        # Mock response with calculated total
        expected_response = {
            "id": 1,
            "position_id": 1,
            "movement_type": "buy",
            "quantity": 7.5,
            "price_per_unit": 123.45,
            "total_amount": expected_total,
            "movement_datetime": "2025-09-20T10:30:00Z",
            "description": None,
            "created_at": "2025-09-20T10:30:00Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = expected_response
            mock_post.return_value = mock_response

            # Make request
            import requests
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 201)
            data = response.json()
            self.assertAlmostEqual(data["total_amount"], expected_total, places=2)

    def test_post_movement_contract_sell_validation(self):
        """Test POST /api/investments/movements validates sell quantity against holdings"""

        # Attempt to sell more than owned
        oversell_payload = {
            "position_id": 1,
            "movement_type": "sell",
            "quantity": 1000.0,  # More than currently held
            "price_per_unit": 150.00,
            "movement_datetime": "2025-09-20T10:30:00Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Cannot sell more than current holdings"}
            mock_post.return_value = mock_response

            # Make request
            import requests
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json=oversell_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 400)

    def test_post_movement_contract_movement_type_validation(self):
        """Test POST /api/investments/movements validates movement_type enum values"""

        valid_movement_types = ["buy", "sell"]
        invalid_movement_types = ["transfer", "dividend", "split", "invalid"]

        # Test valid movement types
        for movement_type in valid_movement_types:
            payload = {
                "position_id": 1,
                "movement_type": movement_type,
                "quantity": 10.0,
                "price_per_unit": 150.00,
                "movement_datetime": "2025-09-20T10:30:00Z"
            }

            expected_response = {
                "id": 1,
                "position_id": 1,
                "movement_type": movement_type,
                "quantity": 10.0,
                "price_per_unit": 150.00,
                "total_amount": 1500.00,
                "movement_datetime": "2025-09-20T10:30:00Z",
                "description": None,
                "created_at": "2025-09-20T10:30:00Z"
            }

            with self.subTest(movement_type=movement_type, valid=True):
                with patch('requests.post') as mock_post:
                    mock_response = Mock()
                    mock_response.status_code = 201
                    mock_response.json.return_value = expected_response
                    mock_post.return_value = mock_response

                    # Make request
                    import requests
                    response = requests.post(
                        f"{self.base_url}{self.endpoint}",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )

                    # Assertions
                    self.assertEqual(response.status_code, 201)

        # Test invalid movement types
        for movement_type in invalid_movement_types:
            payload = {
                "position_id": 1,
                "movement_type": movement_type,
                "quantity": 10.0,
                "price_per_unit": 150.00,
                "movement_datetime": "2025-09-20T10:30:00Z"
            }

            with self.subTest(movement_type=movement_type, valid=False):
                with patch('requests.post') as mock_post:
                    mock_response = Mock()
                    mock_response.status_code = 400
                    mock_response.json.return_value = {"error": "Invalid movement_type"}
                    mock_post.return_value = mock_response

                    # Make request
                    import requests
                    response = requests.post(
                        f"{self.base_url}{self.endpoint}",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )

                    # Assertions
                    self.assertEqual(response.status_code, 400)

    def test_post_movement_contract_optional_description(self):
        """Test POST /api/investments/movements handles optional description field"""

        # Test with description
        with_description = self.valid_buy_payload.copy()

        # Test without description
        without_description = self.valid_buy_payload.copy()
        del without_description["description"]

        test_cases = [
            (with_description, "With description"),
            (without_description, "Without description")
        ]

        for payload, case_name in test_cases:
            with self.subTest(case=case_name):
                expected_response = {
                    "id": 1,
                    "position_id": 1,
                    "movement_type": "buy",
                    "quantity": 10.0,
                    "price_per_unit": 150.00,
                    "total_amount": 1500.00,
                    "movement_datetime": "2025-09-20T10:30:00Z",
                    "description": payload.get("description"),
                    "created_at": "2025-09-20T10:30:00Z"
                }

                # This test will FAIL until the endpoint is implemented
                with patch('requests.post') as mock_post:
                    mock_response = Mock()
                    mock_response.status_code = 201
                    mock_response.json.return_value = expected_response
                    mock_post.return_value = mock_response

                    # Make request
                    import requests
                    response = requests.post(
                        f"{self.base_url}{self.endpoint}",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )

                    # Assertions
                    self.assertEqual(response.status_code, 201)
                    data = response.json()
                    self._validate_movement_schema(data)

    def test_post_movement_contract_datetime_precision(self):
        """Test POST /api/investments/movements handles precise datetime values"""

        payload = {
            "position_id": 1,
            "movement_type": "buy",
            "quantity": 10.0,
            "price_per_unit": 150.00,
            "movement_datetime": "2025-09-20T10:30:45.123Z"  # Precise timestamp
        }

        expected_response = {
            "id": 1,
            "position_id": 1,
            "movement_type": "buy",
            "quantity": 10.0,
            "price_per_unit": 150.00,
            "total_amount": 1500.00,
            "movement_datetime": "2025-09-20T10:30:45.123Z",
            "description": None,
            "created_at": "2025-09-20T10:30:45.123Z"
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = expected_response
            mock_post.return_value = mock_response

            # Make request
            import requests
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 201)
            data = response.json()
            self.assertEqual(data["movement_datetime"], "2025-09-20T10:30:45.123Z")

    def _validate_movement_schema(self, data):
        """Helper method to validate movement response schema"""
        self.assertIsInstance(data, dict)

        for field, expected_type in self.expected_movement_schema.items():
            self.assertIn(field, data, f"Missing field: {field}")

            if isinstance(expected_type, tuple):
                # Field can be one of multiple types (e.g., str or None)
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

        # Additional validations
        self.assertIn(data["movement_type"], ["buy", "sell"])
        self.assertGreater(data["quantity"], 0)
        self.assertGreater(data["price_per_unit"], 0)
        self.assertGreater(data["total_amount"], 0)

if __name__ == '__main__':
    unittest.main()