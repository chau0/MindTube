#!/bin/bash

# MindTube Server Test Script
# Tests that both backend and frontend servers can start and respond

set -e

echo "🧪 Testing MindTube Development Servers"

# Add uv to PATH if it exists
if [ -d "$HOME/.local/bin" ]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# Test Backend
echo ""
echo "🐍 Testing Backend Server..."
cd backend

# Test backend imports
echo "🔍 Testing backend imports..."
if uv run python -c "import app.main; print('Backend imports successful')" 2>/dev/null; then
    echo "✅ Backend imports working"
else
    echo "❌ Backend imports failed"
    exit 1
fi

# Test backend server startup
echo "🚀 Testing backend server startup..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

# Wait for server to start
sleep 3

# Test backend health endpoint
if curl -s http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ Backend server responding on port 8001"
    BACKEND_WORKING=true
else
    echo "❌ Backend server not responding"
    BACKEND_WORKING=false
fi

# Stop backend server
kill $BACKEND_PID 2>/dev/null || true
wait $BACKEND_PID 2>/dev/null || true

cd ..

# Test Frontend
echo ""
echo "⚛️  Testing Frontend Server..."
cd frontend

# Test frontend build
echo "🔍 Testing frontend TypeScript..."
if npm run type-check > /dev/null 2>&1; then
    echo "✅ Frontend TypeScript compilation successful"
else
    echo "❌ Frontend TypeScript compilation failed"
    exit 1
fi

# Test frontend server startup
echo "🚀 Testing frontend server startup..."
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!

# Wait for server to start
sleep 5

# Test frontend health
if curl -s -I http://localhost:3000/ > /dev/null 2>&1; then
    echo "✅ Frontend server responding on port 3000"
    FRONTEND_WORKING=true
else
    echo "❌ Frontend server not responding"
    FRONTEND_WORKING=false
fi

# Stop frontend server
kill $FRONTEND_PID 2>/dev/null || true
wait $FRONTEND_PID 2>/dev/null || true

cd ..

# Summary
echo ""
echo "📋 Test Summary:"
if [ "$BACKEND_WORKING" = true ]; then
    echo "✅ Backend: Working"
else
    echo "❌ Backend: Not working"
fi

if [ "$FRONTEND_WORKING" = true ]; then
    echo "✅ Frontend: Working"
else
    echo "❌ Frontend: Not working"
fi

if [ "$BACKEND_WORKING" = true ] && [ "$FRONTEND_WORKING" = true ]; then
    echo ""
    echo "🎉 All servers working! Ready for development."
    echo ""
    echo "To start development:"
    echo "  ./scripts/dev.sh"
    echo ""
    echo "Or manually:"
    echo "  Backend:  cd backend && uv run uvicorn app.main:app --reload --port 8000"
    echo "  Frontend: cd frontend && npm run dev"
    exit 0
else
    echo ""
    echo "⚠️  Some servers have issues. Check the logs above."
    exit 1
fi