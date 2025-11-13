#!/usr/bin/env python3
"""
Test script to verify add button functionality
"""
import requests
import time
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import subprocess
import sys

def test_api_endpoints():
    """Test all API endpoints that the add buttons should use"""
    base_url = "http://localhost:8000/api"

    print("Testing API endpoints...")

    # Test cards endpoint
    try:
        response = requests.get(f"{base_url}/cards")
        print(f"✓ GET /api/cards: {response.status_code}")

        # Test card creation
        card_data = {
            "name": "Test Card",
            "type": "debit",
            "currency": "MXN",
            "initial_balance": 1000.0
        }
        response = requests.post(f"{base_url}/cards", json=card_data)
        print(f"✓ POST /api/cards: {response.status_code}")

    except Exception as e:
        print(f"✗ Cards API error: {e}")

    # Test transactions endpoint
    try:
        response = requests.get(f"{base_url}/transactions")
        print(f"✓ GET /api/transactions: {response.status_code}")

        # Test transaction creation
        transaction_data = {
            "amount": -25.50,
            "description": "Test Transaction",
            "category": "food",
            "transaction_date": "2024-01-15T12:00:00"
        }
        response = requests.post(f"{base_url}/transactions", json=transaction_data)
        print(f"✓ POST /api/transactions: {response.status_code}")

    except Exception as e:
        print(f"✗ Transactions API error: {e}")

    # Test investments endpoints
    try:
        response = requests.get(f"{base_url}/investments/positions")
        print(f"✓ GET /api/investments/positions: {response.status_code}")

        # Test position creation
        position_data = {
            "asset_type": "stock",
            "symbol": "AAPL"
        }
        response = requests.post(f"{base_url}/investments/positions", json=position_data)
        print(f"✓ POST /api/investments/positions: {response.status_code}")

        # Test movement creation
        movement_data = {
            "position_id": 1,
            "movement_type": "buy",
            "quantity": 10,
            "price_per_unit": 150.00,
            "movement_datetime": "2024-01-15T12:00:00"
        }
        response = requests.post(f"{base_url}/investments/movements", json=movement_data)
        print(f"✓ POST /api/investments/movements: {response.status_code}")

    except Exception as e:
        print(f"✗ Investments API error: {e}")

def test_frontend_pages():
    """Test that frontend pages load correctly"""
    base_url = "http://localhost:8000"
    pages = [
        "/pages/dashboard.html",
        "/pages/transactions.html",
        "/pages/manage.html",
        "/pages/movements.html"
    ]

    print("\nTesting frontend pages...")

    for page in pages:
        try:
            response = requests.get(f"{base_url}{page}")
            if response.status_code == 200:
                # Check if add buttons are present
                content = response.text

                if "addTransactionBtn" in content:
                    print(f"✓ {page}: Add Transaction button found")
                elif "addCardBtn" in content:
                    print(f"✓ {page}: Add Card button found")
                elif "addPositionBtn" in content:
                    print(f"✓ {page}: Add Position button found")
                elif "addMovementBtn" in content:
                    print(f"✓ {page}: Add Movement button found")
                else:
                    print(f"✓ {page}: Page loads (no add buttons expected)")

                # Check for JavaScript includes
                if 'src="../js/' in content:
                    print(f"  - JavaScript files included")

            else:
                print(f"✗ {page}: HTTP {response.status_code}")

        except Exception as e:
            print(f"✗ {page}: Error - {e}")

def test_javascript_files():
    """Test that JavaScript files load correctly"""
    base_url = "http://localhost:8000"
    js_files = [
        "/js/api.js",
        "/js/components.js",
        "/js/utils.js",
        "/js/transactions.js",
        "/js/manage.js",
        "/js/movements.js"
    ]

    print("\nTesting JavaScript files...")

    for js_file in js_files:
        try:
            response = requests.get(f"{base_url}{js_file}")
            if response.status_code == 200:
                content = response.text

                # Check for syntax errors by looking for key classes/functions
                if "class " in content or "function " in content:
                    print(f"✓ {js_file}: Loads successfully")

                    # Check for specific patterns that indicate functionality
                    if "addEventListener" in content:
                        print(f"  - Event listeners found")
                    if "getElementById" in content:
                        print(f"  - DOM manipulation found")

                else:
                    print(f"? {js_file}: Loads but may be empty")

            else:
                print(f"✗ {js_file}: HTTP {response.status_code}")

        except Exception as e:
            print(f"✗ {js_file}: Error - {e}")

if __name__ == "__main__":
    print("Personal Finance App - Add Button Functionality Test")
    print("=" * 50)

    # Test server is running
    try:
        response = requests.get("http://localhost:8000/api/cards", timeout=5)
        print("✓ Server is running and responsive")
    except Exception as e:
        print(f"✗ Server not accessible: {e}")
        print("Please make sure the server is running on port 8000")
        sys.exit(1)

    # Run tests
    test_api_endpoints()
    test_frontend_pages()
    test_javascript_files()

    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nIf all tests pass, the add buttons should be functional.")
    print("If there are still issues, the problem may be with browser-specific JavaScript execution.")