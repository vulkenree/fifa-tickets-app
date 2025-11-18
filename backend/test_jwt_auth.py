#!/usr/bin/env python3
"""Test script for JWT authentication flow"""
import requests
import json
import sys
import time

API_BASE_URL = 'http://localhost:8000'

def test_jwt_auth():
    """Test JWT authentication flow"""
    print("=" * 60)
    print("Testing JWT Authentication Flow")
    print("=" * 60)
    
    # Use unique username with timestamp
    unique_username = f'testuser_jwt_{int(time.time())}'
    
    # Test 1: Register a new user
    print("\n1. Testing user registration...")
    register_data = {
        'username': unique_username,
        'password': 'testpass123'
    }
    try:
        response = requests.post(f'{API_BASE_URL}/api/auth/register', json=register_data)
        if response.status_code == 201:
            data = response.json()
            token = data.get('token')
            user = data.get('user')
            print(f"   ✅ Registration successful")
            if user:
                print(f"   User ID: {user.get('id')}")
                print(f"   Username: {user.get('username')}")
            print(f"   Token received: {bool(token)}")
            if token:
                print(f"   Token preview: {token[:50]}...")
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    # Test 2: Login with credentials
    print("\n2. Testing login...")
    login_data = {
        'username': unique_username,
        'password': 'testpass123'
    }
    try:
        response = requests.post(f'{API_BASE_URL}/api/auth/login', json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user = data.get('user')
            print(f"   ✅ Login successful")
            print(f"   User ID: {user.get('id')}")
            print(f"   Username: {user.get('username')}")
            print(f"   Token received: {bool(token)}")
            if token:
                print(f"   Token preview: {token[:50]}...")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Test 3: Access protected endpoint with token
    print("\n3. Testing protected endpoint access...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(f'{API_BASE_URL}/api/auth/me', headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Protected endpoint access successful")
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Username: {user_data.get('username')}")
        else:
            print(f"   ❌ Protected endpoint access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Protected endpoint error: {e}")
        return False
    
    # Test 4: Access protected endpoint without token
    print("\n4. Testing protected endpoint without token...")
    try:
        response = requests.get(f'{API_BASE_URL}/api/auth/me')
        if response.status_code == 401:
            print(f"   ✅ Correctly rejected request without token")
        else:
            print(f"   ❌ Should have returned 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 5: Access protected endpoint with invalid token
    print("\n5. Testing protected endpoint with invalid token...")
    invalid_headers = {
        'Authorization': 'Bearer invalid_token_12345',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(f'{API_BASE_URL}/api/auth/me', headers=invalid_headers)
        if response.status_code == 401:
            print(f"   ✅ Correctly rejected request with invalid token")
        else:
            print(f"   ❌ Should have returned 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 6: Access profile endpoint
    print("\n6. Testing profile endpoint...")
    try:
        response = requests.get(f'{API_BASE_URL}/api/profile', headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
            print(f"   ✅ Profile endpoint access successful")
            print(f"   Username: {profile_data.get('username')}")
        else:
            print(f"   ❌ Profile endpoint access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Profile endpoint error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All JWT authentication tests passed!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_jwt_auth()
    sys.exit(0 if success else 1)

