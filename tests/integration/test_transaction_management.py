#!/usr/bin/env python3
"""
Integration Test: Transaction Management Workflow
Tests the complete transaction management user story including creation, editing, and internal transfers.
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
from models.card import Card
from models.section import Section
from services.card_service import CardService
from services.section_service import SectionService


class TestTransactionManagementWorkflow(unittest.TestCase):
    """Integration tests for transaction management workflow from quickstart.md"""

    def setUp(self):
        """Set up test database and server connection"""
        self.test_db_path = "./test_data/test_transaction_workflow.db"
        os.makedirs("./test_data", exist_ok=True)

        # Remove existing test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        # Initialize fresh test database
        initialize_database(self.test_db_path)

        # Set up services with test database
        self.card_service = CardService(self.test_db_path)
        self.section_service = SectionService(self.test_db_path)

        # Create test cards for transaction testing
        self.card_a = self.card_service.create_card("Test Card A", "debit", "MXN", 1000.00)
        self.card_b = self.card_service.create_card("Test Card B", "credit", "MXN", credit_limit=2000.00)

        # Create test sections
        self.section_a = self.section_service.create_section(self.card_a.id, "Groceries", 500.00)

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

    def test_transaction_creation_workflow(self):
        """Test creating a basic transaction through API"""
        # Transaction data matching quickstart example
        transaction_data = {
            "amount": -50.00,  # expense
            "description": "Grocery shopping",
            "transaction_date": datetime.now().isoformat(),
            "card_id": self.card_a.id,
            "section_id": self.section_a.id,
            "category": "Food"
        }

        # Create transaction via API
        status, response = self._make_api_request("POST", "/transactions", transaction_data)

        # Verify transaction creation
        self.assertEqual(status, 201, f"Expected 201, got {status}: {response}")
        self.assertIsInstance(response, dict)
        self.assertEqual(response["amount"], -50.00)
        self.assertEqual(response["description"], "Grocery shopping")
        self.assertEqual(response["card_id"], self.card_a.id)
        self.assertEqual(response["section_id"], self.section_a.id)
        self.assertEqual(response["category"], "Food")

        transaction_id = response["id"]

        # Verify transaction appears in transaction list
        status, response = self._make_api_request("GET", "/transactions")
        self.assertEqual(status, 200)
        self.assertIsInstance(response, dict)
        self.assertIn("transactions", response)

        # Find our created transaction
        created_transaction = None
        for transaction in response["transactions"]:
            if transaction["id"] == transaction_id:
                created_transaction = transaction
                break

        self.assertIsNotNone(created_transaction)
        self.assertEqual(created_transaction["amount"], -50.00)
        self.assertEqual(created_transaction["description"], "Grocery shopping")

    def test_internal_transfer_workflow(self):
        """Test internal transfer creating paired transactions"""
        # Internal transfer from Card A to Card B
        transfer_data = {
            "amount": 200.00,
            "description": "Transfer from debit to credit card",
            "transaction_date": datetime.now().isoformat(),
            "is_internal_transfer": True,
            "transfer_from_type": "card",
            "transfer_from_id": self.card_a.id,
            "transfer_to_type": "card",
            "transfer_to_id": self.card_b.id
        }

        # Create internal transfer via API
        status, response = self._make_api_request("POST", "/transactions", transfer_data)

        # Verify transfer creation
        self.assertEqual(status, 201, f"Expected 201, got {status}: {response}")
        self.assertTrue(response["is_internal_transfer"])

        # Get all transactions to verify paired transactions were created
        status, response = self._make_api_request("GET", "/transactions")
        self.assertEqual(status, 200)

        # Should have created 2 transactions (debit + credit)
        transfer_transactions = [
            t for t in response["transactions"]
            if t["is_internal_transfer"] and "Transfer from debit to credit card" in t["description"]
        ]

        self.assertEqual(len(transfer_transactions), 2, "Internal transfer should create paired transactions")

        # Verify one debit and one credit transaction
        amounts = [t["amount"] for t in transfer_transactions]
        self.assertIn(-200.00, amounts, "Should have debit transaction")
        self.assertIn(200.00, amounts, "Should have credit transaction")

    def test_transaction_filtering_workflow(self):
        """Test transaction filtering by card and date range"""
        # Create multiple transactions with different dates and cards
        base_date = datetime.now()

        transactions = [
            {
                "amount": -30.00,
                "description": "Transaction 1",
                "transaction_date": (base_date - timedelta(days=10)).isoformat(),
                "card_id": self.card_a.id
            },
            {
                "amount": -40.00,
                "description": "Transaction 2",
                "transaction_date": (base_date - timedelta(days=5)).isoformat(),
                "card_id": self.card_a.id
            },
            {
                "amount": -50.00,
                "description": "Transaction 3",
                "transaction_date": base_date.isoformat(),
                "card_id": self.card_b.id
            }
        ]

        # Create all transactions
        for transaction_data in transactions:
            status, response = self._make_api_request("POST", "/transactions", transaction_data)
            self.assertEqual(status, 201)

        # Test filtering by card
        status, response = self._make_api_request("GET", f"/transactions?cardId={self.card_a.id}")
        self.assertEqual(status, 200)

        card_a_transactions = [
            t for t in response["transactions"]
            if t["card_id"] == self.card_a.id and not t["is_internal_transfer"]
        ]
        self.assertEqual(len(card_a_transactions), 2, "Should find 2 transactions for Card A")

        # Test filtering by date range
        start_date = (base_date - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = base_date.strftime("%Y-%m-%d")

        status, response = self._make_api_request("GET", f"/transactions?startDate={start_date}&endDate={end_date}")
        self.assertEqual(status, 200)

        recent_transactions = [
            t for t in response["transactions"]
            if not t["is_internal_transfer"]  # Exclude internal transfers for clean count
        ]
        self.assertGreaterEqual(len(recent_transactions), 2, "Should find recent transactions")

    def test_transaction_pagination_workflow(self):
        """Test transaction list pagination"""
        # Create multiple transactions to test pagination
        for i in range(15):
            transaction_data = {
                "amount": -(10 + i),
                "description": f"Test transaction {i}",
                "transaction_date": datetime.now().isoformat(),
                "card_id": self.card_a.id
            }
            status, response = self._make_api_request("POST", "/transactions", transaction_data)
            self.assertEqual(status, 201)

        # Test first page with limit
        status, response = self._make_api_request("GET", "/transactions?page=1&limit=10")
        self.assertEqual(status, 200)
        self.assertLessEqual(len(response["transactions"]), 10)
        self.assertEqual(response["page"], 1)
        self.assertEqual(response["limit"], 10)
        self.assertTrue(response["has_next"])

        # Test second page
        status, response = self._make_api_request("GET", "/transactions?page=2&limit=10")
        self.assertEqual(status, 200)
        self.assertGreater(len(response["transactions"]), 0)
        self.assertEqual(response["page"], 2)

    def test_transaction_validation_workflow(self):
        """Test transaction form validation"""
        # Test missing required fields
        invalid_transactions = [
            {"description": "Missing amount", "transaction_date": datetime.now().isoformat()},
            {"amount": -50.00, "transaction_date": datetime.now().isoformat()},  # Missing description
            {"amount": -50.00, "description": "Missing date"}  # Missing transaction_date
        ]

        for invalid_data in invalid_transactions:
            status, response = self._make_api_request("POST", "/transactions", invalid_data)
            self.assertIn(status, [400, 422], f"Should reject invalid transaction: {invalid_data}")

    def test_transaction_update_workflow(self):
        """Test updating transaction details"""
        # Create initial transaction
        transaction_data = {
            "amount": -75.00,
            "description": "Initial description",
            "transaction_date": datetime.now().isoformat(),
            "card_id": self.card_a.id,
            "category": "Initial category"
        }

        status, response = self._make_api_request("POST", "/transactions", transaction_data)
        self.assertEqual(status, 201)
        transaction_id = response["id"]

        # Update transaction
        update_data = {
            "amount": -85.00,
            "description": "Updated description",
            "category": "Updated category"
        }

        status, response = self._make_api_request("PUT", f"/transactions/{transaction_id}", update_data)
        self.assertEqual(status, 200)

        # Verify updates
        self.assertEqual(response["amount"], -85.00)
        self.assertEqual(response["description"], "Updated description")
        self.assertEqual(response["category"], "Updated category")

        # Verify transaction is updated in list
        status, response = self._make_api_request("GET", f"/transactions/{transaction_id}")
        self.assertEqual(status, 200)
        self.assertEqual(response["amount"], -85.00)
        self.assertEqual(response["description"], "Updated description")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)