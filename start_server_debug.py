#!/usr/bin/env python3
"""
Debug server startup
"""

import sys
import os
from pathlib import Path
import traceback

# Add backend/src to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))
os.chdir(backend_src)

try:
    print("🔄 Starting server debug...")

    # Import server components
    from server import FinanceAPIHandler
    print("✅ Server import successful")

    # Try to create an instance
    from http.server import HTTPServer

    server_address = ('localhost', 8000)
    print(f"🔄 Attempting to bind to {server_address}")

    httpd = HTTPServer(server_address, FinanceAPIHandler)
    print("✅ Server created successfully")

    print(f"🚀 Server starting on http://localhost:8000")
    httpd.serve_forever()

except Exception as e:
    print(f"❌ Server error: {e}")
    traceback.print_exc()