#!/bin/bash

# MindTube Development Script
# Starts both backend and frontend in development mode

set -e

echo "🚀 Starting MindTube Development Environment"

# Check if backend .env file exists
if [ ! -f backend/.env ]; then
    echo "⚠️  Backend .env file not found. Copying from .env.example..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env file with your API keys before continuing."
fi

# Check if frontend .env file exists
if [ ! -f frontend/.env ]; then
    echo "⚠️  Frontend .env file not found. Copying from .env.example..."
    cp frontend/.env.example frontend/.env
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

# Check if uv is installed
if ! command_exists uv; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Setup backend using Makefile
echo "Setting up backend environment..."
make setup

echo "Starting backend server..."
make run &
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