#!/usr/bin/env python3
"""
Quick diagnostic script to test production authentication
Run: python quick_debug.py <backend-url> <username> <password>
"""

import requests
import sys

if len(sys.argv) < 4:
    print("Usage: python quick_debug.py <BACKEND_URL> <username> <password>")
    print("Example: python quick_debug.py https://fifa-tickets-backend-production.up.railway.app admin admin123")
    sys.exit(1)

backend_url = sys.argv[1].rstrip('/')
username = sys.argv[2]
password = sys.argv[3]

print("="*80)
print("PRODUCTION AUTHENTICATION DIAGNOSTIC")
print("="*80)
print(f"Backend URL: {backend_url}\n")

# Test 1: Health check
print("1. Testing health endpoint...")
try:
    r = requests.get(f"{backend_url}/health", timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print("   ✅ Backend is running")
        data = r.json()
        print(f"   Database: {data.get('database', 'unknown')}")
    else:
        print(f"   ❌ Backend health check failed: {r.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Login
print("\n2. Testing login...")
try:
    r = requests.post(
        f"{backend_url}/api/auth/login",
        json={"username": username, "password": password},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print(f"   Status: {r.status_code}")
    
    if r.status_code == 200:
        print("   ✅ Login successful")
        user_data = r.json()
        print(f"   User: {user_data.get('username')} (ID: {user_data.get('id')})")
        
        # Check for session cookie
        cookies = r.cookies
        session_cookie = cookies.get('session')
        if session_cookie:
            print(f"   ✅ Session cookie received: {session_cookie[:30]}...")
            
            # Check Set-Cookie header
            set_cookie = r.headers.get('Set-Cookie', '')
            print(f"   Cookie attributes:")
            if 'Secure' in set_cookie:
                print("      ✅ Secure")
            else:
                print("      ❌ Missing Secure")
            if 'HttpOnly' in set_cookie:
                print("      ✅ HttpOnly")
            else:
                print("      ❌ Missing HttpOnly")
            if 'SameSite=None' in set_cookie:
                print("      ✅ SameSite=None")
            else:
                print("      ❌ Missing SameSite=None")
        else:
            print("   ❌ NO SESSION COOKIE RECEIVED!")
            print("   This is the problem - session cookie not being set")
            sys.exit(1)
    else:
        print(f"   ❌ Login failed: {r.text[:200]}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Session debug endpoint
print("\n3. Testing session debug endpoint...")
try:
    r = requests.get(
        f"{backend_url}/api/debug/session",
        cookies=cookies,
        timeout=10
    )
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        session_info = r.json()
        print("   ✅ Session debug info:")
        print(f"      Has session: {session_info.get('has_session')}")
        print(f"      Session keys: {session_info.get('session_keys')}")
        print(f"      User ID: {session_info.get('user_id')}")
        print(f"      Username: {session_info.get('username')}")
        print(f"      Permanent: {session_info.get('permanent')}")
        print(f"      Cookies received: {session_info.get('cookies_received')}")
        
        if not session_info.get('user_id'):
            print("\n   ❌ PROBLEM: Session exists but user_id is missing!")
            print("   This means the session cookie is not being read correctly")
    else:
        print(f"   ❌ Failed: {r.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Authenticated endpoint
print("\n4. Testing /api/auth/me endpoint...")
try:
    r = requests.get(
        f"{backend_url}/api/auth/me",
        cookies=cookies,
        timeout=10
    )
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        user_data = r.json()
        print(f"   ✅ Authentication successful")
        print(f"   User: {user_data.get('username')} (ID: {user_data.get('id')})")
    elif r.status_code == 401:
        print("   ❌ 401 UNAUTHORIZED - This is the issue!")
        print(f"   Error: {r.text[:200]}")
        print("\n   Possible causes:")
        print("   - Session cookie not being sent (check cookies variable)")
        print("   - Session not in database (Flask-Session not working)")
        print("   - SECRET_KEY changed")
        print("   - Session expired")
    else:
        print(f"   ❌ Unexpected status: {r.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Tickets endpoint
print("\n5. Testing /api/tickets endpoint...")
try:
    r = requests.get(
        f"{backend_url}/api/tickets",
        cookies=cookies,
        timeout=10
    )
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        tickets = r.json()
        count = len(tickets) if isinstance(tickets, list) else 0
        print(f"   ✅ Tickets retrieved: {count} tickets")
    elif r.status_code == 401:
        print("   ❌ 401 UNAUTHORIZED")
    else:
        print(f"   ❌ Status {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
print("\nNext steps:")
print("1. Check Railway backend logs for Flask-Session errors")
print("2. Verify sessions table exists in PostgreSQL")
print("3. Check SECRET_KEY is set and stable in Railway")
print("4. Verify NEXT_PUBLIC_API_URL is set in frontend build")

