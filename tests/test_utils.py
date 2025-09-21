#!/usr/bin/env python3
"""
Common test utilities to reduce duplication across test files
"""

import subprocess
import time
import os


class TestServerManager:
    """Manages test server lifecycle to reduce duplication"""

    def __init__(self, port=8000):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.server_process = None

    def start_server(self):
        """Start the backend server for testing"""
        try:
            self.server_process = subprocess.Popen(
                ["python", "backend/src/server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "SERVER_PORT": str(self.port)}
            )
            self.wait_for_server()
        except Exception as e:
            print(f"Failed to start server: {e}")
            raise

    def stop_server(self):
        """Stop the test server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()

    def wait_for_server(self, max_wait=10):
        """Wait for server to be ready"""
        try:
            import requests
            start_time = time.time()

            while time.time() - start_time < max_wait:
                try:
                    response = requests.get(f"{self.base_url}/", timeout=1)
                    if response.status_code in [200, 404]:  # Server is responding
                        return
                except requests.exceptions.RequestException:
                    time.sleep(0.5)

            raise Exception("Server failed to start within timeout")
        except ImportError:
            # If requests not available, just wait a fixed time
            time.sleep(3)


class PlaywrightTestMixin:
    """Common Playwright test functionality to reduce E2E test duplication"""

    @staticmethod
    def get_playwright_imports():
        """Get Playwright MCP imports with fallback handling"""
        try:
            from mcp__playwright__browser_navigate import browser_navigate
            from mcp__playwright__browser_click import browser_click
            from mcp__playwright__browser_type import browser_type
            from mcp__playwright__browser_select_option import browser_select_option
            from mcp__playwright__browser_take_screenshot import browser_take_screenshot
            from mcp__playwright__browser_wait_for import browser_wait_for
            from mcp__playwright__browser_evaluate import browser_evaluate
            from mcp__playwright__browser_install import browser_install
            from mcp__playwright__browser_close import browser_close

            return {
                'browser_navigate': browser_navigate,
                'browser_click': browser_click,
                'browser_type': browser_type,
                'browser_select_option': browser_select_option,
                'browser_take_screenshot': browser_take_screenshot,
                'browser_wait_for': browser_wait_for,
                'browser_evaluate': browser_evaluate,
                'browser_install': browser_install,
                'browser_close': browser_close,
                'available': True
            }
        except ImportError:
            return {'available': False}

    @staticmethod
    async def fill_form_field(field_name, value, possible_selectors):
        """Common form filling logic"""
        from mcp__playwright__browser_type import browser_type
        from mcp__playwright__browser_select_option import browser_select_option

        for selector in possible_selectors:
            try:
                if "select" in selector.lower():
                    await browser_select_option(selector, value)
                else:
                    await browser_type(selector, value)
                print(f"Filled {field_name} with {value} using {selector}")
                return True
            except:
                continue
        return False


class APITestMixin:
    """Common API testing functionality"""

    @staticmethod
    def assert_response_time(response_time, max_time=0.1, endpoint=""):
        """Assert API response time meets constitutional requirements"""
        assert response_time < max_time, \
            f"API {endpoint} response time {response_time*1000:.1f}ms exceeds constitutional requirement of {max_time*1000}ms"

    @staticmethod
    def get_test_data():
        """Get common test data for API tests"""
        return {
            'card': {
                "name": "Test Card",
                "type": "debit",
                "currency": "MXN",
                "balance": 1000.00
            },
            'transaction': {
                "amount": -50.00,
                "description": "Test transaction",
                "transaction_date": "2024-01-01T12:00:00Z",
                "category": "test"
            },
            'position': {
                "asset_type": "stock",
                "symbol": "AAPL"
            },
            'movement': {
                "position_id": 1,
                "movement_type": "buy",
                "quantity": 10.0,
                "price_per_unit": 150.00,
                "movement_datetime": "2024-01-01T12:00:00Z"
            }
        }


def setup_test_environment():
    """Common test environment setup"""
    # Initialize database if needed
    try:
        subprocess.run(["python", "backend/src/database/init_db.py"],
                      capture_output=True, check=False)
    except:
        pass  # Database may already exist

    return TestServerManager()


def cleanup_test_environment(server_manager):
    """Common test environment cleanup"""
    if server_manager:
        server_manager.stop_server()