#!/bin/bash
# Test profile authentication in production

if [ -z "$1" ]; then
    echo "Usage: ./test_profile_auth.sh <BACKEND_URL> [username] [password]"
    echo "Example: ./test_profile_auth.sh https://fifa-tickets-backend-production.up.railway.app admin admin123"
    exit 1
fi

BACKEND_URL="$1"
USERNAME="${2:-admin}"
PASSWORD="${3:-admin123}"
COOKIE_FILE="/tmp/profile_test_cookies.txt"

echo "=========================================="
echo "Testing Profile Authentication"
echo "=========================================="
echo "Backend URL: $BACKEND_URL"
echo ""

# Step 1: Login
echo "1. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" \
  -c "$COOKIE_FILE" \
  -w "\nHTTP_STATUS:%{http_code}")

HTTP_STATUS=$(echo "$LOGIN_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" != "200" ]; then
    echo "   ❌ Login failed (Status: $HTTP_STATUS)"
    echo "   Response: $LOGIN_BODY"
    exit 1
fi

echo "   ✅ Login successful"
echo "   Response: $LOGIN_BODY"
echo ""

# Step 2: Check cookie
echo "2. Checking session cookie..."
if [ -f "$COOKIE_FILE" ]; then
    COOKIE_CONTENT=$(cat "$COOKIE_FILE" | grep -v "^#" | grep "session" | head -1)
    if [ -z "$COOKIE_CONTENT" ]; then
        echo "   ❌ No session cookie found in cookie file"
        exit 1
    fi
    echo "   ✅ Session cookie found"
    echo "   Cookie: ${COOKIE_CONTENT:0:80}..."
else
    echo "   ❌ Cookie file not created"
    exit 1
fi
echo ""

# Step 3: Test /api/auth/me
echo "3. Testing /api/auth/me..."
ME_RESPONSE=$(curl -s "$BACKEND_URL/api/auth/me" \
  -b "$COOKIE_FILE" \
  -w "\nHTTP_STATUS:%{http_code}")

ME_HTTP_STATUS=$(echo "$ME_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
ME_BODY=$(echo "$ME_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$ME_HTTP_STATUS" = "200" ]; then
    echo "   ✅ /api/auth/me successful"
    echo "   Response: $ME_BODY"
else
    echo "   ❌ /api/auth/me failed (Status: $ME_HTTP_STATUS)"
    echo "   Response: $ME_BODY"
    echo "   This indicates session cookie is not being recognized"
fi
echo ""

# Step 4: Test /api/profile
echo "4. Testing /api/profile..."
PROFILE_RESPONSE=$(curl -s "$BACKEND_URL/api/profile" \
  -b "$COOKIE_FILE" \
  -w "\nHTTP_STATUS:%{http_code}")

PROFILE_HTTP_STATUS=$(echo "$PROFILE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
PROFILE_BODY=$(echo "$PROFILE_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$PROFILE_HTTP_STATUS" = "200" ]; then
    echo "   ✅ /api/profile successful"
    echo "   Response: $PROFILE_BODY"
else
    echo "   ❌ /api/profile failed (Status: $PROFILE_HTTP_STATUS)"
    echo "   Response: $PROFILE_BODY"
    echo ""
    echo "   This is the error you're seeing in production!"
    echo ""
    echo "   Possible causes:"
    echo "   - Cookie not being sent (check Network tab in browser)"
    echo "   - Cookie attributes wrong (Secure/SameSite)"
    echo "   - Session not in database"
    echo "   - CORS configuration issue"
fi
echo ""

# Step 5: Check cookie attributes from login
echo "5. Checking cookie attributes from login response..."
LOGIN_HEADERS=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" \
  -D - -o /dev/null 2>&1 | grep -i "set-cookie")

echo "   Set-Cookie header:"
echo "   $LOGIN_HEADERS"
echo ""

# Check for required attributes
if echo "$LOGIN_HEADERS" | grep -qi "Secure"; then
    echo "   ✅ Secure flag present"
else
    echo "   ❌ Secure flag MISSING (required for HTTPS)"
fi

if echo "$LOGIN_HEADERS" | grep -qi "SameSite=None"; then
    echo "   ✅ SameSite=None present"
else
    echo "   ❌ SameSite=None MISSING (required for cross-origin)"
fi

if echo "$LOGIN_HEADERS" | grep -qi "HttpOnly"; then
    echo "   ✅ HttpOnly flag present"
else
    echo "   ❌ HttpOnly flag MISSING"
fi

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="

# Cleanup
rm -f "$COOKIE_FILE"

