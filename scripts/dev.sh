#!/bin/bash

# MindTube Development Script
# Starts both backend and frontend in development mode

set -e

echo "🚀 Starting MindTube Development Environment"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before continuing."
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed."
    exit 1
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/{artifacts,cache,logs}

# Backend setup
echo "🐍 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Starting backend server..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

cd ..

# Frontend setup
echo "⚛️  Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

cd ..

# Cleanup function
cleanup() {
    echo "🛑 Shutting down development servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ Development servers stopped."
}

# Set trap to cleanup on script exit
trap cleanup EXIT

echo ""
echo "🎉 MindTube development environment is running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
wait