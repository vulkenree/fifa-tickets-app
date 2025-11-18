#!/bin/bash
# Test login flow locally

BACKEND_URL="http://localhost:8000"
COOKIE_FILE="/tmp/test_cookies.txt"

echo "=========================================="
echo "Testing Login Flow Locally"
echo "=========================================="
echo ""

# Step 1: Test health
echo "1. Testing backend health..."
HEALTH=$(curl -s http://localhost:8000/health)
if [ $? -eq 0 ]; then
    echo "   ✅ Backend is running"
    echo "   Response: $HEALTH" | head -3
else
    echo "   ❌ Backend is not responding"
    exit 1
fi
echo ""

# Step 2: Login
echo "2. Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c $COOKIE_FILE \
  -w "\nHTTP_STATUS:%{http_code}")

HTTP_STATUS=$(echo "$LOGIN_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" = "200" ]; then
    echo "   ✅ Login successful (Status: $HTTP_STATUS)"
    echo "   Response: $LOGIN_BODY"
    
    # Check cookie file
    if [ -f "$COOKIE_FILE" ]; then
        echo "   ✅ Session cookie saved"
        echo "   Cookie content:"
        cat $COOKIE_FILE | grep -v "^#" | head -2
    else
        echo "   ❌ No cookie file created"
    fi
else
    echo "   ❌ Login failed (Status: $HTTP_STATUS)"
    echo "   Response: $LOGIN_BODY"
    exit 1
fi
echo ""

# Step 3: Extract user info from login
LOGIN_USER_ID=$(echo "$LOGIN_BODY" | grep -o '"id":[0-9]*' | cut -d: -f2)
LOGIN_USERNAME=$(echo "$LOGIN_BODY" | grep -o '"username":"[^"]*"' | cut -d: -f2 | tr -d '"')

echo "   Login returned:"
echo "   - User ID: $LOGIN_USER_ID"
echo "   - Username: $LOGIN_USERNAME"
echo ""

# Step 4: Test /api/auth/me
echo "3. Testing /api/auth/me endpoint..."
ME_RESPONSE=$(curl -s http://localhost:8000/api/auth/me \
  -b $COOKIE_FILE \
  -w "\nHTTP_STATUS:%{http_code}")

ME_HTTP_STATUS=$(echo "$ME_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
ME_BODY=$(echo "$ME_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$ME_HTTP_STATUS" = "200" ]; then
    echo "   ✅ /api/auth/me successful (Status: $ME_HTTP_STATUS)"
    echo "   Response: $ME_BODY"
    
    # Extract user info from /me
    ME_USER_ID=$(echo "$ME_BODY" | grep -o '"id":[0-9]*' | cut -d: -f2)
    ME_USERNAME=$(echo "$ME_BODY" | grep -o '"username":"[^"]*"' | cut -d: -f2 | tr -d '"')
    
    echo "   /me returned:"
    echo "   - User ID: $ME_USER_ID"
    echo "   - Username: $ME_USERNAME"
    echo ""
    
    # Step 5: Verify users match
    echo "4. Verifying user consistency..."
    if [ "$LOGIN_USER_ID" = "$ME_USER_ID" ] && [ "$LOGIN_USERNAME" = "$ME_USERNAME" ]; then
        echo "   ✅ SUCCESS: User matches between login and /me"
        echo "   - Same User ID: $LOGIN_USER_ID"
        echo "   - Same Username: $ME_USERNAME"
    else
        echo "   ❌ ERROR: User mismatch!"
        echo "   Login: ID=$LOGIN_USER_ID, Username=$LOGIN_USERNAME"
        echo "   /me:   ID=$ME_USER_ID, Username=$ME_USERNAME"
        exit 1
    fi
else
    echo "   ❌ /api/auth/me failed (Status: $ME_HTTP_STATUS)"
    echo "   Response: $ME_BODY"
    echo ""
    echo "   This indicates the session cookie is not being recognized."
    exit 1
fi
echo ""

# Step 6: Test session debug endpoint
echo "5. Testing /api/debug/session endpoint..."
DEBUG_RESPONSE=$(curl -s http://localhost:8000/api/debug/session -b $COOKIE_FILE)
echo "   Response: $DEBUG_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "   $DEBUG_RESPONSE"
echo ""

# Cleanup
rm -f $COOKIE_FILE

echo "=========================================="
echo "✅ All tests passed!"
echo "=========================================="

