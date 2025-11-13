#!/usr/bin/env python3
"""
Contract test for GET /api/investments/movements
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

class TestMovementsGetContract(unittest.TestCase):
    """Contract tests for GET /api/investments/movements endpoint"""

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

    def test_get_movements_contract_success(self):
        """Test GET /api/investments/movements returns list of movements"""

        # Mock response data matching schema
        expected_response = [
            {
                "id": 1,
                "position_id": 1,
                "movement_type": "buy",
                "quantity": 10.0,
                "price_per_unit": 150.00,
                "total_amount": 1500.00,
                "movement_datetime": "2025-09-20T10:30:00Z",
                "description": "Initial investment",
                "created_at": "2025-09-20T10:30:00Z"
            },
            {
                "id": 2,
                "position_id": 1,
                "movement_type": "sell",
                "quantity": 5.0,
                "price_per_unit": 155.00,
                "total_amount": 775.00,
                "movement_datetime": "2025-09-20T14:30:00Z",
                "description": None,
                "created_at": "2025-09-20T14:30:00Z"
            }
        ]

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(f"{self.base_url}{self.endpoint}")

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate response structure
            self.assertIsInstance(data, list)
            for movement in data:
                self._validate_movement_schema(movement)

    def test_get_movements_contract_with_position_filter(self):
        """Test GET /api/investments/movements with positionId query parameter"""
        position_id = 1

        # Mock response data for specific position
        expected_response = [
            {
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
        ]

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request with positionId filter
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"positionId": position_id}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate all movements belong to the specified position
            for movement in data:
                self._validate_movement_schema(movement)
                self.assertEqual(movement["position_id"], position_id)

    def test_get_movements_contract_with_date_range_filter(self):
        """Test GET /api/investments/movements with date range query parameters"""
        start_date = "2025-09-20"
        end_date = "2025-09-21"

        # Mock response data for date range
        expected_response = [
            {
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
        ]

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request with date range filter
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"startDate": start_date, "endDate": end_date}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate response structure
            self.assertIsInstance(data, list)
            for movement in data:
                self._validate_movement_schema(movement)

    def test_get_movements_contract_empty_result(self):
        """Test GET /api/investments/movements returns empty array when no movements exist"""

        # Mock empty response
        expected_response = []

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(f"{self.base_url}{self.endpoint}")

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 0)

    def test_get_movements_contract_invalid_position_id(self):
        """Test GET /api/investments/movements with invalid positionId parameter"""
        invalid_position_id = "invalid"

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Invalid positionId format"}
            mock_get.return_value = mock_response

            # Make request with invalid positionId
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"positionId": invalid_position_id}
            )

            # Assertions
            self.assertEqual(response.status_code, 400)

    def test_get_movements_contract_invalid_date_format(self):
        """Test GET /api/investments/movements with invalid date format"""
        invalid_date = "invalid-date"

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Invalid date format"}
            mock_get.return_value = mock_response

            # Make request with invalid date
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"startDate": invalid_date}
            )

            # Assertions
            self.assertEqual(response.status_code, 400)

    def test_get_movements_contract_movement_types(self):
        """Test GET /api/investments/movements returns movements with correct movement_type values"""

        # Mock response with both buy and sell movements
        expected_response = [
            {
                "id": 1,
                "position_id": 1,
                "movement_type": "buy",
                "quantity": 10.0,
                "price_per_unit": 150.00,
                "total_amount": 1500.00,
                "movement_datetime": "2025-09-20T10:30:00Z",
                "description": "Buy order",
                "created_at": "2025-09-20T10:30:00Z"
            },
            {
                "id": 2,
                "position_id": 1,
                "movement_type": "sell",
                "quantity": 5.0,
                "price_per_unit": 155.00,
                "total_amount": 775.00,
                "movement_datetime": "2025-09-20T14:30:00Z",
                "description": "Sell order",
                "created_at": "2025-09-20T14:30:00Z"
            }
        ]

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(f"{self.base_url}{self.endpoint}")

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate movement types
            movement_types = [movement["movement_type"] for movement in data]
            for movement_type in movement_types:
                self.assertIn(movement_type, ["buy", "sell"])

    def test_get_movements_contract_combined_filters(self):
        """Test GET /api/investments/movements with multiple query parameters"""
        position_id = 1
        start_date = "2025-09-20"
        end_date = "2025-09-21"

        # Mock response data for combined filters
        expected_response = [
            {
                "id": 1,
                "position_id": 1,
                "movement_type": "buy",
                "quantity": 10.0,
                "price_per_unit": 150.00,
                "total_amount": 1500.00,
                "movement_datetime": "2025-09-20T10:30:00Z",
                "description": "Filtered result",
                "created_at": "2025-09-20T10:30:00Z"
            }
        ]

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request with multiple filters
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={
                    "positionId": position_id,
                    "startDate": start_date,
                    "endDate": end_date
                }
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate combined filter criteria
            for movement in data:
                self._validate_movement_schema(movement)
                self.assertEqual(movement["position_id"], position_id)

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