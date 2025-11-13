#!/usr/bin/env python3
"""
Simple test server for frontend
"""

import http.server
import socketserver
import json
import os
from urllib.parse import urlparse

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)

        if parsed_path.path.startswith('/api/'):
            self.handle_api_request(parsed_path.path)
        else:
            # Serve static files from frontend directory
            if self.path == '/':
                self.path = '/pages/dashboard.html'

            # Adjust path for frontend directory structure
            if self.path.startswith('/pages/') or self.path.startswith('/css/') or self.path.startswith('/js/'):
                file_path = 'frontend' + self.path
            else:
                file_path = 'frontend' + self.path

            try:
                with open(file_path, 'rb') as f:
                    content = f.read()

                # Determine content type
                content_type = 'text/html'
                if file_path.endswith('.css'):
                    content_type = 'text/css'
                elif file_path.endswith('.js'):
                    content_type = 'application/javascript'

                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(content)

            except FileNotFoundError:
                self.send_error(404, f"File not found: {file_path}")

    def handle_api_request(self, path):
        """Handle API requests with mock data"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        # Mock responses
        if path == '/api/cards':
            response = [
                {"id": 1, "name": "Main Checking", "type": "debit", "balance": 1500.00, "currency": "MXN"},
                {"id": 2, "name": "Credit Card", "type": "credit", "balance": -300.00, "credit_limit": 5000.00, "currency": "MXN"}
            ]
        elif path == '/api/transactions':
            response = {
                "transactions": [
                    {"id": 1, "amount": -50.00, "description": "Grocery Store", "transaction_date": "2024-01-15", "category": "Food"},
                    {"id": 2, "amount": -25.00, "description": "Coffee Shop", "transaction_date": "2024-01-14", "category": "Food"},
                    {"id": 3, "amount": 2000.00, "description": "Salary", "transaction_date": "2024-01-01", "category": "Income"}
                ],
                "total": 3,
                "page": 1,
                "has_next": False
            }
        elif path == '/api/dashboard/summary':
            response = {
                "total_balance": 1200.00,
                "total_credit_available": 4700.00,
                "total_investments_value": 3500.00,
                "period_income": 2000.00,
                "period_expenses": -800.00,
                "period_profit_loss": 1200.00
            }
        elif path == '/api/dashboard/charts':
            response = {
                "chart_type": "balance_trend",
                "labels": ["Jan 1", "Jan 8", "Jan 15", "Jan 22", "Jan 29"],
                "datasets": [
                    {
                        "label": "Balance",
                        "data": [1000, 1100, 1050, 1200, 1200],
                        "backgroundColor": "rgba(54, 162, 235, 0.2)",
                        "borderColor": "rgba(54, 162, 235, 1)"
                    }
                ]
            }
        elif path == '/api/investments/positions':
            response = [
                {"id": 1, "asset_type": "stock", "symbol": "AAPL", "current_quantity": 10, "current_value": 1500.00},
                {"id": 2, "asset_type": "crypto", "symbol": "BTC", "current_quantity": 0.05, "current_value": 2000.00}
            ]
        else:
            response = {"error": "Endpoint not implemented"}

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle POST requests"""
        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {"message": "Created successfully", "id": 123}
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    import sys
    # Read port from environment variable or command line argument
    PORT = int(os.environ.get('SERVER_PORT', 8000))
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)

    with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
        print(f"🚀 Simple server running at http://localhost:{PORT}")
        print(f"📊 Dashboard: http://localhost:{PORT}/")
        print(f"💳 Transactions: http://localhost:{PORT}/pages/transactions.html")
        print(f"⚙️ Manage: http://localhost:{PORT}/pages/manage.html")
        print(f"📈 Investments: http://localhost:{PORT}/pages/movements.html")
        httpd.serve_forever()