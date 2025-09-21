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
        """Handle cards API requests (placeholder)."""
        self._send_json({'message': 'Cards API placeholder', 'method': method, 'path': path})

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