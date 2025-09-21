#!/usr/bin/env python3
"""
Minimal HTTP server for Personal Finance Management Application.
Uses Python standard library only (constitutional requirement).
"""

import os
import json
import sqlite3
import time
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import mimetypes
import logging


class FinanceAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Personal Finance API."""

    # Class-level rate limiting tracking
    request_counts = defaultdict(list)
    blocked_ips = set()

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
            'CORS_ORIGINS': 'http://localhost:8000,http://127.0.0.1:8000',
            'RATE_LIMIT_REQUESTS': 100,
            'RATE_LIMIT_WINDOW': 60
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
                                elif key in ['RATE_LIMIT_REQUESTS', 'RATE_LIMIT_WINDOW']:
                                    config[key] = int(value)
                                else:
                                    config[key] = value
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")

        return config

    def _sanitize_input(self, data):
        """Basic input sanitization for security."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                sanitized[self._sanitize_input(key)] = self._sanitize_input(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_input(item) for item in data]
        elif isinstance(data, str):
            # Basic sanitization - remove potentially dangerous characters
            # For a local app, this is basic protection
            dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
            sanitized = data
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, '')
            return sanitized.strip()
        else:
            return data

    def _validate_content_length(self, max_size=1024*1024):  # 1MB default
        """Validate request content length to prevent DoS."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > max_size:
            self._send_error(413, f'Request too large. Maximum size is {max_size} bytes.')
            return False
        return True

    def _check_rate_limit(self):
        """Check if client is within rate limits."""
        client_ip = self.client_address[0]
        current_time = time.time()

        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            return False

        # Clean old requests
        window = self.config.get('RATE_LIMIT_WINDOW', 60)
        cutoff_time = current_time - window
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if req_time > cutoff_time
        ]

        # Check current request count
        max_requests = self.config.get('RATE_LIMIT_REQUESTS', 100)
        if len(self.request_counts[client_ip]) >= max_requests:
            # Block IP for security (local app, so be more lenient)
            if len(self.request_counts[client_ip]) > max_requests * 2:
                self.blocked_ips.add(client_ip)
            return False

        # Add current request
        self.request_counts[client_ip].append(current_time)
        return True

    def do_GET(self):
        """Handle GET requests."""
        # Check rate limit first
        if not self._check_rate_limit():
            self._send_error(429, 'Too many requests. Please slow down.')
            return

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
        # Check rate limit first
        if not self._check_rate_limit():
            self._send_error(429, 'Too many requests. Please slow down.')
            return

        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Add CORS headers
        self._add_cors_headers()

        if path.startswith('/api/'):
            # Validate content length
            if not self._validate_content_length():
                return

            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''

            try:
                request_data = json.loads(post_data) if post_data else {}
                # Sanitize input data
                request_data = self._sanitize_input(request_data)
            except json.JSONDecodeError:
                self._send_error(400, 'Invalid JSON format', {'hint': 'Please ensure your request body contains valid JSON'})
                return

            self._handle_api_request('POST', path, request_data)
        else:
            self.send_error(404)

    def do_PUT(self):
        """Handle PUT requests."""
        # Check rate limit first
        if not self._check_rate_limit():
            self._send_error(429, 'Too many requests. Please slow down.')
            return

        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Add CORS headers
        self._add_cors_headers()

        if path.startswith('/api/'):
            # Validate content length
            if not self._validate_content_length():
                return

            content_length = int(self.headers.get('Content-Length', 0))
            put_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''

            try:
                request_data = json.loads(put_data) if put_data else {}
                # Sanitize input data
                request_data = self._sanitize_input(request_data)
            except json.JSONDecodeError:
                self._send_error(400, 'Invalid JSON format', {'hint': 'Please ensure your request body contains valid JSON'})
                return

            self._handle_api_request('PUT', path, request_data)
        else:
            self.send_error(404)

    def do_DELETE(self):
        """Handle DELETE requests."""
        # Check rate limit first
        if not self._check_rate_limit():
            self._send_error(429, 'Too many requests. Please slow down.')
            return

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
        # Get allowed origins from config
        allowed_origins = self.config.get('CORS_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')

        # Check if request origin is allowed
        origin = self.headers.get('Origin')
        if origin and origin in allowed_origins:
            self.send_header('Access-Control-Allow-Origin', origin)
        elif not origin:  # Direct access (same origin)
            self.send_header('Access-Control-Allow-Origin', allowed_origins[0])
        else:
            # For local development, allow localhost variations
            if any(origin.startswith(prefix) for prefix in ['http://localhost:', 'http://127.0.0.1:']):
                self.send_header('Access-Control-Allow-Origin', origin)
            else:
                self.send_header('Access-Control-Allow-Origin', allowed_origins[0])

        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours

        # Basic security headers for local app
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')

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
        """Handle transactions API requests."""
        try:
            # Import API module
            import sys
            from pathlib import Path
            backend_path = Path(__file__).parent
            sys.path.insert(0, str(backend_path))

            from api.transactions import handle_transactions_api

            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            # Handle request
            status_code, response_data = handle_transactions_api(
                method, path, query_params, data, self.config['DATABASE_PATH']
            )

            if status_code == 204:
                self.send_response(204)
                self._add_cors_headers()
                self.end_headers()
            else:
                self._send_json(response_data, status_code)

        except Exception as e:
            self._send_error(500, f'Transactions API error: {str(e)}')

    def _handle_investments_api(self, method, path, data):
        """Handle investments API requests."""
        try:
            # Import API module
            import sys
            from pathlib import Path
            backend_path = Path(__file__).parent
            sys.path.insert(0, str(backend_path))

            from api.investments import handle_investments_api

            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            # Handle request
            status_code, response_data = handle_investments_api(
                method, path, query_params, data, self.config['DATABASE_PATH']
            )

            self._send_json(response_data, status_code)

        except Exception as e:
            self._send_error(500, f'Investments API error: {str(e)}')

    def _handle_dashboard_api(self, method, path, data):
        """Handle dashboard API requests."""
        try:
            # Import API module
            import sys
            from pathlib import Path
            backend_path = Path(__file__).parent
            sys.path.insert(0, str(backend_path))

            from api.dashboard import handle_dashboard_api

            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            # Handle request
            status_code, response_data = handle_dashboard_api(
                method, path, query_params, data, self.config['DATABASE_PATH']
            )

            self._send_json(response_data, status_code)

        except Exception as e:
            self._send_error(500, f'Dashboard API error: {str(e)}')

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
            # Security check: ensure file is within frontend directory
            try:
                file_path.resolve().relative_to(frontend_root.resolve())
            except ValueError:
                self.send_error(403, 'Access denied')
                return

            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = 'application/octet-stream'

            self.send_response(200)
            self.send_header('Content-Type', content_type)

            # Add caching headers for static assets
            file_ext = file_path.suffix.lower()
            if file_ext in ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']:
                # Cache static assets for 1 hour
                self.send_header('Cache-Control', 'public, max-age=3600')
            elif file_ext in ['.html']:
                # Don't cache HTML files for development
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')

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

    def _send_error(self, status_code, message, details=None):
        """Send structured error response."""
        error_response = {
            'error': message,
            'status_code': status_code,
            'timestamp': time.time()
        }

        if details:
            error_response['details'] = details

        # Add helpful error descriptions
        error_descriptions = {
            400: "Bad Request - The request was invalid or malformed",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Access to this resource is denied",
            404: "Not Found - The requested resource was not found",
            405: "Method Not Allowed - This HTTP method is not supported for this endpoint",
            409: "Conflict - The request conflicts with the current state",
            429: "Too Many Requests - Rate limit exceeded",
            500: "Internal Server Error - An unexpected error occurred"
        }

        if status_code in error_descriptions:
            error_response['description'] = error_descriptions[status_code]

        self._send_json(error_response, status_code)

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