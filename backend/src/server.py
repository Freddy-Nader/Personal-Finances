#!/usr/bin/env python3
"""
Minimal HTTP server for Personal Finance Management Application.
Uses Python standard library only (constitutional requirement).
"""

import os
import json
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import mimetypes
import logging


class FinanceAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Personal Finance API."""

    def __init__(self, *args, **kwargs):
        # Load configuration
        self.config = self._load_config()
        super().__init__(*args, **kwargs)

    def _load_config(self):
        """Load configuration from .env file."""
        config = {
            'DATABASE_PATH': './data/finance.db',
            'SERVER_PORT': 8000,
            'SERVER_HOST': 'localhost',
            'DEBUG_MODE': True,
            'DEFAULT_CURRENCY': 'MXN',
            'CORS_ORIGINS': 'http://localhost:8000,http://127.0.0.1:8000'
        }

        try:
            env_path = Path(__file__).parent.parent.parent / '.env'
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            if key in config:
                                if key == 'SERVER_PORT':
                                    config[key] = int(value)
                                elif key == 'DEBUG_MODE':
                                    config[key] = value.lower() == 'true'
                                else:
                                    config[key] = value
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")

        return config

    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        # Add CORS headers
        self._add_cors_headers()

        if path.startswith('/api/'):
            self._handle_api_request('GET', path, query_params)
        else:
            self._serve_static_file(path)

    def do_POST(self):
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Add CORS headers
        self._add_cors_headers()

        if path.startswith('/api/'):
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''

            try:
                request_data = json.loads(post_data) if post_data else {}
            except json.JSONDecodeError:
                self._send_error(400, 'Invalid JSON')
                return

            self._handle_api_request('POST', path, request_data)
        else:
            self.send_error(404)

    def do_PUT(self):
        """Handle PUT requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Add CORS headers
        self._add_cors_headers()

        if path.startswith('/api/'):
            content_length = int(self.headers.get('Content-Length', 0))
            put_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''

            try:
                request_data = json.loads(put_data) if put_data else {}
            except json.JSONDecodeError:
                self._send_error(400, 'Invalid JSON')
                return

            self._handle_api_request('PUT', path, request_data)
        else:
            self.send_error(404)

    def do_DELETE(self):
        """Handle DELETE requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Add CORS headers
        self._add_cors_headers()

        if path.startswith('/api/'):
            self._handle_api_request('DELETE', path, {})
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self._add_cors_headers()
        self.send_response(200)
        self.end_headers()

    def _add_cors_headers(self):
        """Add CORS headers for local development."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def _handle_api_request(self, method, path, data):
        """Route API requests to appropriate handlers."""

        # Remove /api prefix
        api_path = path[4:]

        # Basic routing structure (will be expanded in later tasks)
        if api_path.startswith('/cards'):
            self._handle_cards_api(method, api_path, data)
        elif api_path.startswith('/transactions'):
            self._handle_transactions_api(method, api_path, data)
        elif api_path.startswith('/investments'):
            self._handle_investments_api(method, api_path, data)
        elif api_path.startswith('/dashboard'):
            self._handle_dashboard_api(method, api_path, data)
        else:
            self._send_error(404, 'API endpoint not found')

    def _handle_cards_api(self, method, path, data):
        """Handle cards API requests."""
        try:
            # Import services here to avoid circular imports
            import sys
            from pathlib import Path
            backend_path = Path(__file__).parent
            sys.path.insert(0, str(backend_path))

            from services.card_service import CardService
            from services.section_service import SectionService

            # Remove /cards prefix and parse path
            api_path = path[6:]  # Remove '/cards'

            if api_path == '' or api_path == '/':
                if method == 'GET':
                    # GET /api/cards
                    cards = CardService.get_all_cards()
                    self._send_json([card.to_dict() for card in cards])
                elif method == 'POST':
                    # POST /api/cards
                    errors = CardService.validate_card_data(data)
                    if errors:
                        self._send_error(400, f"Validation errors: {', '.join(errors)}")
                        return

                    card = CardService.create_card(data)
                    self._send_json(card.to_dict(), 201)
                else:
                    self._send_error(405, 'Method not allowed')

            elif api_path.startswith('/') and api_path.count('/') == 1:
                # Path like /123 or /123/sections
                path_parts = api_path.strip('/').split('/')

                try:
                    card_id = int(path_parts[0])
                except ValueError:
                    self._send_error(400, 'Invalid card ID format')
                    return

                if len(path_parts) == 1:
                    # /api/cards/{cardId}
                    if method == 'GET':
                        card = CardService.get_card_by_id(card_id)
                        if card:
                            self._send_json(card.to_dict())
                        else:
                            self._send_error(404, 'Card not found')
                    elif method == 'PUT':
                        try:
                            card = CardService.update_card(card_id, data)
                            self._send_json(card.to_dict())
                        except ValueError as e:
                            self._send_error(404 if 'not found' in str(e) else 400, str(e))
                    elif method == 'DELETE':
                        try:
                            CardService.delete_card(card_id)
                            self.send_response(204)
                            self._add_cors_headers()
                            self.end_headers()
                        except ValueError as e:
                            self._send_error(404 if 'not found' in str(e) else 400, str(e))
                    else:
                        self._send_error(405, 'Method not allowed')

                elif len(path_parts) == 2 and path_parts[1] == 'sections':
                    # /api/cards/{cardId}/sections
                    if method == 'GET':
                        # Check if card exists
                        card = CardService.get_card_by_id(card_id)
                        if not card:
                            self._send_error(404, 'Card not found')
                            return

                        sections = SectionService.get_sections_by_card_id(card_id)
                        self._send_json([section.to_dict() for section in sections])
                    elif method == 'POST':
                        # Check if card exists
                        card = CardService.get_card_by_id(card_id)
                        if not card:
                            self._send_error(404, 'Card not found')
                            return

                        # Add card_id to data
                        data['card_id'] = card_id
                        try:
                            section = SectionService.create_section(data)
                            self._send_json(section.to_dict(), 201)
                        except ValueError as e:
                            if 'already exists' in str(e):
                                self._send_error(409, str(e))
                            else:
                                self._send_error(400, str(e))
                    else:
                        self._send_error(405, 'Method not allowed')
                else:
                    self._send_error(404, 'API endpoint not found')
            else:
                self._send_error(404, 'API endpoint not found')

        except Exception as e:
            if self.config.get('DEBUG_MODE', True):
                print(f"Error in cards API: {e}")
            self._send_error(500, 'Internal server error')

    def _handle_transactions_api(self, method, path, data):
        """Handle transactions API requests (placeholder)."""
        self._send_json({'message': 'Transactions API placeholder', 'method': method, 'path': path})

    def _handle_investments_api(self, method, path, data):
        """Handle investments API requests (placeholder)."""
        self._send_json({'message': 'Investments API placeholder', 'method': method, 'path': path})

    def _handle_dashboard_api(self, method, path, data):
        """Handle dashboard API requests (placeholder)."""
        self._send_json({'message': 'Dashboard API placeholder', 'method': method, 'path': path})

    def _serve_static_file(self, path):
        """Serve static files from frontend directory."""

        # Default to index.html for root path
        if path == '/' or path == '':
            path = '/dashboard.html'

        # Map frontend paths
        frontend_root = Path(__file__).parent.parent.parent / 'frontend'

        if path.endswith('.html'):
            file_path = frontend_root / 'pages' / path.lstrip('/')
        elif path.startswith('/css/'):
            file_path = frontend_root / 'css' / path[5:]
        elif path.startswith('/js/'):
            file_path = frontend_root / 'js' / path[4:]
        elif path.startswith('/assets/'):
            file_path = frontend_root / 'assets' / path[8:]
        else:
            file_path = frontend_root / path.lstrip('/')

        if file_path.exists() and file_path.is_file():
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = 'application/octet-stream'

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self._add_cors_headers()
            self.end_headers()

            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, f'File not found: {path}')

    def _send_json(self, data, status_code=200):
        """Send JSON response."""
        response = json.dumps(data, indent=2)
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._add_cors_headers()
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    def _send_error(self, status_code, message):
        """Send error response."""
        self._send_json({'error': message}, status_code)

    def log_message(self, format, *args):
        """Override to control logging."""
        if self.config.get('DEBUG_MODE', True):
            super().log_message(format, *args)


def start_server():
    """Start the HTTP server."""

    # Load config for server settings
    config = {
        'SERVER_PORT': 8000,
        'SERVER_HOST': 'localhost'
    }

    try:
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        if key == 'SERVER_PORT':
                            config[key] = int(value)
                        elif key == 'SERVER_HOST':
                            config[key] = value
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")

    server_address = (config['SERVER_HOST'], config['SERVER_PORT'])
    httpd = HTTPServer(server_address, FinanceAPIHandler)

    print(f"Personal Finance Server starting on http://{config['SERVER_HOST']}:{config['SERVER_PORT']}")
    print("Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    finally:
        httpd.server_close()


if __name__ == '__main__':
    start_server()