#!/bin/bash

# Personal Finance Management Application Startup Script
# This script handles all necessary steps to run the application

set -e  # Exit on any error

echo "🚀 Starting Personal Finance Management Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to find an available port
find_available_port() {
    local start_port=$1
    local port=$start_port

    while [ $port -le 9000 ]; do
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo $port
            return 0
        fi
        port=$((port + 1))
    done

    print_error "No available ports found between $start_port and 9000"
    exit 1
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_warning ".env file not found. Copying from .env.example..."
        cp .env.example .env
        print_success ".env file created from example"
    else
        print_error ".env file not found and no .env.example available"
        exit 1
    fi
fi

# Check if database directory exists
if [ ! -d "data" ]; then
    print_status "Creating data directory..."
    mkdir -p data
    print_success "Data directory created"
fi

# Check if database exists and initialize if needed
if [ ! -f "data/finance.db" ]; then
    print_status "Database not found. Initializing database..."
    if [ -f "backend/src/database/init_db.py" ]; then
        python3 backend/src/database/init_db.py
        print_success "Database initialized"
    else
        print_warning "Database initialization script not found. Database will be created on first run."
    fi
else
    print_status "Database exists. Ensuring schema is up to date..."
    if [ -f "backend/src/database/init_db.py" ]; then
        python3 backend/src/database/init_db.py
        print_success "Database schema verified"
    fi
fi

# Find an available port starting from 8000
AVAILABLE_PORT=$(find_available_port 8000)

if [ $AVAILABLE_PORT -ne 8000 ]; then
    print_warning "Port 8000 is in use. Using port $AVAILABLE_PORT instead."
fi

# Start the server
print_status "Starting server on http://localhost:$AVAILABLE_PORT..."

# Update .env file with the available port
if [ $AVAILABLE_PORT -ne 8000 ]; then
    print_status "Updating .env file with port $AVAILABLE_PORT..."
    # Backup original .env
    cp .env .env.backup
    # Update SERVER_PORT in .env file
    if grep -q "^SERVER_PORT=" .env; then
        sed -i.bak "s/^SERVER_PORT=.*/SERVER_PORT=$AVAILABLE_PORT/" .env
    else
        echo "SERVER_PORT=$AVAILABLE_PORT" >> .env
    fi
    # Update CORS_ORIGINS in .env file
    if grep -q "^CORS_ORIGINS=" .env; then
        sed -i.bak "s|^CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:$AVAILABLE_PORT,http://127.0.0.1:$AVAILABLE_PORT|" .env
    else
        echo "CORS_ORIGINS=http://localhost:$AVAILABLE_PORT,http://127.0.0.1:$AVAILABLE_PORT" >> .env
    fi
fi

# Try the main server first, fallback to simple server
if [ -f "backend/src/server.py" ]; then
    print_status "Using main application server..."
    python3 backend/src/server.py &
    SERVER_PID=$!
elif [ -f "simple_server.py" ]; then
    print_status "Using simple server..."
    SERVER_PORT=$AVAILABLE_PORT python3 simple_server.py &
    SERVER_PID=$!
else
    print_error "No server file found"
    exit 1
fi

# Wait a moment for server to start
sleep 3

# Check if server is listening on the port
if lsof -Pi :$AVAILABLE_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_success "Server started successfully!"
    echo ""
    echo "📊 Personal Finance Management Application is running!"
    echo ""
    echo "🌐 Dashboard:     http://localhost:$AVAILABLE_PORT/"
    echo "💳 Transactions:  http://localhost:$AVAILABLE_PORT/pages/transactions.html"
    echo "⚙️  Manage Cards:  http://localhost:$AVAILABLE_PORT/pages/manage.html"
    echo "📈 Movements:     http://localhost:$AVAILABLE_PORT/pages/movements.html"
    echo ""
    echo "📝 Server PID: $SERVER_PID"
    echo "🛑 To stop the server: kill $SERVER_PID"
    echo ""

    # Try to open in default browser
    if command -v open &> /dev/null; then
        print_status "Opening application in browser..."
        open http://localhost:$AVAILABLE_PORT
    elif command -v xdg-open &> /dev/null; then
        print_status "Opening application in browser..."
        xdg-open http://localhost:$AVAILABLE_PORT
    fi

    # Keep script running to show server logs
    echo "Press Ctrl+C to stop the server"

    # Cleanup function for temporary files
    cleanup() {
        print_status "Cleaning up..."
        kill $SERVER_PID 2>/dev/null || true
        # Restore original .env if we made a backup
        if [ -f ".env.backup" ]; then
            print_status "Restoring original .env file..."
            mv .env.backup .env
        fi
        rm -f .env.bak
        exit 0
    }

    trap cleanup INT TERM

    wait $SERVER_PID
else
    print_error "Server failed to start or is not responding"
    kill $SERVER_PID 2>/dev/null || true
    # Restore original .env if we made a backup
    if [ -f ".env.backup" ]; then
        print_status "Restoring original .env file..."
        mv .env.backup .env
    fi
    rm -f .env.bak
    exit 1
fi