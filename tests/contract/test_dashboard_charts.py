#!/usr/bin/env python3
"""
Contract test for GET /api/dashboard/charts
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

class TestDashboardChartsContract(unittest.TestCase):
    """Contract tests for GET /api/dashboard/charts endpoint"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8000"
        self.endpoint = "/api/dashboard/charts"

        # Expected response schema for ChartData object
        self.expected_chart_schema = {
            "chart_type": str,
            "labels": list,
            "datasets": list
        }

        # Expected dataset structure
        self.expected_dataset_schema = {
            "label": str,
            "data": list,
            "backgroundColor": str,
            "borderColor": str
        }

    def test_get_dashboard_charts_balance_trend_contract(self):
        """Test GET /api/dashboard/charts with chartType=balance_trend"""

        # Mock response data matching schema
        expected_response = {
            "chart_type": "balance_trend",
            "labels": ["2025-09-01", "2025-09-07", "2025-09-14", "2025-09-20"],
            "datasets": [
                {
                    "label": "Total Balance",
                    "data": [1000.00, 1150.00, 1050.00, 1200.00],
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "borderColor": "rgba(54, 162, 235, 1)"
                }
            ]
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"chartType": "balance_trend", "period": "month"}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate response structure
            self._validate_chart_schema(data)
            self.assertEqual(data["chart_type"], "balance_trend")

    def test_get_dashboard_charts_spending_categories_contract(self):
        """Test GET /api/dashboard/charts with chartType=spending_categories"""

        # Mock response data matching schema
        expected_response = {
            "chart_type": "spending_categories",
            "labels": ["Food", "Transportation", "Entertainment", "Shopping", "Utilities"],
            "datasets": [
                {
                    "label": "Monthly Spending",
                    "data": [450.00, 200.00, 150.00, 300.00, 180.00],
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "borderColor": "rgba(255, 99, 132, 1)"
                }
            ]
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"chartType": "spending_categories", "period": "month"}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate response structure
            self._validate_chart_schema(data)
            self.assertEqual(data["chart_type"], "spending_categories")

    def test_get_dashboard_charts_investment_performance_contract(self):
        """Test GET /api/dashboard/charts with chartType=investment_performance"""

        # Mock response data matching schema
        expected_response = {
            "chart_type": "investment_performance",
            "labels": ["AAPL", "MSFT", "BTC", "ETH"],
            "datasets": [
                {
                    "label": "Portfolio Value",
                    "data": [1500.00, 800.00, 2000.00, 600.00],
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "borderColor": "rgba(75, 192, 192, 1)"
                },
                {
                    "label": "Profit/Loss",
                    "data": [150.00, -50.00, 500.00, -100.00],
                    "backgroundColor": "rgba(153, 102, 255, 0.2)",
                    "borderColor": "rgba(153, 102, 255, 1)"
                }
            ]
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"chartType": "investment_performance", "period": "month"}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate response structure
            self._validate_chart_schema(data)
            self.assertEqual(data["chart_type"], "investment_performance")
            self.assertEqual(len(data["datasets"]), 2)  # Value and Profit/Loss

    def test_get_dashboard_charts_contract_invalid_chart_type(self):
        """Test GET /api/dashboard/charts with invalid chartType parameter"""

        invalid_chart_types = ["invalid_chart", "unknown", "balance", "spending"]

        for invalid_chart_type in invalid_chart_types:
            with self.subTest(chart_type=invalid_chart_type):
                # This test will FAIL until the endpoint is implemented
                with patch('requests.get') as mock_get:
                    mock_response = Mock()
                    mock_response.status_code = 400
                    mock_response.json.return_value = {"error": "Invalid chartType parameter"}
                    mock_get.return_value = mock_response

                    # Make request
                    import requests
                    response = requests.get(
                        f"{self.base_url}{self.endpoint}",
                        params={"chartType": invalid_chart_type, "period": "month"}
                    )

                    # Assertions
                    self.assertEqual(response.status_code, 400)

    def test_get_dashboard_charts_contract_period_validation(self):
        """Test GET /api/dashboard/charts with different period parameters"""

        valid_periods = ["week", "month", "quarter", "year"]
        invalid_periods = ["day", "decade", "invalid"]

        # Test valid periods
        for period in valid_periods:
            with self.subTest(period=period, valid=True):
                expected_response = {
                    "chart_type": "balance_trend",
                    "labels": ["Label1", "Label2"],
                    "datasets": [{
                        "label": "Test Data",
                        "data": [100, 200],
                        "backgroundColor": "rgba(54, 162, 235, 0.2)",
                        "borderColor": "rgba(54, 162, 235, 1)"
                    }]
                }

                with patch('requests.get') as mock_get:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = expected_response
                    mock_get.return_value = mock_response

                    # Make request
                    import requests
                    response = requests.get(
                        f"{self.base_url}{self.endpoint}",
                        params={"chartType": "balance_trend", "period": period}
                    )

                    # Assertions
                    self.assertEqual(response.status_code, 200)

        # Test invalid periods
        for period in invalid_periods:
            with self.subTest(period=period, valid=False):
                with patch('requests.get') as mock_get:
                    mock_response = Mock()
                    mock_response.status_code = 400
                    mock_response.json.return_value = {"error": "Invalid period parameter"}
                    mock_get.return_value = mock_response

                    # Make request
                    import requests
                    response = requests.get(
                        f"{self.base_url}{self.endpoint}",
                        params={"chartType": "balance_trend", "period": period}
                    )

                    # Assertions
                    self.assertEqual(response.status_code, 400)

    def test_get_dashboard_charts_contract_default_period(self):
        """Test GET /api/dashboard/charts uses default period when not specified"""

        expected_response = {
            "chart_type": "balance_trend",
            "labels": ["2025-09-01", "2025-09-07", "2025-09-14", "2025-09-20"],
            "datasets": [{
                "label": "Total Balance",
                "data": [1000.00, 1150.00, 1050.00, 1200.00],
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)"
            }]
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request without period parameter (should default to "month")
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"chartType": "balance_trend"}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self._validate_chart_schema(data)

    def test_get_dashboard_charts_contract_missing_chart_type(self):
        """Test GET /api/dashboard/charts when chartType parameter is missing"""

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "chartType parameter is required"}
            mock_get.return_value = mock_response

            # Make request without chartType parameter
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"period": "month"}
            )

            # Assertions
            self.assertEqual(response.status_code, 400)

    def test_get_dashboard_charts_contract_empty_data(self):
        """Test GET /api/dashboard/charts handles empty data gracefully"""

        expected_response = {
            "chart_type": "balance_trend",
            "labels": [],
            "datasets": [{
                "label": "Total Balance",
                "data": [],
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)"
            }]
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"chartType": "balance_trend", "period": "month"}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self._validate_chart_schema(data)
            self.assertEqual(len(data["labels"]), 0)
            self.assertEqual(len(data["datasets"][0]["data"]), 0)

    def test_get_dashboard_charts_contract_multiple_datasets(self):
        """Test GET /api/dashboard/charts handles multiple datasets correctly"""

        expected_response = {
            "chart_type": "investment_performance",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "datasets": [
                {
                    "label": "Stocks",
                    "data": [1000.00, 1200.00, 1100.00, 1300.00],
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "borderColor": "rgba(255, 99, 132, 1)"
                },
                {
                    "label": "Crypto",
                    "data": [500.00, 800.00, 600.00, 900.00],
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "borderColor": "rgba(54, 162, 235, 1)"
                }
            ]
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"chartType": "investment_performance", "period": "year"}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self._validate_chart_schema(data)
            self.assertEqual(len(data["datasets"]), 2)

            # Validate each dataset
            for dataset in data["datasets"]:
                self._validate_dataset_schema(dataset)

    def test_get_dashboard_charts_contract_color_consistency(self):
        """Test GET /api/dashboard/charts returns consistent color schemes"""

        expected_response = {
            "chart_type": "spending_categories",
            "labels": ["Food", "Transport"],
            "datasets": [{
                "label": "Spending",
                "data": [300.00, 150.00],
                "backgroundColor": "rgba(255, 99, 132, 0.2)",
                "borderColor": "rgba(255, 99, 132, 1)"
            }]
        }

        # This test will FAIL until the endpoint is implemented
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_get.return_value = mock_response

            # Make request
            import requests
            response = requests.get(
                f"{self.base_url}{self.endpoint}",
                params={"chartType": "spending_categories", "period": "month"}
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Validate color format (rgba)
            dataset = data["datasets"][0]
            self.assertTrue(dataset["backgroundColor"].startswith("rgba("))
            self.assertTrue(dataset["borderColor"].startswith("rgba("))

    def _validate_chart_schema(self, data):
        """Helper method to validate chart response schema"""
        self.assertIsInstance(data, dict)

        for field, expected_type in self.expected_chart_schema.items():
            self.assertIn(field, data, f"Missing field: {field}")
            self.assertIsInstance(
                data[field], expected_type,
                f"Field {field} should be {expected_type}, got {type(data[field])}"
            )

        # Validate chart_type is one of the allowed values
        valid_chart_types = ["balance_trend", "spending_categories", "investment_performance"]
        self.assertIn(data["chart_type"], valid_chart_types)

        # Validate datasets structure
        self.assertGreaterEqual(len(data["datasets"]), 1, "Must have at least one dataset")
        for dataset in data["datasets"]:
            self._validate_dataset_schema(dataset)

    def _validate_dataset_schema(self, dataset):
        """Helper method to validate dataset schema"""
        self.assertIsInstance(dataset, dict)

        for field, expected_type in self.expected_dataset_schema.items():
            self.assertIn(field, dataset, f"Missing dataset field: {field}")
            self.assertIsInstance(
                dataset[field], expected_type,
                f"Dataset field {field} should be {expected_type}, got {type(dataset[field])}"
            )

        # Validate data array contains numbers
        for value in dataset["data"]:
            self.assertIsInstance(value, (int, float), f"Data value should be numeric, got {type(value)}")

if __name__ == '__main__':
    unittest.main()