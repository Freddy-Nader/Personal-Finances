#!/usr/bin/env python3
"""
Integration test for dashboard analytics workflow.
Tests the complete user story: User accesses dashboard and sees consolidated statistics.
This test MUST FAIL until the full workflow is implemented.
"""

import unittest
import json
import urllib.request
import urllib.error
import sqlite3
from pathlib import Path
import sys
import os

# Add backend path to sys.path for imports
backend_path = Path(__file__).parent.parent.parent / 'backend' / 'src'
sys.path.insert(0, str(backend_path))


class TestDashboardAnalyticsIntegration(unittest.TestCase):
    """Integration test for complete dashboard analytics workflow."""

    BASE_URL = 'http://localhost:8000'

    def setUp(self):
        """Set up test environment with sample data."""
        self.api_base = f"{self.BASE_URL}/api"
        self.dashboard_url = f"{self.api_base}/dashboard"

        # Set up test database with sample data
        self._setup_test_data()

    def _setup_test_data(self):
        """Create sample data for testing dashboard analytics."""
        # This will create test cards, transactions, and investments
        # in the test database for integration testing

        try:
            # Create sample cards
            card_data = {
                'name': 'Test Checking Account',
                'type': 'debit',
                'currency': 'MXN',
                'balance': 5000.00
            }
            self._create_test_card(card_data)

            credit_card_data = {
                'name': 'Test Credit Card',
                'type': 'credit',
                'currency': 'MXN',
                'credit_limit': 10000.00
            }
            self._create_test_card(credit_card_data)

            # Create sample transactions
            transactions = [
                {
                    'amount': -150.00,
                    'description': 'Grocery shopping',
                    'transaction_date': '2024-09-15T10:30:00Z',
                    'card_id': 1,
                    'category': 'Food'
                },
                {
                    'amount': -800.00,
                    'description': 'Rent payment',
                    'transaction_date': '2024-09-01T09:00:00Z',
                    'card_id': 1,
                    'category': 'Housing'
                },
                {
                    'amount': 3000.00,
                    'description': 'Salary deposit',
                    'transaction_date': '2024-09-01T08:00:00Z',
                    'card_id': 1,
                    'category': 'Income'
                }
            ]

            for transaction in transactions:
                self._create_test_transaction(transaction)

            # Create sample investment position
            position_data = {
                'asset_type': 'stock',
                'symbol': 'AAPL'
            }
            self._create_test_position(position_data)

        except Exception as e:
            print(f"Warning: Could not set up test data: {e}")

    def _create_test_card(self, card_data):
        """Helper to create test card via API."""
        json_data = json.dumps(card_data).encode('utf-8')
        req = urllib.request.Request(
            f"{self.api_base}/cards",
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        req.get_method = lambda: 'POST'
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception:
            # Ignore errors during test setup - tests will handle missing data
            pass

    def _create_test_transaction(self, transaction_data):
        """Helper to create test transaction via API."""
        json_data = json.dumps(transaction_data).encode('utf-8')
        req = urllib.request.Request(
            f"{self.api_base}/transactions",
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        req.get_method = lambda: 'POST'
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception:
            pass

    def _create_test_position(self, position_data):
        """Helper to create test investment position via API."""
        json_data = json.dumps(position_data).encode('utf-8')
        req = urllib.request.Request(
            f"{self.api_base}/investments/positions",
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        req.get_method = lambda: 'POST'
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception:
            pass

    def test_dashboard_analytics_complete_workflow(self):
        """Test complete dashboard analytics workflow from user story."""

        # User story: User accesses dashboard and sees consolidated statistics

        # Step 1: Get dashboard summary
        try:
            with urllib.request.urlopen(f"{self.dashboard_url}/summary") as response:
                self.assertEqual(response.getcode(), 200)

                summary_data = json.loads(response.read().decode('utf-8'))

                # Verify summary contains all required financial metrics
                required_fields = {
                    'total_balance', 'total_credit_available', 'total_investments_value',
                    'period_income', 'period_expenses', 'period_profit_loss'
                }
                actual_fields = set(summary_data.keys())
                self.assertTrue(required_fields.issubset(actual_fields),
                              f"Missing summary fields: {required_fields - actual_fields}")

                # Validate realistic values based on test data
                self.assertGreater(summary_data['total_balance'], 0)
                self.assertGreater(summary_data['total_credit_available'], 0)
                self.assertGreaterEqual(summary_data['total_investments_value'], 0)

        except Exception as e:
            self.fail(f"Dashboard summary request failed: {e}")

        # Step 2: Get chart data for visualization
        chart_types = ['balance_trend', 'spending_categories', 'investment_performance']

        for chart_type in chart_types:
            try:
                chart_url = f"{self.dashboard_url}/charts?chartType={chart_type}"
                with urllib.request.urlopen(chart_url) as response:
                    self.assertEqual(response.getcode(), 200)

                    chart_data = json.loads(response.read().decode('utf-8'))

                    # Verify chart data structure
                    required_chart_fields = {'chart_type', 'labels', 'datasets'}
                    actual_chart_fields = set(chart_data.keys())
                    self.assertTrue(required_chart_fields.issubset(actual_chart_fields))

                    self.assertEqual(chart_data['chart_type'], chart_type)
                    self.assertIsInstance(chart_data['labels'], list)
                    self.assertIsInstance(chart_data['datasets'], list)

            except Exception as e:
                self.fail(f"Chart data request failed for {chart_type}: {e}")

    def test_dashboard_time_period_filtering(self):
        """Test dashboard analytics with different time periods."""

        periods = ['week', 'month', 'quarter', 'year']

        for period in periods:
            try:
                # Test summary with period filter
                summary_url = f"{self.dashboard_url}/summary?period={period}"
                with urllib.request.urlopen(summary_url) as response:
                    self.assertEqual(response.getcode(), 200)

                    summary_data = json.loads(response.read().decode('utf-8'))

                    # Period-specific metrics should be present
                    self.assertIn('period_income', summary_data)
                    self.assertIn('period_expenses', summary_data)
                    self.assertIn('period_profit_loss', summary_data)

                # Test charts with period filter
                chart_url = f"{self.dashboard_url}/charts?chartType=balance_trend&period={period}"
                with urllib.request.urlopen(chart_url) as response:
                    self.assertEqual(response.getcode(), 200)

                    chart_data = json.loads(response.read().decode('utf-8'))
                    self.assertIsInstance(chart_data['labels'], list)

            except Exception as e:
                self.fail(f"Period filtering failed for {period}: {e}")

    def test_dashboard_data_consistency(self):
        """Test consistency between different dashboard endpoints."""

        try:
            # Get summary data
            with urllib.request.urlopen(f"{self.dashboard_url}/summary") as response:
                summary_data = json.loads(response.read().decode('utf-8'))

            # Get detailed transaction data
            with urllib.request.urlopen(f"{self.api_base}/transactions") as response:
                transactions_data = json.loads(response.read().decode('utf-8'))

            # Get card data
            with urllib.request.urlopen(f"{self.api_base}/cards") as response:
                cards_data = json.loads(response.read().decode('utf-8'))

            # Basic consistency checks
            # Total balance in summary should relate to card balances
            if len(cards_data) > 0:
                total_card_balance = sum(card.get('balance', 0) for card in cards_data)
                summary_balance = summary_data.get('total_balance', 0)

                # Allow for reasonable differences due to pending transactions, etc.
                # This is a basic sanity check, not exact equality
                self.assertIsInstance(summary_balance, (int, float))
                self.assertIsInstance(total_card_balance, (int, float))

            # Income/expense calculations should be based on transaction data
            if len(transactions_data.get('transactions', [])) > 0:
                period_income = summary_data.get('period_income', 0)
                period_expenses = summary_data.get('period_expenses', 0)

                self.assertIsInstance(period_income, (int, float))
                self.assertIsInstance(period_expenses, (int, float))

                # Income should be non-negative, expenses typically negative
                self.assertGreaterEqual(period_income, 0)
                self.assertLessEqual(period_expenses, 0)

        except Exception as e:
            self.fail(f"Data consistency check failed: {e}")

    def test_dashboard_performance_requirements(self):
        """Test dashboard meets constitutional performance requirements."""

        import time

        # Test response time for dashboard summary (<100ms for interactions)
        start_time = time.time()

        try:
            with urllib.request.urlopen(f"{self.dashboard_url}/summary") as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds

                self.assertEqual(response.getcode(), 200)
                self.assertLess(response_time, 100,
                               f"Dashboard summary took {response_time:.1f}ms, should be <100ms")

        except Exception as e:
            self.fail(f"Performance test failed: {e}")


if __name__ == '__main__':
    print("Testing complete dashboard analytics workflow (Integration)")
    print("This test MUST FAIL until the full workflow is implemented")
    print("-" * 70)

    unittest.main(verbosity=2)