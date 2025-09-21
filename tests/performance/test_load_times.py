#!/usr/bin/env python3
"""
Performance test for page load times - Constitutional requirement: <3s
Tests that all pages load within 3 seconds as per constitutional requirements.
"""

import time
import unittest
import requests
import subprocess
import threading
import os
import signal
from urllib.parse import urljoin


class PageLoadTimeTest(unittest.TestCase):
    """Test page load times meet constitutional requirements (<3s)"""

    @classmethod
    def setUpClass(cls):
        """Start the server for testing"""
        cls.server_process = None
        cls.base_url = "http://localhost:8000"
        cls.max_load_time = 3.0  # Constitutional requirement: <3s

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

    def test_dashboard_load_time(self):
        """Test dashboard page loads within 3 seconds"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/", timeout=self.max_load_time)
            load_time = time.time() - start_time

            self.assertLess(load_time, self.max_load_time,
                          f"Dashboard load time {load_time:.2f}s exceeds constitutional requirement of {self.max_load_time}s")

            # Also check response is successful
            self.assertIn(response.status_code, [200, 404], "Dashboard should respond with valid status")

        except requests.exceptions.Timeout:
            load_time = time.time() - start_time
            self.fail(f"Dashboard timed out after {load_time:.2f}s (constitutional requirement: <{self.max_load_time}s)")

    def test_transactions_page_load_time(self):
        """Test transactions page loads within 3 seconds"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/pages/transactions.html", timeout=self.max_load_time)
            load_time = time.time() - start_time

            self.assertLess(load_time, self.max_load_time,
                          f"Transactions page load time {load_time:.2f}s exceeds constitutional requirement of {self.max_load_time}s")

        except requests.exceptions.Timeout:
            load_time = time.time() - start_time
            self.fail(f"Transactions page timed out after {load_time:.2f}s (constitutional requirement: <{self.max_load_time}s)")

    def test_manage_page_load_time(self):
        """Test manage page loads within 3 seconds"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/pages/manage.html", timeout=self.max_load_time)
            load_time = time.time() - start_time

            self.assertLess(load_time, self.max_load_time,
                          f"Manage page load time {load_time:.2f}s exceeds constitutional requirement of {self.max_load_time}s")

        except requests.exceptions.Timeout:
            load_time = time.time() - start_time
            self.fail(f"Manage page timed out after {load_time:.2f}s (constitutional requirement: <{self.max_load_time}s)")

    def test_movements_page_load_time(self):
        """Test movements page loads within 3 seconds"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/pages/movements.html", timeout=self.max_load_time)
            load_time = time.time() - start_time

            self.assertLess(load_time, self.max_load_time,
                          f"Movements page load time {load_time:.2f}s exceeds constitutional requirement of {self.max_load_time}s")

        except requests.exceptions.Timeout:
            load_time = time.time() - start_time
            self.fail(f"Movements page timed out after {load_time:.2f}s (constitutional requirement: <{self.max_load_time}s)")

    def test_api_endpoints_response_time(self):
        """Test API endpoints respond within constitutional requirements"""
        api_endpoints = [
            "/api/cards",
            "/api/transactions",
            "/api/investments/positions",
            "/api/investments/movements",
            "/api/dashboard/summary",
            "/api/dashboard/charts"
        ]

        for endpoint in api_endpoints:
            with self.subTest(endpoint=endpoint):
                start_time = time.time()

                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=self.max_load_time)
                    load_time = time.time() - start_time

                    self.assertLess(load_time, self.max_load_time,
                                  f"API endpoint {endpoint} response time {load_time:.2f}s exceeds constitutional requirement of {self.max_load_time}s")

                except requests.exceptions.Timeout:
                    load_time = time.time() - start_time
                    self.fail(f"API endpoint {endpoint} timed out after {load_time:.2f}s (constitutional requirement: <{self.max_load_time}s)")

    def test_concurrent_load_performance(self):
        """Test multiple concurrent page loads meet performance requirements"""
        urls = [
            f"{self.base_url}/",
            f"{self.base_url}/pages/transactions.html",
            f"{self.base_url}/pages/manage.html",
            f"{self.base_url}/pages/movements.html"
        ]

        results = []

        def load_page(url):
            start_time = time.time()
            try:
                response = requests.get(url, timeout=self.max_load_time)
                load_time = time.time() - start_time
                results.append((url, load_time, response.status_code))
            except Exception as e:
                load_time = time.time() - start_time
                results.append((url, load_time, f"Error: {e}"))

        # Start concurrent requests
        threads = []
        for url in urls:
            thread = threading.Thread(target=load_page, args=(url,))
            thread.start()
            threads.append(thread)

        # Wait for all to complete
        for thread in threads:
            thread.join()

        # Verify all met requirements
        for url, load_time, status in results:
            with self.subTest(url=url):
                self.assertLess(load_time, self.max_load_time,
                              f"Concurrent load of {url} took {load_time:.2f}s (constitutional requirement: <{self.max_load_time}s)")


if __name__ == "__main__":
    unittest.main()