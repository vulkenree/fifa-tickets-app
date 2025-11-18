# Where Cookie Settings Are Configured in the Code

## Overview

Cookie attributes (Secure, SameSite, HttpOnly) are set in **two places** in the code:

1. **Configuration** (lines 100-106) - Sets Flask-Session config
2. **Enforcement** (lines 50-78) - `after_request` hook ensures attributes are present

---

## Location 1: Flask-Session Configuration

**File**: `backend/app.py`  
**Lines**: 100-106

```python
# Flask-Session cookie configuration (must be set before Session initialization)
# These settings ensure cookies work with cross-origin requests in production
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True  # Required for HTTPS
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Required for cross-origin
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Let browser set domain automatically
```

**What this does:**
- Tells Flask-Session what cookie attributes to use
- Only applies in production (`FLASK_ENV=production`)
- Sets the configuration before Flask-Session is initialized

**Verification:**
- Check backend startup logs for:
  ```
  ✅ Flask-Session initialized with SQLAlchemy backend
     Cookie Secure: True
     Cookie SameSite: None
     Cookie HttpOnly: True
  ```

---

## Location 2: Cookie Enforcement (after_request hook)

**File**: `backend/app.py`  
**Lines**: 42-80 (specifically 50-78 for cookie handling)

```python
@app.after_request
def after_request(response):
    # ... security headers ...
    
    if os.environ.get('FLASK_ENV') == 'production':
        # Ensure session cookie has correct attributes for cross-origin requests
        # Flask-Session might not always respect config, so we enforce it here
        set_cookie_headers = response.headers.getlist('Set-Cookie')
        if set_cookie_headers:
            updated_cookies = []
            for cookie in set_cookie_headers:
                # Check if it's a session cookie
                if 'session=' in cookie or 'fifa_tickets:session:' in cookie:
                    # Ensure Secure and SameSite=None are present
                    if 'Secure' not in cookie:
                        cookie = cookie + '; Secure'
                    
                    # Ensure SameSite=None is present
                    if 'SameSite=None' not in cookie and 'SameSite=' not in cookie:
                        cookie = cookie + '; SameSite=None'
                    
                updated_cookies.append(cookie)
            
            # Replace all Set-Cookie headers
            response.headers.poplist('Set-Cookie')
            for cookie in updated_cookies:
                response.headers.add('Set-Cookie', cookie)
    
    return response
```

**What this does:**
- Runs **after every response** (including login)
- Checks if `Set-Cookie` header exists
- If it's a session cookie, ensures `Secure` and `SameSite=None` are present
- **Overwrites** the cookie header with corrected attributes
- This is a **safety net** in case Flask-Session doesn't respect the config

**When it runs:**
- After login response (when cookie is set)
- After any response that sets a session cookie

**Verification:**
- Check backend logs after login for:
  ```
  🍪 Cookie attributes modified:
     Original: session=...; HttpOnly; Path=/
     Updated:  session=...; HttpOnly; Secure; SameSite=None; Path=/
     Has Secure: True
     Has SameSite=None: True
     Has HttpOnly: True
  ```

---

## Location 3: Login Endpoint (Where Cookie is Created)

**File**: `backend/app.py`  
**Lines**: 228-259

```python
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    # ... validation ...
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = True  # Make session persistent
        
        return jsonify({
            'id': user.id,
            'username': user.username
        })
```

**What this does:**
- Creates the session (which triggers Flask-Session to set cookie)
- The cookie is set by Flask-Session automatically
- The `after_request` hook then modifies it to ensure correct attributes

**Flow:**
1. Login endpoint creates session → Flask-Session sets cookie → `after_request` modifies cookie → Response sent

---

## How to Verify Cookie Attributes Are Set

### Method 1: Check Backend Logs

After login, look for these log messages:

**On startup:**
```
✅ Flask-Session initialized with SQLAlchemy backend
   Cookie Secure: True
   Cookie SameSite: None
   Cookie HttpOnly: True
```

**After login (if cookie was modified):**
```
🍪 Cookie attributes modified:
   Original: session=...; HttpOnly; Path=/
   Updated:  session=...; HttpOnly; Secure; SameSite=None; Path=/
   Has Secure: True
   Has SameSite=None: True
   Has HttpOnly: True
```

### Method 2: Add Debug Logging to after_request

You can add this to see the final cookie:

```python
@app.after_request
def after_request(response):
    # ... existing code ...
    
    if os.environ.get('FLASK_ENV') == 'production':
        # ... cookie modification code ...
        
        # Log final cookie (for debugging)
        final_cookies = response.headers.getlist('Set-Cookie')
        for cookie in final_cookies:
            if 'session=' in cookie:
                print(f"🔍 Final Set-Cookie header: {cookie[:150]}...")
                print(f"   Contains Secure: {'Secure' in cookie}")
                print(f"   Contains SameSite=None: {'SameSite=None' in cookie}")
                print(f"   Contains HttpOnly: {'HttpOnly' in cookie}")
    
    return response
```

### Method 3: Test with curl

```bash
curl -X POST https://<backend-url>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -v 2>&1 | grep -i "set-cookie"
```

Look for `Secure` and `SameSite=None` in the output.

---

## Summary

**Cookie settings are configured in 3 places:**

1. **Lines 100-106**: Flask-Session configuration (tells Flask-Session what to use)
2. **Lines 50-78**: `after_request` hook (enforces attributes are present)
3. **Lines 241-243**: Login endpoint (creates session, which triggers cookie)

**The `after_request` hook is the safety net** - it ensures that even if Flask-Session doesn't respect the config, the cookie will have the correct attributes before being sent to the client.

**To verify it's working:**
- Check backend logs for cookie modification messages
- Use the `check_cookie_attributes.sh` script
- Check browser DevTools → Application → Cookies

