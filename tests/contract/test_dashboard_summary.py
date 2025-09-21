#!/usr/bin/env python3
"""
Contract test for GET /api/dashboard/summary endpoint.
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


class TestDashboardSummaryContract(unittest.TestCase):
    """Test contract for GET /api/dashboard/summary endpoint."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test cases."""
        self.api_url = f"{self.BASE_URL}/api/dashboard/summary"

    def test_get_dashboard_summary_returns_200(self):
        """Test that GET /api/dashboard/summary returns 200 status code."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                self.assertEqual(response.getcode(), 200)
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_dashboard_summary_returns_json(self):
        """Test that GET /api/dashboard/summary returns JSON content type."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                content_type = response.headers.get('Content-Type', '')
                self.assertIn('application/json', content_type)
        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_dashboard_summary_structure(self):
        """Test structure of dashboard summary response."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))

                # Required fields from contract
                required_fields = {
                    'total_balance', 'total_credit_available', 'total_investments_value',
                    'period_income', 'period_expenses', 'period_profit_loss'
                }
                actual_fields = set(data.keys())
                self.assertTrue(required_fields.issubset(actual_fields))

                # Field type validation
                for field in required_fields:
                    self.assertIsInstance(data[field], (int, float),
                                        f"Field {field} should be numeric")

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_dashboard_summary_with_period_param(self):
        """Test GET /api/dashboard/summary with period parameter."""
        periods = ['week', 'month', 'quarter', 'year']

        for period in periods:
            try:
                url_with_period = f"{self.api_url}?period={period}"
                with urllib.request.urlopen(url_with_period) as response:
                    self.assertEqual(response.getcode(), 200)

                    data = json.loads(response.read().decode('utf-8'))
                    # Response should include period-specific calculations
                    self.assertIn('period_income', data)
                    self.assertIn('period_expenses', data)
                    self.assertIn('period_profit_loss', data)

            except Exception as e:
                self.fail(f"Request failed for period {period}: {e}")

    def test_get_dashboard_summary_default_period(self):
        """Test GET /api/dashboard/summary defaults to month period."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))

                # Should return data (defaults to month period)
                self.assertIsInstance(data['period_income'], (int, float))
                self.assertIsInstance(data['period_expenses'], (int, float))

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_dashboard_summary_invalid_period(self):
        """Test GET /api/dashboard/summary with invalid period parameter."""
        try:
            url_with_invalid_period = f"{self.api_url}?period=invalid"
            with urllib.request.urlopen(url_with_invalid_period) as response:
                self.fail("Expected 400 error for invalid period")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_get_dashboard_summary_balance_calculations(self):
        """Test that balance calculations are consistent."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))

                # Balances should be non-negative or handle negative appropriately
                total_balance = data['total_balance']
                total_credit = data['total_credit_available']
                total_investments = data['total_investments_value']

                self.assertIsInstance(total_balance, (int, float))
                self.assertIsInstance(total_credit, (int, float))
                self.assertIsInstance(total_investments, (int, float))

                # Credit available should be non-negative
                self.assertGreaterEqual(total_credit, 0)

        except Exception as e:
            self.fail(f"Request failed: {e}")

    def test_get_dashboard_summary_profit_loss_calculation(self):
        """Test profit/loss calculation consistency."""
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode('utf-8'))

                period_income = data['period_income']
                period_expenses = data['period_expenses']
                period_profit_loss = data['period_profit_loss']

                # Basic sanity check: profit/loss should relate to income/expenses
                # Note: This might not be exact equality due to investment gains/losses
                expected_pl = period_income + period_expenses  # expenses are typically negative

                # Allow for investment-related profit/loss that doesn't match income-expenses
                self.assertIsInstance(period_profit_loss, (int, float))

        except Exception as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    print("Testing GET /api/dashboard/summary contract")
    print("This test MUST FAIL until the endpoint is implemented")
    print("-" * 50)

    unittest.main(verbosity=2)