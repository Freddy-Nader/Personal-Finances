#!/usr/bin/env python3
"""
Performance test for interaction response times - Constitutional requirement: <100ms
Tests that all user interactions respond within 100ms as per constitutional requirements.
"""

import time
import unittest
import requests
import subprocess
import json
import os
from urllib.parse import urljoin


class InteractionResponseTest(unittest.TestCase):
    """Test interaction response times meet constitutional requirements (<100ms)"""

    @classmethod
    def setUpClass(cls):
        """Start the server for testing"""
        cls.server_process = None
        cls.base_url = "http://localhost:8000"
        cls.max_response_time = 0.1  # Constitutional requirement: <100ms

        # Start server in background
        cls._start_server()
        cls._wait_for_server()

    @classmethod
    def tearDownClass(cls):
        """Stop the test server"""
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()

    @classmethod
    def _start_server(cls):
        """Start the backend server for testing"""
        try:
            cls.server_process = subprocess.Popen(
                ["python", "backend/src/server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "SERVER_PORT": "8000"}
            )
        except Exception as e:
            print(f"Failed to start server: {e}")

    @classmethod
    def _wait_for_server(cls):
        """Wait for server to be ready"""
        max_wait = 10  # seconds
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{cls.base_url}/", timeout=1)
                if response.status_code in [200, 404]:  # Server is responding
                    return
            except requests.exceptions.RequestException:
                time.sleep(0.5)

        raise Exception("Server failed to start within timeout")

    def test_api_cards_get_response_time(self):
        """Test GET /api/cards responds within 100ms"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/api/cards", timeout=1)
            response_time = time.time() - start_time

            self.assertLess(response_time, self.max_response_time,
                          f"GET /api/cards response time {response_time*1000:.1f}ms exceeds constitutional requirement of {self.max_response_time*1000}ms")

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            # Allow for 404 or other expected errors, focus on response time
            self.assertLess(response_time, self.max_response_time,
                          f"GET /api/cards response time {response_time*1000:.1f}ms exceeds constitutional requirement even with error: {e}")

    def test_api_cards_post_response_time(self):
        """Test POST /api/cards responds within 100ms"""
        card_data = {
            "name": "Test Card",
            "type": "debit",
            "currency": "MXN",
            "balance": 1000.00
        }

        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/api/cards",
                json=card_data,
                headers={"Content-Type": "application/json"},
                timeout=1
            )
            response_time = time.time() - start_time

            self.assertLess(response_time, self.max_response_time,
                          f"POST /api/cards response time {response_time*1000:.1f}ms exceeds constitutional requirement of {self.max_response_time*1000}ms")

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.assertLess(response_time, self.max_response_time,
                          f"POST /api/cards response time {response_time*1000:.1f}ms exceeds constitutional requirement even with error: {e}")

    def test_api_transactions_get_response_time(self):
        """Test GET /api/transactions responds within 100ms"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/api/transactions", timeout=1)
            response_time = time.time() - start_time

            self.assertLess(response_time, self.max_response_time,
                          f"GET /api/transactions response time {response_time*1000:.1f}ms exceeds constitutional requirement of {self.max_response_time*1000}ms")

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.assertLess(response_time, self.max_response_time,
                          f"GET /api/transactions response time {response_time*1000:.1f}ms exceeds constitutional requirement even with error: {e}")

    def test_api_transactions_post_response_time(self):
        """Test POST /api/transactions responds within 100ms"""
        transaction_data = {
            "amount": -50.00,
            "description": "Test transaction",
            "transaction_date": "2024-01-01T12:00:00Z",
            "category": "test"
        }

        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/api/transactions",
                json=transaction_data,
                headers={"Content-Type": "application/json"},
                timeout=1
            )
            response_time = time.time() - start_time

            self.assertLess(response_time, self.max_response_time,
                          f"POST /api/transactions response time {response_time*1000:.1f}ms exceeds constitutional requirement of {self.max_response_time*1000}ms")

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.assertLess(response_time, self.max_response_time,
                          f"POST /api/transactions response time {response_time*1000:.1f}ms exceeds constitutional requirement even with error: {e}")

    def test_api_dashboard_summary_response_time(self):
        """Test GET /api/dashboard/summary responds within 100ms"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/api/dashboard/summary", timeout=1)
            response_time = time.time() - start_time

            self.assertLess(response_time, self.max_response_time,
                          f"GET /api/dashboard/summary response time {response_time*1000:.1f}ms exceeds constitutional requirement of {self.max_response_time*1000}ms")

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.assertLess(response_time, self.max_response_time,
                          f"GET /api/dashboard/summary response time {response_time*1000:.1f}ms exceeds constitutional requirement even with error: {e}")

    def test_api_dashboard_charts_response_time(self):
        """Test GET /api/dashboard/charts responds within 100ms"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/api/dashboard/charts", timeout=1)
            response_time = time.time() - start_time

            self.assertLess(response_time, self.max_response_time,
                          f"GET /api/dashboard/charts response time {response_time*1000:.1f}ms exceeds constitutional requirement of {self.max_response_time*1000}ms")

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.assertLess(response_time, self.max_response_time,
                          f"GET /api/dashboard/charts response time {response_time*1000:.1f}ms exceeds constitutional requirement even with error: {e}")

    def test_api_investments_positions_response_time(self):
        """Test GET /api/investments/positions responds within 100ms"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/api/investments/positions", timeout=1)
            response_time = time.time() - start_time

            self.assertLess(response_time, self.max_response_time,
                          f"GET /api/investments/positions response time {response_time*1000:.1f}ms exceeds constitutional requirement of {self.max_response_time*1000}ms")

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.assertLess(response_time, self.max_response_time,
                          f"GET /api/investments/positions response time {response_time*1000:.1f}ms exceeds constitutional requirement even with error: {e}")

    def test_batch_api_calls_response_time(self):
        """Test multiple API calls maintain response time requirements"""
        endpoints = [
            "/api/cards",
            "/api/transactions",
            "/api/investments/positions",
            "/api/investments/movements",
            "/api/dashboard/summary",
            "/api/dashboard/charts"
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                start_time = time.time()

                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=1)
                    response_time = time.time() - start_time

                    self.assertLess(response_time, self.max_response_time,
                                  f"GET {endpoint} response time {response_time*1000:.1f}ms exceeds constitutional requirement of {self.max_response_time*1000}ms")

                except requests.exceptions.RequestException as e:
                    response_time = time.time() - start_time
                    self.assertLess(response_time, self.max_response_time,
                                  f"GET {endpoint} response time {response_time*1000:.1f}ms exceeds constitutional requirement even with error: {e}")

    def test_static_file_response_time(self):
        """Test static files (CSS, JS) respond within 100ms"""
        static_files = [
            "/css/finance-app.css",
            "/js/api.js",
            "/js/components.js",
            "/js/utils.js"
        ]

        for file_path in static_files:
            with self.subTest(file=file_path):
                start_time = time.time()

                try:
                    response = requests.get(f"{self.base_url}{file_path}", timeout=1)
                    response_time = time.time() - start_time

                    self.assertLess(response_time, self.max_response_time,
                                  f"Static file {file_path} response time {response_time*1000:.1f}ms exceeds constitutional requirement of {self.max_response_time*1000}ms")

                except requests.exceptions.RequestException as e:
                    response_time = time.time() - start_time
                    # Allow 404 for static files that may not exist yet
                    if "404" not in str(e):
                        self.assertLess(response_time, self.max_response_time,
                                      f"Static file {file_path} response time {response_time*1000:.1f}ms exceeds constitutional requirement: {e}")


if __name__ == "__main__":
    unittest.main()