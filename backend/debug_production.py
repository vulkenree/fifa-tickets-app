#!/usr/bin/env python3
"""
Debug script to test production authentication and API endpoints.
This script helps identify issues with session management, cookies, and API connectivity.
"""

import requests
import json
import sys
from urllib.parse import urlparse

# Production URLs
FRONTEND_URL = "https://fifa-tickets-frontendapp-production.up.railway.app"
BACKEND_URL = None  # Will be determined from frontend or environment

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_result(success, message):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def test_health_endpoints(backend_url):
    """Test health check endpoints"""
    print_section("Testing Health Endpoints")
    
    endpoints = [
        ("/ping", "Basic ping endpoint"),
        ("/health", "Health check endpoint"),
        ("/health/detailed", "Detailed health check")
    ]
    
    results = {}
    for endpoint, description in endpoints:
        url = f"{backend_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            success = response.status_code == 200
            print_result(success, f"{description} ({endpoint}) - Status: {response.status_code}")
            if success:
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)}")
                    results[endpoint] = data
                except:
                    print(f"   Response: {response.text[:200]}")
            else:
                print(f"   Error: {response.text[:200]}")
        except Exception as e:
            print_result(False, f"{description} ({endpoint}) - Exception: {str(e)}")
            results[endpoint] = None
    
    return results

def test_login(backend_url, username, password):
    """Test login endpoint and verify session cookie"""
    print_section("Testing Authentication Flow")
    
    login_url = f"{backend_url}/api/auth/login"
    
    print(f"Login URL: {login_url}")
    print(f"Username: {username}")
    
    try:
        # Login request
        response = requests.post(
            login_url,
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10,
            allow_redirects=False
        )
        
        print(f"\nLogin Response Status: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['set-cookie', 'content-type', 'access-control-allow-credentials', 
                              'access-control-allow-origin', 'access-control-allow-methods']:
                print(f"  {key}: {value}")
        
        # Check for session cookie
        cookies = response.cookies
        session_cookie = cookies.get('session')
        
        if response.status_code == 200:
            print_result(True, "Login successful")
            try:
                user_data = response.json()
                print(f"   User data: {json.dumps(user_data, indent=2)}")
            except:
                print(f"   Response: {response.text[:200]}")
        else:
            print_result(False, f"Login failed with status {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return None, None
        
        # Check session cookie
        if session_cookie:
            print_result(True, f"Session cookie received: {session_cookie[:50]}...")
            
            # Check cookie attributes from Set-Cookie header
            set_cookie_header = response.headers.get('Set-Cookie', '')
            print(f"\n   Set-Cookie header: {set_cookie_header}")
            
            # Check for important attributes
            if 'Secure' in set_cookie_header:
                print_result(True, "Cookie has Secure flag")
            else:
                print_result(False, "Cookie missing Secure flag (required for HTTPS)")
            
            if 'HttpOnly' in set_cookie_header:
                print_result(True, "Cookie has HttpOnly flag")
            else:
                print_result(False, "Cookie missing HttpOnly flag")
            
            if 'SameSite=None' in set_cookie_header:
                print_result(True, "Cookie has SameSite=None (required for cross-origin)")
            else:
                print_result(False, "Cookie missing SameSite=None (needed for cross-origin)")
        else:
            print_result(False, "No session cookie received!")
            return None, None
        
        return session_cookie, cookies
    except Exception as e:
        print_result(False, f"Login request failed: {str(e)}")
        return None, None

def test_auth_me(backend_url, cookies):
    """Test /api/auth/me endpoint with session cookie"""
    print_section("Testing /api/auth/me Endpoint")
    
    if not cookies:
        print_result(False, "No cookies available to test")
        return False
    
    me_url = f"{backend_url}/api/auth/me"
    
    try:
        response = requests.get(
            me_url,
            cookies=cookies,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Request URL: {me_url}")
        print(f"Cookies sent: {dict(cookies)}")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print_result(True, "Authentication check passed")
            try:
                user_data = response.json()
                print(f"   User data: {json.dumps(user_data, indent=2)}")
                return True
            except:
                print(f"   Response: {response.text[:200]}")
                return True
        elif response.status_code == 401:
            print_result(False, "Authentication failed - 401 Unauthorized")
            print(f"   Error: {response.text[:200]}")
            print("\n   Possible causes:")
            print("   - Session cookie not being sent correctly")
            print("   - Session expired or invalid")
            print("   - SECRET_KEY changed, invalidating all sessions")
            print("   - Session storage issue (in-memory sessions lost)")
            return False
        else:
            print_result(False, f"Unexpected status code: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print_result(False, f"Request failed: {str(e)}")
        return False

def test_tickets_endpoint(backend_url, cookies):
    """Test /api/tickets endpoint"""
    print_section("Testing /api/tickets Endpoint")
    
    if not cookies:
        print_result(False, "No cookies available to test")
        return False
    
    tickets_url = f"{backend_url}/api/tickets"
    
    try:
        response = requests.get(
            tickets_url,
            cookies=cookies,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Request URL: {tickets_url}")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                tickets = response.json()
                ticket_count = len(tickets) if isinstance(tickets, list) else 0
                print_result(True, f"Tickets retrieved successfully - {ticket_count} tickets found")
                if ticket_count > 0:
                    print(f"\n   Sample ticket:")
                    print(f"   {json.dumps(tickets[0], indent=2)}")
                return True
            except Exception as e:
                print_result(False, f"Failed to parse tickets response: {str(e)}")
                print(f"   Response: {response.text[:200]}")
                return False
        elif response.status_code == 401:
            print_result(False, "Authentication failed - 401 Unauthorized")
            print(f"   Error: {response.text[:200]}")
            return False
        else:
            print_result(False, f"Unexpected status code: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print_result(False, f"Request failed: {str(e)}")
        return False

def discover_backend_url():
    """Try to discover backend URL from frontend"""
    print_section("Discovering Backend URL")
    
    # Try to fetch frontend and check for API calls or environment
    # For now, we'll need to check common Railway patterns
    # Backend might be on a different subdomain or port
    
    # Common patterns:
    # - Same domain, different path: https://fifa-tickets-frontendapp-production.up.railway.app/api
    # - Different subdomain: https://fifa-tickets-backend-production.up.railway.app
    # - Environment variable in Railway
    
    print("Note: Backend URL needs to be determined from Railway configuration.")
    print("Common patterns:")
    print("  - https://fifa-tickets-backend-production.up.railway.app")
    print("  - https://fifa-tickets-app-production.up.railway.app")
    print("  - Check Railway dashboard for backend service URL")
    
    return None

def main():
    print("="*80)
    print("  PRODUCTION DEBUGGING SCRIPT")
    print("="*80)
    
    # Get backend URL
    if len(sys.argv) > 1:
        backend_url = sys.argv[1].rstrip('/')
    else:
        backend_url = os.environ.get('BACKEND_URL')
        if not backend_url:
            print("\n❌ ERROR: Backend URL not provided")
            print("Usage: python debug_production.py <BACKEND_URL> [username] [password]")
            print("Example: python debug_production.py https://fifa-tickets-backend-production.up.railway.app admin admin123")
            sys.exit(1)
    
    # Get credentials
    username = sys.argv[2] if len(sys.argv) > 2 else "admin"
    password = sys.argv[3] if len(sys.argv) > 3 else "admin123"
    
    print(f"\nBackend URL: {backend_url}")
    print(f"Frontend URL: {FRONTEND_URL}")
    
    # Test health endpoints
    health_results = test_health_endpoints(backend_url)
    
    # Test login
    session_cookie, cookies = test_login(backend_url, username, password)
    
    if cookies:
        # Test authenticated endpoints
        auth_me_success = test_auth_me(backend_url, cookies)
        tickets_success = test_tickets_endpoint(backend_url, cookies)
        
        # Summary
        print_section("Summary")
        print(f"Health Check: {'✅' if health_results.get('/health') else '❌'}")
        print(f"Login: {'✅' if session_cookie else '❌'}")
        print(f"/api/auth/me: {'✅' if auth_me_success else '❌'}")
        print(f"/api/tickets: {'✅' if tickets_success else '❌'}")
        
        if not auth_me_success or not tickets_success:
            print("\n⚠️  ISSUES DETECTED:")
            if not auth_me_success:
                print("  - Session authentication failing after login")
                print("  - Likely causes: session storage, SECRET_KEY, or cookie issues")
            if not tickets_success:
                print("  - Cannot retrieve tickets data")
    else:
        print_section("Summary")
        print("❌ Cannot proceed with authenticated tests - login failed")

if __name__ == "__main__":
    import os
    main()

