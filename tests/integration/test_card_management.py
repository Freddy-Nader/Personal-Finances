#!/usr/bin/env python3
"""
Integration Test: Card Management Workflow
Tests the complete card management user story including creation, modification, sections, and interests/fees.
"""

import unittest
import json
import sqlite3
import os
import sys
from datetime import datetime
import http.client

# Add backend src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend/src'))

from database.init_db import initialize_database
from models.card import Card
from models.section import Section
from services.card_service import CardService
from services.section_service import SectionService


class TestCardManagementWorkflow(unittest.TestCase):
    """Integration tests for card management workflow from quickstart.md"""

    def setUp(self):
        """Set up test database and server connection"""
        self.test_db_path = "./test_data/test_card_management.db"
        os.makedirs("./test_data", exist_ok=True)

        # Remove existing test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        # Initialize fresh test database
        initialize_database(self.test_db_path)

        # Set up services with test database
        self.card_service = CardService(self.test_db_path)
        self.section_service = SectionService(self.test_db_path)

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

    def test_card_creation_workflow(self):
        """Test creating a new card through API - matching quickstart example"""
        # Card data matching quickstart example
        card_data = {
            "name": "Main Checking",
            "type": "debit",
            "currency": "MXN",  # Default currency
            "balance": 1000.00
        }

        # Create card via API
        status, response = self._make_api_request("POST", "/cards", card_data)

        # Verify card creation
        self.assertEqual(status, 201, f"Expected 201, got {status}: {response}")
        self.assertIsInstance(response, dict)
        self.assertEqual(response["name"], "Main Checking")
        self.assertEqual(response["type"], "debit")
        self.assertEqual(response["currency"], "MXN")  # Should default to MXN
        self.assertEqual(response["balance"], 1000.00)
        self.assertIsNone(response["credit_limit"])  # Debit card should not have credit limit

        # Store card ID for further tests
        self.card_id = response["id"]

        # Verify card appears in cards list
        status, response = self._make_api_request("GET", "/cards")
        self.assertEqual(status, 200)
        self.assertIsInstance(response, list)

        # Find our created card
        created_card = None
        for card in response:
            if card["id"] == self.card_id:
                created_card = card
                break

        self.assertIsNotNone(created_card)
        self.assertEqual(created_card["name"], "Main Checking")

    def test_credit_card_creation_workflow(self):
        """Test creating a credit card with credit limit"""
        # Credit card data
        card_data = {
            "name": "Main Credit Card",
            "type": "credit",
            "currency": "MXN",
            "credit_limit": 5000.00
        }

        # Create credit card via API
        status, response = self._make_api_request("POST", "/cards", card_data)

        # Verify credit card creation
        self.assertEqual(status, 201)
        self.assertEqual(response["name"], "Main Credit Card")
        self.assertEqual(response["type"], "credit")
        self.assertEqual(response["credit_limit"], 5000.00)
        self.assertEqual(response["balance"], 0.00)  # Credit cards start with 0 balance

    def test_default_currency_workflow(self):
        """Test that cards default to MXN currency as specified"""
        # Card without explicit currency
        card_data = {
            "name": "Test Card",
            "type": "debit",
            "balance": 500.00
        }

        # Create card via API
        status, response = self._make_api_request("POST", "/cards", card_data)

        # Verify default currency is MXN
        self.assertEqual(status, 201)
        self.assertEqual(response["currency"], "MXN")

    def test_section_creation_workflow(self):
        """Test creating sections for a card - matching quickstart example"""
        # First create a card
        card_data = {
            "name": "Test Card with Sections",
            "type": "debit",
            "balance": 1000.00
        }

        status, response = self._make_api_request("POST", "/cards", card_data)
        self.assertEqual(status, 201)
        card_id = response["id"]

        # Create section matching quickstart example
        section_data = {
            "name": "Emergency Fund",
            "initial_balance": 500.00
        }

        # Create section via API
        status, response = self._make_api_request("POST", f"/cards/{card_id}/sections", section_data)

        # Verify section creation
        self.assertEqual(status, 201, f"Expected 201, got {status}: {response}")
        self.assertEqual(response["name"], "Emergency Fund")
        self.assertEqual(response["initial_balance"], 500.00)
        self.assertEqual(response["card_id"], card_id)

        # Verify section appears in card's sections list
        status, response = self._make_api_request("GET", f"/cards/{card_id}/sections")
        self.assertEqual(status, 200)
        self.assertIsInstance(response, list)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["name"], "Emergency Fund")

    def test_multiple_sections_workflow(self):
        """Test creating multiple sections for a card"""
        # Create a card
        card_data = {
            "name": "Multi-Section Card",
            "type": "credit",
            "credit_limit": 3000.00
        }

        status, response = self._make_api_request("POST", "/cards", card_data)
        self.assertEqual(status, 201)
        card_id = response["id"]

        # Create multiple sections
        sections = [
            {"name": "Groceries", "initial_balance": 800.00},
            {"name": "Entertainment", "initial_balance": 400.00},
            {"name": "Emergency", "initial_balance": 1000.00}
        ]

        created_sections = []
        for section_data in sections:
            status, response = self._make_api_request("POST", f"/cards/{card_id}/sections", section_data)
            self.assertEqual(status, 201)
            created_sections.append(response)

        # Verify all sections were created
        status, response = self._make_api_request("GET", f"/cards/{card_id}/sections")
        self.assertEqual(status, 200)
        self.assertEqual(len(response), 3)

        # Verify section names
        section_names = [section["name"] for section in response]
        self.assertIn("Groceries", section_names)
        self.assertIn("Entertainment", section_names)
        self.assertIn("Emergency", section_names)

    def test_card_update_workflow(self):
        """Test updating card details"""
        # Create initial card
        card_data = {
            "name": "Initial Name",
            "type": "debit",
            "balance": 100.00
        }

        status, response = self._make_api_request("POST", "/cards", card_data)
        self.assertEqual(status, 201)
        card_id = response["id"]

        # Update card
        update_data = {
            "name": "Updated Name",
            "balance": 200.00
        }

        status, response = self._make_api_request("PUT", f"/cards/{card_id}", update_data)
        self.assertEqual(status, 200)

        # Verify updates
        self.assertEqual(response["name"], "Updated Name")
        self.assertEqual(response["balance"], 200.00)

        # Verify card is updated in list
        status, response = self._make_api_request("GET", f"/cards/{card_id}")
        self.assertEqual(status, 200)
        self.assertEqual(response["name"], "Updated Name")
        self.assertEqual(response["balance"], 200.00)

    def test_card_validation_workflow(self):
        """Test card form validation"""
        # Test missing required fields
        invalid_cards = [
            {"type": "debit", "balance": 100.00},  # Missing name
            {"name": "Test Card", "balance": 100.00},  # Missing type
            {"name": "Test Card", "type": "invalid", "balance": 100.00},  # Invalid type
        ]

        for invalid_data in invalid_cards:
            status, response = self._make_api_request("POST", "/cards", invalid_data)
            self.assertIn(status, [400, 422], f"Should reject invalid card: {invalid_data}")

    def test_section_validation_workflow(self):
        """Test section form validation"""
        # Create a card first
        card_data = {"name": "Test Card", "type": "debit", "balance": 1000.00}
        status, response = self._make_api_request("POST", "/cards", card_data)
        self.assertEqual(status, 201)
        card_id = response["id"]

        # Test missing required fields
        invalid_sections = [
            {},  # Missing name
            {"initial_balance": 100.00},  # Missing name
        ]

        for invalid_data in invalid_sections:
            status, response = self._make_api_request("POST", f"/cards/{card_id}/sections", invalid_data)
            self.assertIn(status, [400, 422], f"Should reject invalid section: {invalid_data}")

    def test_card_deletion_workflow(self):
        """Test deleting a card"""
        # Create card
        card_data = {
            "name": "Card to Delete",
            "type": "debit",
            "balance": 100.00
        }

        status, response = self._make_api_request("POST", "/cards", card_data)
        self.assertEqual(status, 201)
        card_id = response["id"]

        # Delete card
        status, response = self._make_api_request("DELETE", f"/cards/{card_id}")
        self.assertEqual(status, 204)

        # Verify card is deleted
        status, response = self._make_api_request("GET", f"/cards/{card_id}")
        self.assertEqual(status, 404)

    def test_section_inheritance_workflow(self):
        """Test that sections properly inherit from card's properties"""
        # Create a credit card with credit limit
        card_data = {
            "name": "Credit Card with Sections",
            "type": "credit",
            "credit_limit": 2000.00
        }

        status, response = self._make_api_request("POST", "/cards", card_data)
        self.assertEqual(status, 201)
        card_id = response["id"]

        # Create section that should inherit proportionally from credit limit
        section_data = {
            "name": "Shopping",
            "initial_balance": 1000.00  # 50% of credit limit
        }

        status, response = self._make_api_request("POST", f"/cards/{card_id}/sections", section_data)
        self.assertEqual(status, 201)

        # Verify section has proper relationship to card
        self.assertEqual(response["card_id"], card_id)
        self.assertEqual(response["initial_balance"], 1000.00)

        # Verify section appears when getting card sections
        status, response = self._make_api_request("GET", f"/cards/{card_id}/sections")
        self.assertEqual(status, 200)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["name"], "Shopping")

    def test_comprehensive_card_management_workflow(self):
        """Test complete card management workflow as described in quickstart"""
        # Step 1: Create main checking account (debit)
        checking_data = {
            "name": "Main Checking",
            "type": "debit",
            "currency": "MXN",
            "balance": 1000.00
        }

        status, response = self._make_api_request("POST", "/cards", checking_data)
        self.assertEqual(status, 201)
        checking_id = response["id"]

        # Step 2: Create emergency fund section
        emergency_data = {
            "name": "Emergency Fund",
            "initial_balance": 500.00
        }

        status, response = self._make_api_request("POST", f"/cards/{checking_id}/sections", emergency_data)
        self.assertEqual(status, 201)

        # Step 3: Create credit card
        credit_data = {
            "name": "Main Credit Card",
            "type": "credit",
            "currency": "MXN",
            "credit_limit": 5000.00
        }

        status, response = self._make_api_request("POST", "/cards", credit_data)
        self.assertEqual(status, 201)
        credit_id = response["id"]

        # Step 4: Verify complete setup
        # Get all cards
        status, response = self._make_api_request("GET", "/cards")
        self.assertEqual(status, 200)
        self.assertEqual(len(response), 2)

        # Verify debit card
        checking_card = next((card for card in response if card["id"] == checking_id), None)
        self.assertIsNotNone(checking_card)
        self.assertEqual(checking_card["type"], "debit")
        self.assertEqual(checking_card["currency"], "MXN")

        # Verify credit card
        credit_card = next((card for card in response if card["id"] == credit_id), None)
        self.assertIsNotNone(credit_card)
        self.assertEqual(credit_card["type"], "credit")
        self.assertEqual(credit_card["credit_limit"], 5000.00)

        # Verify sections
        status, response = self._make_api_request("GET", f"/cards/{checking_id}/sections")
        self.assertEqual(status, 200)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["name"], "Emergency Fund")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)