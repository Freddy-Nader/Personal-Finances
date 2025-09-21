#!/usr/bin/env python3
"""
Integration Test: Time-based Analytics Workflow
Tests the complete time-based analytics user story including dashboard filtering and profit/loss calculations.
"""

import unittest
import json
import sqlite3
import os
import sys
from datetime import datetime, timedelta
import http.client

# Add backend src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend/src'))

from database.init_db import initialize_database


class TestTimeAnalyticsWorkflow(unittest.TestCase):
    """Integration tests for time-based analytics workflow from quickstart.md"""

    def setUp(self):
        """Set up test database and server connection"""
        self.test_db_path = "./test_data/test_time_analytics.db"
        os.makedirs("./test_data", exist_ok=True)

        # Remove existing test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        # Initialize fresh test database
        initialize_database(self.test_db_path)

        # Server connection for API tests
        self.server_host = "localhost"
        self.server_port = 8000

    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def _make_api_request(self, method, path, data=None):
        """Helper method to make API requests"""
        try:
            conn = http.client.HTTPConnection(self.server_host, self.server_port)
            headers = {'Content-Type': 'application/json'}

            if data:
                data = json.dumps(data)

            conn.request(method, f"/api{path}", data, headers)
            response = conn.getresponse()

            response_data = response.read().decode()
            conn.close()

            # Parse JSON response if available
            try:
                response_data = json.loads(response_data) if response_data else None
            except json.JSONDecodeError:
                pass

            return response.status, response_data
        except ConnectionRefusedError:
            self.skipTest("Server not running - start with 'python backend/src/server.py'")

    def _create_sample_data(self):
        """Create sample data spanning multiple months for testing"""
        base_date = datetime.now()

        # Create cards
        card_data = [
            {"name": "Checking Account", "type": "debit", "balance": 5000.00},
            {"name": "Credit Card", "type": "credit", "credit_limit": 3000.00}
        ]

        card_ids = []
        for card in card_data:
            status, response = self._make_api_request("POST", "/cards", card)
            self.assertEqual(status, 201)
            card_ids.append(response["id"])

        # Create investment positions
        position_data = [
            {"asset_type": "stock", "symbol": "AAPL"},
            {"asset_type": "crypto", "symbol": "BTC"}
        ]

        position_ids = []
        for position in position_data:
            status, response = self._make_api_request("POST", "/investments/positions", position)
            self.assertEqual(status, 201)
            position_ids.append(response["id"])

        # Create transactions spanning multiple months
        transactions = [
            # 3 months ago
            {"amount": -500.00, "description": "Rent", "transaction_date": (base_date - timedelta(days=90)).isoformat(), "card_id": card_ids[0], "category": "Housing"},
            {"amount": -200.00, "description": "Groceries", "transaction_date": (base_date - timedelta(days=85)).isoformat(), "card_id": card_ids[0], "category": "Food"},
            {"amount": 3000.00, "description": "Salary", "transaction_date": (base_date - timedelta(days=80)).isoformat(), "card_id": card_ids[0], "category": "Income"},

            # 2 months ago
            {"amount": -500.00, "description": "Rent", "transaction_date": (base_date - timedelta(days=60)).isoformat(), "card_id": card_ids[0], "category": "Housing"},
            {"amount": -150.00, "description": "Utilities", "transaction_date": (base_date - timedelta(days=55)).isoformat(), "card_id": card_ids[1], "category": "Utilities"},
            {"amount": 3000.00, "description": "Salary", "transaction_date": (base_date - timedelta(days=50)).isoformat(), "card_id": card_ids[0], "category": "Income"},

            # 1 month ago
            {"amount": -500.00, "description": "Rent", "transaction_date": (base_date - timedelta(days=30)).isoformat(), "card_id": card_ids[0], "category": "Housing"},
            {"amount": -300.00, "description": "Shopping", "transaction_date": (base_date - timedelta(days=25)).isoformat(), "card_id": card_ids[1], "category": "Shopping"},
            {"amount": 3000.00, "description": "Salary", "transaction_date": (base_date - timedelta(days=20)).isoformat(), "card_id": card_ids[0], "category": "Income"},

            # Current month
            {"amount": -500.00, "description": "Rent", "transaction_date": (base_date - timedelta(days=5)).isoformat(), "card_id": card_ids[0], "category": "Housing"},
            {"amount": -100.00, "description": "Gas", "transaction_date": (base_date - timedelta(days=3)).isoformat(), "card_id": card_ids[0], "category": "Transportation"},
            {"amount": 3000.00, "description": "Salary", "transaction_date": base_date.isoformat(), "card_id": card_ids[0], "category": "Income"},
        ]

        for transaction in transactions:
            status, response = self._make_api_request("POST", "/transactions", transaction)
            self.assertEqual(status, 201)

        # Create investment movements spanning time
        movements = [
            # 2 months ago
            {"position_id": position_ids[0], "movement_type": "buy", "quantity": 10.0, "price_per_unit": 150.00, "movement_datetime": (base_date - timedelta(days=60)).isoformat(), "description": "AAPL buy"},
            {"position_id": position_ids[1], "movement_type": "buy", "quantity": 0.1, "price_per_unit": 45000.00, "movement_datetime": (base_date - timedelta(days=55)).isoformat(), "description": "BTC buy"},

            # 1 month ago
            {"position_id": position_ids[0], "movement_type": "buy", "quantity": 5.0, "price_per_unit": 160.00, "movement_datetime": (base_date - timedelta(days=30)).isoformat(), "description": "AAPL additional buy"},

            # Recent
            {"position_id": position_ids[0], "movement_type": "sell", "quantity": 3.0, "price_per_unit": 170.00, "movement_datetime": (base_date - timedelta(days=5)).isoformat(), "description": "AAPL partial sell"},
        ]

        for movement in movements:
            status, response = self._make_api_request("POST", "/investments/movements", movement)
            self.assertEqual(status, 201)

        return card_ids, position_ids

    def test_dashboard_summary_periods(self):
        """Test dashboard summary for different time periods"""
        # Create sample data
        self._create_sample_data()

        # Test different time periods
        periods = ["week", "month", "quarter", "year"]

        for period in periods:
            status, response = self._make_api_request("GET", f"/dashboard/summary?period={period}")
            self.assertEqual(status, 200, f"Failed to get dashboard summary for period: {period}")

            # Verify response structure
            self.assertIsInstance(response, dict)
            required_fields = [
                "total_balance", "total_credit_available", "total_investments_value",
                "period_income", "period_expenses", "period_profit_loss"
            ]

            for field in required_fields:
                self.assertIn(field, response, f"Missing field {field} in {period} summary")
                self.assertIsInstance(response[field], (int, float), f"Field {field} should be numeric")

    def test_weekly_analytics_workflow(self):
        """Test weekly view analytics"""
        # Create sample data
        self._create_sample_data()

        # Get weekly summary
        status, response = self._make_api_request("GET", "/dashboard/summary?period=week")
        self.assertEqual(status, 200)

        # Should show data for last 7 days
        self.assertGreaterEqual(response["period_income"], 0)
        self.assertLessEqual(response["period_expenses"], 0)  # Expenses are negative

        # Get weekly chart data
        status, response = self._make_api_request("GET", "/dashboard/charts?chartType=balance_trend&period=week")
        self.assertEqual(status, 200)

        # Verify chart structure
        self.assertIn("chart_type", response)
        self.assertIn("labels", response)
        self.assertIn("datasets", response)
        self.assertEqual(response["chart_type"], "balance_trend")

    def test_monthly_analytics_workflow(self):
        """Test monthly view analytics"""
        # Create sample data
        self._create_sample_data()

        # Get monthly summary
        status, response = self._make_api_request("GET", "/dashboard/summary?period=month")
        self.assertEqual(status, 200)

        # Monthly should show larger amounts than weekly
        monthly_income = response["period_income"]
        monthly_expenses = response["period_expenses"]

        # Get weekly for comparison
        status, weekly_response = self._make_api_request("GET", "/dashboard/summary?period=week")
        self.assertEqual(status, 200)

        # Monthly should generally have more activity than weekly
        self.assertGreaterEqual(monthly_income, weekly_response["period_income"])

    def test_quarterly_analytics_workflow(self):
        """Test quarterly view analytics"""
        # Create sample data
        self._create_sample_data()

        # Get quarterly summary
        status, response = self._make_api_request("GET", "/dashboard/summary?period=quarter")
        self.assertEqual(status, 200)

        # Verify quarterly calculations
        self.assertIsInstance(response["period_income"], (int, float))
        self.assertIsInstance(response["period_expenses"], (int, float))
        self.assertIsInstance(response["period_profit_loss"], (int, float))

        # Profit/loss should be income + expenses (expenses are negative)
        calculated_pnl = response["period_income"] + response["period_expenses"]
        self.assertAlmostEqual(response["period_profit_loss"], calculated_pnl, places=2)

    def test_yearly_analytics_workflow(self):
        """Test yearly view analytics"""
        # Create sample data
        self._create_sample_data()

        # Get yearly summary
        status, response = self._make_api_request("GET", "/dashboard/summary?period=year")
        self.assertEqual(status, 200)

        # Yearly should encompass all our test data
        self.assertGreater(response["period_income"], 0)
        self.assertLess(response["period_expenses"], 0)

    def test_chart_data_periods(self):
        """Test chart data for different periods"""
        # Create sample data
        self._create_sample_data()

        chart_types = ["balance_trend", "spending_categories", "investment_performance"]
        periods = ["week", "month", "quarter", "year"]

        for chart_type in chart_types:
            for period in periods:
                status, response = self._make_api_request("GET", f"/dashboard/charts?chartType={chart_type}&period={period}")
                self.assertEqual(status, 200, f"Failed to get {chart_type} chart for {period}")

                # Verify chart structure
                self.assertIn("chart_type", response)
                self.assertIn("labels", response)
                self.assertIn("datasets", response)
                self.assertEqual(response["chart_type"], chart_type)

                # Verify data structure
                self.assertIsInstance(response["labels"], list)
                self.assertIsInstance(response["datasets"], list)

                if response["datasets"]:
                    dataset = response["datasets"][0]
                    self.assertIn("label", dataset)
                    self.assertIn("data", dataset)
                    self.assertIsInstance(dataset["data"], list)

    def test_profit_loss_calculations(self):
        """Test profit/loss calculations across periods"""
        # Create sample data with known amounts
        self._create_sample_data()

        # Test each period and verify profit/loss calculation
        periods = ["week", "month", "quarter", "year"]

        for period in periods:
            status, response = self._make_api_request("GET", f"/dashboard/summary?period={period}")
            self.assertEqual(status, 200)

            income = response["period_income"]
            expenses = response["period_expenses"]
            profit_loss = response["period_profit_loss"]

            # Verify calculation: profit_loss = income + expenses (expenses are negative)
            expected_pnl = income + expenses
            self.assertAlmostEqual(profit_loss, expected_pnl, places=2,
                                 msg=f"Profit/loss calculation incorrect for {period}: {profit_loss} != {expected_pnl}")

    def test_time_filtering_performance(self):
        """Test that time period filtering responds quickly"""
        # Create sample data
        self._create_sample_data()

        import time

        # Test response time for each period
        periods = ["week", "month", "quarter", "year"]

        for period in periods:
            start_time = time.time()
            status, response = self._make_api_request("GET", f"/dashboard/summary?period={period}")
            end_time = time.time()

            self.assertEqual(status, 200)

            # Response should be under 100ms as per constitutional requirements
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            self.assertLess(response_time, 100, f"Response time {response_time}ms exceeds 100ms limit for {period}")

    def test_comprehensive_time_analytics_workflow(self):
        """Test complete time-based analytics workflow as described in quickstart"""
        # Step 1: Create sample data spanning multiple months
        card_ids, position_ids = self._create_sample_data()

        # Step 2: Test weekly view (last 4 weeks)
        status, response = self._make_api_request("GET", "/dashboard/summary?period=week")
        self.assertEqual(status, 200)
        weekly_summary = response

        status, response = self._make_api_request("GET", "/dashboard/charts?chartType=balance_trend&period=week")
        self.assertEqual(status, 200)
        weekly_chart = response

        # Step 3: Test monthly view (last 6 months)
        status, response = self._make_api_request("GET", "/dashboard/summary?period=month")
        self.assertEqual(status, 200)
        monthly_summary = response

        status, response = self._make_api_request("GET", "/dashboard/charts?chartType=spending_categories&period=month")
        self.assertEqual(status, 200)
        monthly_chart = response

        # Step 4: Test quarterly view (last 4 quarters)
        status, response = self._make_api_request("GET", "/dashboard/summary?period=quarter")
        self.assertEqual(status, 200)
        quarterly_summary = response

        # Step 5: Test yearly view (last 3 years)
        status, response = self._make_api_request("GET", "/dashboard/summary?period=year")
        self.assertEqual(status, 200)
        yearly_summary = response

        # Step 6: Verify chart data updates correctly
        # Charts should have different data points for different periods
        self.assertNotEqual(weekly_chart["labels"], monthly_chart["labels"])

        # Step 7: Verify profit/loss calculations are accurate for all periods
        for period, summary in [("week", weekly_summary), ("month", monthly_summary),
                               ("quarter", quarterly_summary), ("year", yearly_summary)]:
            income = summary["period_income"]
            expenses = summary["period_expenses"]
            profit_loss = summary["period_profit_loss"]

            expected_pnl = income + expenses
            self.assertAlmostEqual(profit_loss, expected_pnl, places=2,
                                 msg=f"P&L calculation incorrect for {period}")

        # Step 8: Verify performance requirements
        # All responses should be under 100ms
        import time
        start_time = time.time()
        status, response = self._make_api_request("GET", "/dashboard/summary?period=month")
        end_time = time.time()

        response_time = (end_time - start_time) * 1000
        self.assertLess(response_time, 100, "Filter change response time exceeds 100ms requirement")

    def test_empty_data_periods(self):
        """Test analytics with no data for certain periods"""
        # Don't create any sample data - test with empty database

        periods = ["week", "month", "quarter", "year"]

        for period in periods:
            # Should handle empty data gracefully
            status, response = self._make_api_request("GET", f"/dashboard/summary?period={period}")
            self.assertEqual(status, 200)

            # All values should be 0 for empty data
            self.assertEqual(response["total_balance"], 0)
            self.assertEqual(response["period_income"], 0)
            self.assertEqual(response["period_expenses"], 0)
            self.assertEqual(response["period_profit_loss"], 0)

    def test_invalid_period_handling(self):
        """Test handling of invalid period parameters"""
        invalid_periods = ["invalid", "daily", "hourly", ""]

        for invalid_period in invalid_periods:
            status, response = self._make_api_request("GET", f"/dashboard/summary?period={invalid_period}")
            # Should either default to valid period or return 400
            self.assertIn(status, [200, 400])

            if status == 200:
                # If it defaults, should have valid response structure
                self.assertIn("period_income", response)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)