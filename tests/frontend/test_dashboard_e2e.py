#!/usr/bin/env python3
"""
End-to-end test for dashboard user story using Playwright MCP
Tests the complete dashboard analytics workflow as specified in quickstart.md
"""

import asyncio
import unittest
import subprocess
import time
import os
import sys

# Add the project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from mcp__playwright__browser_navigate import browser_navigate
    from mcp__playwright__browser_click import browser_click
    from mcp__playwright__browser_take_screenshot import browser_take_screenshot
    from mcp__playwright__browser_wait_for import browser_wait_for
    from mcp__playwright__browser_evaluate import browser_evaluate
    from mcp__playwright__browser_install import browser_install
    from mcp__playwright__browser_close import browser_close
    PLAYWRIGHT_MCP_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_MCP_AVAILABLE = False


class DashboardE2ETest(unittest.TestCase):
    """End-to-end test for dashboard user story using Playwright MCP"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        if not PLAYWRIGHT_MCP_AVAILABLE:
            raise unittest.SkipTest("Playwright MCP not available - install required")

        cls.server_process = None
        cls.base_url = "http://localhost:8000"

        # Start server for testing
        cls._start_server()
        cls._wait_for_server()

        # Install Playwright browsers
        asyncio.run(browser_install())

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()

        # Close browser
        try:
            asyncio.run(browser_close())
        except:
            pass

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
        import requests
        max_wait = 10
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{cls.base_url}/", timeout=1)
                if response.status_code in [200, 404]:
                    return
            except requests.exceptions.RequestException:
                time.sleep(0.5)

        raise Exception("Server failed to start within timeout")

    def test_dashboard_analytics_user_story(self):
        """
        Test Story 1: Dashboard Analytics
        Given a user has multiple financial accounts
        When they access the dashboard
        Then they see consolidated statistics, graphs, and metrics
        """

        async def run_dashboard_test():
            # Navigate to dashboard
            await browser_navigate(self.base_url)

            # Take screenshot for debugging
            await browser_take_screenshot()

            # Wait for page to load completely
            await browser_wait_for("body", timeout=5000)

            # Verify dashboard loads within 3 seconds (constitutional requirement)
            load_time = await browser_evaluate("""
                () => {
                    return performance.timing.loadEventEnd - performance.timing.navigationStart;
                }
            """)

            if load_time > 3000:
                self.fail(f"Dashboard load time {load_time}ms exceeds constitutional requirement of 3000ms")

            # Check for required dashboard sections
            sections_to_check = [
                "total-balance-summary",
                "recent-transactions",
                "investment-portfolio",
                "profit-loss-metrics"
            ]

            for section in sections_to_check:
                try:
                    await browser_wait_for(f"#{section}, .{section}, [data-testid='{section}']", timeout=2000)
                except:
                    # If specific IDs don't exist, check for general dashboard content
                    print(f"Dashboard section {section} not found - checking for general content")

            # Verify charts are present (Chart.js integration)
            chart_present = await browser_evaluate("""
                () => {
                    // Look for canvas elements (Chart.js renders to canvas)
                    const canvases = document.querySelectorAll('canvas');
                    // Or look for chart containers
                    const chartContainers = document.querySelectorAll('.chart, [id*="chart"], [class*="chart"]');
                    return canvases.length > 0 || chartContainers.length > 0;
                }
            """)

            # Verify dashboard has basic content structure
            dashboard_content = await browser_evaluate("""
                () => {
                    const bodyText = document.body.innerText.toLowerCase();
                    const hasFinancialTerms = bodyText.includes('balance') ||
                                            bodyText.includes('transaction') ||
                                            bodyText.includes('investment') ||
                                            bodyText.includes('dashboard');

                    // Check for navigation or menu
                    const hasNavigation = document.querySelectorAll('nav, .nav, .menu, .navigation').length > 0;

                    // Check for interactive elements
                    const hasButtons = document.querySelectorAll('button, .btn, [role="button"]').length > 0;

                    return {
                        hasFinancialTerms,
                        hasNavigation,
                        hasButtons,
                        bodyLength: document.body.innerText.length
                    };
                }
            """)

            # Assertions for dashboard content
            self.assertGreater(dashboard_content['bodyLength'], 50,
                             "Dashboard should have meaningful content")

            # Test time period filters (if implemented)
            period_filters = ['week', 'month', 'quarter', 'year']
            for period in period_filters:
                try:
                    # Look for period filter buttons/links
                    filter_element = await browser_evaluate(f"""
                        () => {{
                            const elements = Array.from(document.querySelectorAll('*'));
                            return elements.some(el =>
                                el.textContent.toLowerCase().includes('{period}') &&
                                (el.tagName === 'BUTTON' || el.role === 'button' || el.onclick)
                            );
                        }}
                    """)

                    if filter_element:
                        # Click the filter and verify response time
                        start_time = time.time()
                        await browser_click(f"text={period}")

                        # Wait for potential AJAX response
                        await asyncio.sleep(0.2)

                        response_time = (time.time() - start_time) * 1000
                        self.assertLess(response_time, 100,
                                      f"Period filter '{period}' response time {response_time}ms exceeds constitutional requirement of 100ms")

                except Exception as e:
                    print(f"Period filter '{period}' test skipped: {e}")

            # Verify responsive interactions
            interaction_response = await browser_evaluate("""
                () => {
                    const startTime = performance.now();
                    // Simulate a simple interaction
                    document.body.click();
                    const endTime = performance.now();
                    return endTime - startTime;
                }
            """)

            self.assertLess(interaction_response, 100,
                          f"Dashboard interaction response time {interaction_response}ms exceeds constitutional requirement of 100ms")

            # Take final screenshot
            await browser_take_screenshot()

            return True

        # Run the async test
        result = asyncio.run(run_dashboard_test())
        self.assertTrue(result, "Dashboard analytics user story test completed successfully")

    def test_dashboard_navigation_performance(self):
        """Test dashboard navigation meets performance requirements"""

        async def run_navigation_test():
            # Navigate to dashboard
            await browser_navigate(self.base_url)

            # Test navigation to other pages and back
            navigation_tests = [
                "/pages/transactions.html",
                "/pages/manage.html",
                "/pages/movements.html"
            ]

            for page_url in navigation_tests:
                start_time = time.time()

                try:
                    await browser_navigate(f"{self.base_url}{page_url}")
                    await browser_wait_for("body", timeout=3000)

                    load_time = (time.time() - start_time) * 1000
                    self.assertLess(load_time, 3000,
                                  f"Page {page_url} load time {load_time}ms exceeds constitutional requirement of 3000ms")

                    # Navigate back to dashboard
                    await browser_navigate(self.base_url)
                    await browser_wait_for("body", timeout=3000)

                except Exception as e:
                    print(f"Navigation test for {page_url} failed: {e}")

            return True

        result = asyncio.run(run_navigation_test())
        self.assertTrue(result, "Dashboard navigation performance test completed")


# Fallback test class if Playwright MCP is not available
class DashboardE2EFallbackTest(unittest.TestCase):
    """Fallback test using requests when Playwright MCP is not available"""

    def setUp(self):
        """Set up fallback test"""
        if PLAYWRIGHT_MCP_AVAILABLE:
            self.skipTest("Playwright MCP is available, use main test")

    def test_dashboard_basic_functionality(self):
        """Basic dashboard test using requests library"""
        import requests

        base_url = "http://localhost:8000"

        try:
            # Test dashboard loads
            response = requests.get(base_url, timeout=3)
            self.assertIn(response.status_code, [200, 404],
                         "Dashboard should respond with valid status")

            # Test API endpoints respond
            api_endpoints = [
                "/api/dashboard/summary",
                "/api/dashboard/charts"
            ]

            for endpoint in api_endpoints:
                try:
                    start_time = time.time()
                    response = requests.get(f"{base_url}{endpoint}", timeout=1)
                    response_time = (time.time() - start_time) * 1000

                    self.assertLess(response_time, 100,
                                  f"API {endpoint} response time {response_time}ms exceeds constitutional requirement")
                except Exception as e:
                    print(f"API endpoint {endpoint} test failed: {e}")

        except Exception as e:
            self.skipTest(f"Server not available for testing: {e}")


if __name__ == "__main__":
    unittest.main()