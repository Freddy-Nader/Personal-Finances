#!/usr/bin/env python3
"""
Contract test for POST /api/investments/positions
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

class TestPositionsPostContract(unittest.TestCase):
    """Contract tests for POST /api/investments/positions endpoint"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8000"
        self.endpoint = "/api/investments/positions"

        # Expected response schema for InvestmentPosition object
        self.expected_position_schema = {
            "id": int,
            "asset_type": str,
            "symbol": str,
            "current_quantity": float,
            "current_value": float,
            "profit_loss": float,
            "created_at": str,
            "updated_at": str
        }

        # Valid create request payloads
        self.valid_stock_payload = {
            "asset_type": "stock",
            "symbol": "AAPL"
        }

        self.valid_crypto_payload = {
            "asset_type": "crypto",
            "symbol": "BTC"
        }

    def test_post_investment_position_stock_contract_success(self):
        """Test POST /api/investments/positions creates stock position successfully"""

        # Mock response data matching schema
        expected_response = {
            "id": 1,
            "asset_type": "stock",
            "symbol": "AAPL",
            "current_quantity": 0.0,
            "current_value": 0.0,
            "profit_loss": 0.0,
            "created_at": "2025-09-20T10:30:00Z",
            "updated_at": "2025-09-20T10:30:00Z"
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
                json=self.valid_stock_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 201)
            data = response.json()

            # Validate response structure
            self._validate_position_schema(data)
            self.assertEqual(data["asset_type"], "stock")
            self.assertEqual(data["symbol"], "AAPL")
            self.assertEqual(data["current_quantity"], 0.0)  # New position starts empty

    def test_post_investment_position_crypto_contract_success(self):
        """Test POST /api/investments/positions creates crypto position successfully"""

        # Mock response data matching schema
        expected_response = {
            "id": 2,
            "asset_type": "crypto",
            "symbol": "BTC",
            "current_quantity": 0.0,
            "current_value": 0.0,
            "profit_loss": 0.0,
            "created_at": "2025-09-20T10:35:00Z",
            "updated_at": "2025-09-20T10:35:00Z"
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
                json=self.valid_crypto_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 201)
            data = response.json()

            # Validate response structure
            self._validate_position_schema(data)
            self.assertEqual(data["asset_type"], "crypto")
            self.assertEqual(data["symbol"], "BTC")

    def test_post_investment_position_contract_invalid_payload(self):
        """Test POST /api/investments/positions validates request payload"""

        invalid_payloads = [
            {},  # Empty payload
            {"asset_type": "stock"},  # Missing symbol
            {"symbol": "AAPL"},  # Missing asset_type
            {"asset_type": "invalid", "symbol": "AAPL"},  # Invalid asset_type
            {"asset_type": "stock", "symbol": ""},  # Empty symbol
            {"asset_type": "stock", "symbol": None},  # Null symbol
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

    def test_post_investment_position_contract_duplicate_position(self):
        """Test POST /api/investments/positions handles duplicate asset_type + symbol combination"""

        # This test will FAIL until the endpoint is implemented
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 409
            mock_response.json.return_value = {
                "error": "Investment position already exists for this asset"
            }
            mock_post.return_value = mock_response

            # Make request
            import requests
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json=self.valid_stock_payload,
                headers={"Content-Type": "application/json"}
            )

            # Assertions
            self.assertEqual(response.status_code, 409)
            data = response.json()
            self.assertIn("error", data)

    def test_post_investment_position_contract_asset_type_validation(self):
        """Test POST /api/investments/positions validates asset_type enum values"""

        valid_asset_types = ["stock", "crypto"]
        invalid_asset_types = ["bond", "real_estate", "commodity", "invalid"]

        # Test valid asset types
        for asset_type in valid_asset_types:
            payload = {"asset_type": asset_type, "symbol": "TEST"}
            expected_response = {
                "id": 1,
                "asset_type": asset_type,
                "symbol": "TEST",
                "current_quantity": 0.0,
                "current_value": 0.0,
                "profit_loss": 0.0,
                "created_at": "2025-09-20T10:30:00Z",
                "updated_at": "2025-09-20T10:30:00Z"
            }

            with self.subTest(asset_type=asset_type, valid=True):
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

        # Test invalid asset types
        for asset_type in invalid_asset_types:
            payload = {"asset_type": asset_type, "symbol": "TEST"}

            with self.subTest(asset_type=asset_type, valid=False):
                with patch('requests.post') as mock_post:
                    mock_response = Mock()
                    mock_response.status_code = 400
                    mock_response.json.return_value = {"error": "Invalid asset_type"}
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

    def test_post_investment_position_contract_symbol_format(self):
        """Test POST /api/investments/positions validates symbol format"""

        valid_symbols = ["AAPL", "MSFT", "BTC", "ETH", "GOOGL"]

        for symbol in valid_symbols:
            payload = {"asset_type": "stock", "symbol": symbol}
            expected_response = {
                "id": 1,
                "asset_type": "stock",
                "symbol": symbol,
                "current_quantity": 0.0,
                "current_value": 0.0,
                "profit_loss": 0.0,
                "created_at": "2025-09-20T10:30:00Z",
                "updated_at": "2025-09-20T10:30:00Z"
            }

            with self.subTest(symbol=symbol):
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
                    self.assertEqual(data["symbol"], symbol)

    def test_post_investment_position_contract_content_type(self):
        """Test POST /api/investments/positions requires correct Content-Type header"""

        # This test will FAIL until the endpoint is implemented
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Content-Type must be application/json"}
            mock_post.return_value = mock_response

            # Make request without proper Content-Type
            import requests
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                data=json.dumps(self.valid_stock_payload),
                headers={"Content-Type": "text/plain"}
            )

            # Assertions
            self.assertEqual(response.status_code, 400)

    def _validate_position_schema(self, data):
        """Helper method to validate investment position response schema"""
        self.assertIsInstance(data, dict)

        for field, expected_type in self.expected_position_schema.items():
            self.assertIn(field, data, f"Missing field: {field}")
            self.assertIsInstance(
                data[field], expected_type,
                f"Field {field} should be {expected_type}, got {type(data[field])}"
            )

        # Additional validations
        self.assertIn(data["asset_type"], ["stock", "crypto"])
        self.assertIsInstance(data["symbol"], str)
        self.assertGreater(len(data["symbol"]), 0)

if __name__ == '__main__':
    unittest.main()