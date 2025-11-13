#!/usr/bin/env python3
"""
Integration Test: Investment Tracking Workflow
Tests the complete investment tracking user story including positions, movements, and portfolio calculations.
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


class TestInvestmentTrackingWorkflow(unittest.TestCase):
    """Integration tests for investment tracking workflow from quickstart.md"""

    def setUp(self):
        """Set up test database and server connection"""
        self.test_db_path = "./test_data/test_investment_tracking.db"
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

    def test_investment_position_creation_workflow(self):
        """Test creating investment positions - matching quickstart example"""
        # Position data matching quickstart example
        position_data = {
            "asset_type": "stock",
            "symbol": "AAPL"
        }

        # Create position via API
        status, response = self._make_api_request("POST", "/investments/positions", position_data)

        # Verify position creation
        self.assertEqual(status, 201, f"Expected 201, got {status}: {response}")
        self.assertIsInstance(response, dict)
        self.assertEqual(response["asset_type"], "stock")
        self.assertEqual(response["symbol"], "AAPL")

        # Store position ID for further tests
        self.position_id = response["id"]

        # Verify position appears in positions list
        status, response = self._make_api_request("GET", "/investments/positions")
        self.assertEqual(status, 200)
        self.assertIsInstance(response, list)

        # Find our created position
        created_position = None
        for position in response:
            if position["id"] == self.position_id:
                created_position = position
                break

        self.assertIsNotNone(created_position)
        self.assertEqual(created_position["symbol"], "AAPL")

    def test_crypto_position_creation_workflow(self):
        """Test creating cryptocurrency position"""
        # Crypto position data
        position_data = {
            "asset_type": "crypto",
            "symbol": "BTC"
        }

        # Create crypto position via API
        status, response = self._make_api_request("POST", "/investments/positions", position_data)

        # Verify crypto position creation
        self.assertEqual(status, 201)
        self.assertEqual(response["asset_type"], "crypto")
        self.assertEqual(response["symbol"], "BTC")

    def test_buy_movement_workflow(self):
        """Test adding buy movements - matching quickstart example"""
        # First create a position
        position_data = {
            "asset_type": "stock",
            "symbol": "AAPL"
        }

        status, response = self._make_api_request("POST", "/investments/positions", position_data)
        self.assertEqual(status, 201)
        position_id = response["id"]

        # Buy movement data matching quickstart example
        movement_data = {
            "position_id": position_id,
            "movement_type": "buy",
            "quantity": 10.0,
            "price_per_unit": 150.00,
            "movement_datetime": datetime.now().isoformat(),
            "description": "Initial investment"
        }

        # Create buy movement via API
        status, response = self._make_api_request("POST", "/investments/movements", movement_data)

        # Verify movement creation
        self.assertEqual(status, 201, f"Expected 201, got {status}: {response}")
        self.assertEqual(response["position_id"], position_id)
        self.assertEqual(response["movement_type"], "buy")
        self.assertEqual(response["quantity"], 10.0)
        self.assertEqual(response["price_per_unit"], 150.00)
        self.assertEqual(response["total_amount"], 1500.00)  # 10 * 150
        self.assertEqual(response["description"], "Initial investment")

    def test_sell_movement_workflow(self):
        """Test selling shares/crypto"""
        # Create position and initial buy movement
        position_data = {"asset_type": "stock", "symbol": "MSFT"}
        status, response = self._make_api_request("POST", "/investments/positions", position_data)
        self.assertEqual(status, 201)
        position_id = response["id"]

        # Buy movement first
        buy_data = {
            "position_id": position_id,
            "movement_type": "buy",
            "quantity": 20.0,
            "price_per_unit": 100.00,
            "movement_datetime": (datetime.now() - timedelta(days=30)).isoformat(),
            "description": "Initial purchase"
        }

        status, response = self._make_api_request("POST", "/investments/movements", buy_data)
        self.assertEqual(status, 201)

        # Sell movement
        sell_data = {
            "position_id": position_id,
            "movement_type": "sell",
            "quantity": 5.0,
            "price_per_unit": 110.00,
            "movement_datetime": datetime.now().isoformat(),
            "description": "Partial sale for profit"
        }

        status, response = self._make_api_request("POST", "/investments/movements", sell_data)
        self.assertEqual(status, 201)
        self.assertEqual(response["movement_type"], "sell")
        self.assertEqual(response["quantity"], 5.0)
        self.assertEqual(response["total_amount"], 550.00)  # 5 * 110

    def test_portfolio_calculations_workflow(self):
        """Test portfolio calculations and holdings"""
        # Create multiple positions with movements
        positions_data = [
            {"asset_type": "stock", "symbol": "GOOGL"},
            {"asset_type": "crypto", "symbol": "ETH"}
        ]

        position_ids = []
        for pos_data in positions_data:
            status, response = self._make_api_request("POST", "/investments/positions", pos_data)
            self.assertEqual(status, 201)
            position_ids.append(response["id"])

        # Add movements for each position
        movements_data = [
            {
                "position_id": position_ids[0],
                "movement_type": "buy",
                "quantity": 5.0,
                "price_per_unit": 2500.00,
                "movement_datetime": (datetime.now() - timedelta(days=60)).isoformat(),
                "description": "GOOGL initial buy"
            },
            {
                "position_id": position_ids[1],
                "movement_type": "buy",
                "quantity": 2.0,
                "price_per_unit": 3000.00,
                "movement_datetime": (datetime.now() - timedelta(days=45)).isoformat(),
                "description": "ETH initial buy"
            },
            {
                "position_id": position_ids[0],
                "movement_type": "sell",
                "quantity": 1.0,
                "price_per_unit": 2600.00,
                "movement_datetime": (datetime.now() - timedelta(days=10)).isoformat(),
                "description": "GOOGL partial sale"
            }
        ]

        for movement_data in movements_data:
            status, response = self._make_api_request("POST", "/investments/movements", movement_data)
            self.assertEqual(status, 201)

        # Test getting all movements
        status, response = self._make_api_request("GET", "/investments/movements")
        self.assertEqual(status, 200)
        self.assertIsInstance(response, list)
        self.assertEqual(len(response), 3)

        # Test filtering movements by position
        status, response = self._make_api_request("GET", f"/investments/movements?positionId={position_ids[0]}")
        self.assertEqual(status, 200)

        googl_movements = response
        self.assertEqual(len(googl_movements), 2)  # 1 buy + 1 sell for GOOGL

        # Verify movement types
        movement_types = [m["movement_type"] for m in googl_movements]
        self.assertIn("buy", movement_types)
        self.assertIn("sell", movement_types)

    def test_movement_validation_workflow(self):
        """Test movement form validation"""
        # Create position first
        position_data = {"asset_type": "stock", "symbol": "TEST"}
        status, response = self._make_api_request("POST", "/investments/positions", position_data)
        self.assertEqual(status, 201)
        position_id = response["id"]

        # Test missing required fields
        invalid_movements = [
            {
                "movement_type": "buy",
                "quantity": 10.0,
                "price_per_unit": 150.00,
                "movement_datetime": datetime.now().isoformat()
                # Missing position_id
            },
            {
                "position_id": position_id,
                "quantity": 10.0,
                "price_per_unit": 150.00,
                "movement_datetime": datetime.now().isoformat()
                # Missing movement_type
            },
            {
                "position_id": position_id,
                "movement_type": "buy",
                "price_per_unit": 150.00,
                "movement_datetime": datetime.now().isoformat()
                # Missing quantity
            },
            {
                "position_id": position_id,
                "movement_type": "invalid",
                "quantity": 10.0,
                "price_per_unit": 150.00,
                "movement_datetime": datetime.now().isoformat()
                # Invalid movement_type
            }
        ]

        for invalid_data in invalid_movements:
            status, response = self._make_api_request("POST", "/investments/movements", invalid_data)
            self.assertIn(status, [400, 422], f"Should reject invalid movement: {invalid_data}")

    def test_position_validation_workflow(self):
        """Test position form validation"""
        # Test missing required fields
        invalid_positions = [
            {"symbol": "AAPL"},  # Missing asset_type
            {"asset_type": "stock"},  # Missing symbol
            {"asset_type": "invalid", "symbol": "AAPL"},  # Invalid asset_type
        ]

        for invalid_data in invalid_positions:
            status, response = self._make_api_request("POST", "/investments/positions", invalid_data)
            self.assertIn(status, [400, 422], f"Should reject invalid position: {invalid_data}")

    def test_time_based_movement_filtering(self):
        """Test filtering movements by date range"""
        # Create position
        position_data = {"asset_type": "stock", "symbol": "TSLA"}
        status, response = self._make_api_request("POST", "/investments/positions", position_data)
        self.assertEqual(status, 201)
        position_id = response["id"]

        # Create movements with different dates
        base_date = datetime.now()
        movements_data = [
            {
                "position_id": position_id,
                "movement_type": "buy",
                "quantity": 10.0,
                "price_per_unit": 800.00,
                "movement_datetime": (base_date - timedelta(days=60)).isoformat(),
                "description": "Old buy"
            },
            {
                "position_id": position_id,
                "movement_type": "buy",
                "quantity": 5.0,
                "price_per_unit": 850.00,
                "movement_datetime": (base_date - timedelta(days=30)).isoformat(),
                "description": "Recent buy"
            },
            {
                "position_id": position_id,
                "movement_type": "sell",
                "quantity": 3.0,
                "price_per_unit": 900.00,
                "movement_datetime": (base_date - timedelta(days=5)).isoformat(),
                "description": "Very recent sell"
            }
        ]

        for movement_data in movements_data:
            status, response = self._make_api_request("POST", "/investments/movements", movement_data)
            self.assertEqual(status, 201)

        # Test date range filtering
        start_date = (base_date - timedelta(days=40)).strftime("%Y-%m-%d")
        end_date = base_date.strftime("%Y-%m-%d")

        status, response = self._make_api_request("GET", f"/investments/movements?startDate={start_date}&endDate={end_date}")
        self.assertEqual(status, 200)

        # Should find the recent movements (last 40 days)
        recent_movements = response
        self.assertGreaterEqual(len(recent_movements), 2)

        # Verify movements are within date range
        for movement in recent_movements:
            movement_date = datetime.fromisoformat(movement["movement_datetime"].replace('Z', '+00:00'))
            self.assertGreaterEqual(movement_date.date(), (base_date - timedelta(days=40)).date())

    def test_comprehensive_investment_workflow(self):
        """Test complete investment workflow as described in quickstart"""
        # Step 1: Create new investment position (AAPL stock)
        position_data = {
            "asset_type": "stock",
            "symbol": "AAPL"
        }

        status, response = self._make_api_request("POST", "/investments/positions", position_data)
        self.assertEqual(status, 201)
        position_id = response["id"]

        # Step 2: Add buy movement (10 shares at $150 each)
        buy_data = {
            "position_id": position_id,
            "movement_type": "buy",
            "quantity": 10.0,
            "price_per_unit": 150.00,
            "movement_datetime": datetime.now().isoformat(),
            "description": "Initial investment"
        }

        status, response = self._make_api_request("POST", "/investments/movements", buy_data)
        self.assertEqual(status, 201)
        self.assertEqual(response["total_amount"], 1500.00)

        # Step 3: Verify portfolio calculations
        # Get all positions
        status, response = self._make_api_request("GET", "/investments/positions")
        self.assertEqual(status, 200)

        aapl_position = next((pos for pos in response if pos["symbol"] == "AAPL"), None)
        self.assertIsNotNone(aapl_position)

        # Step 4: Get movement history
        status, response = self._make_api_request("GET", f"/investments/movements?positionId={position_id}")
        self.assertEqual(status, 200)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["description"], "Initial investment")

        # Step 5: Add another buy to test cost basis calculation
        buy_data_2 = {
            "position_id": position_id,
            "movement_type": "buy",
            "quantity": 5.0,
            "price_per_unit": 160.00,
            "movement_datetime": (datetime.now() + timedelta(hours=1)).isoformat(),
            "description": "Additional investment"
        }

        status, response = self._make_api_request("POST", "/investments/movements", buy_data_2)
        self.assertEqual(status, 201)

        # Step 6: Verify total movements
        status, response = self._make_api_request("GET", f"/investments/movements?positionId={position_id}")
        self.assertEqual(status, 200)
        self.assertEqual(len(response), 2)

        # Calculate expected totals: 10*150 + 5*160 = 1500 + 800 = 2300
        total_cost = sum(m["total_amount"] for m in response if m["movement_type"] == "buy")
        self.assertEqual(total_cost, 2300.00)

        total_quantity = sum(m["quantity"] for m in response if m["movement_type"] == "buy")
        self.assertEqual(total_quantity, 15.0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)