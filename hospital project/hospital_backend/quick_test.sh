#!/bin/bash

# Quick Test Script
# Tests basic connectivity

echo "=================================="
echo "Quick Backend Test"
echo "=================================="
echo ""

# Check if server is running
echo "1. Checking if server is running..."
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "   ✓ Server is running"
else
    echo "   ✗ Server is not running"
    echo "   Start with: uvicorn main:app --reload"
    exit 1
fi

# Test health endpoint
echo ""
echo "2. Testing health endpoint..."
HEALTH=$(curl -s http://127.0.0.1:8000/health)
echo "   Response: $HEALTH"

# Test database connection
echo ""
echo "3. Testing database connection..."
DB_TEST=$(curl -s http://127.0.0.1:8000/test-db)
echo "   Response: $DB_TEST"

# Check API docs
echo ""
echo "4. API Documentation available at:"
echo "   http://127.0.0.1:8000/docs"

echo ""
echo "=================================="
echo "Quick test complete!"
echo "=================================="



