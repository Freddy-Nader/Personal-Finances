#!/usr/bin/env python3
"""
Contract test for GET /api/investments/positions endpoint.
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


class TestPositionsGetContract(unittest.TestCase):
    """Test contract for GET /api/investments/positions endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_url = f"{self.BASE_URL}/api/investments/positions"

    def test_get_positions_returns_200(self):
        """Test that GET /api/investments/positions returns 200 status code."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                self.assertEqual(response.getcode(), 200)
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_positions_returns_json(self):
        """Test that GET /api/investments/positions returns JSON content type."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                content_type = response.headers.get('Content-Type', '')
                self.assertIn('application/json', content_type)
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_positions_returns_array(self):
        """Test that GET /api/investments/positions returns an array."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))
                self.assertIsInstance(data, list)
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_positions_structure_validation(self):
        """Test structure of position objects in response."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))

                if len(data) > 0:
                    position = data[0]

                    # Required fields from contract
                    required_fields = {
                        'id', 'asset_type', 'symbol', 'current_quantity',
                        'current_value', 'profit_loss', 'created_at', 'updated_at'
                    }
                    actual_fields = set(position.keys())
                    self.assertTrue(required_fields.issubset(actual_fields))

                    # Field type validation
                    self.assertIsInstance(position['id'], int)
                    self.assertIn(position['asset_type'], ['stock', 'crypto'])
                    self.assertIsInstance(position['symbol'], str)
                    self.assertIsInstance(position['current_quantity'], (int, float))
                    self.assertIsInstance(position['current_value'], (int, float))
                    self.assertIsInstance(position['profit_loss'], (int, float))

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_positions_asset_type_validation(self):
        """Test that asset_type field contains valid values."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))

                for position in data:
                    self.assertIn(position['asset_type'], ['stock', 'crypto'])

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_positions_symbol_format(self):
        """Test that symbol field is properly formatted."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))

                for position in data:
                    symbol = position['symbol']
                    self.assertIsInstance(symbol, str)
                    self.assertGreater(len(symbol), 0)
                    # Symbol should be uppercase for stocks/crypto
                    self.assertEqual(symbol, symbol.upper())

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    print("Testing GET /api/investments/positions contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)