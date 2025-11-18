# Profile 401 Error Debugging Guide

## Problem
After logging in successfully, accessing the profile page returns:
```json
{"error": "Authentication required"}
```

This is a 401 Unauthorized error, meaning the session cookie is not being recognized.

## Root Cause Analysis

The `/api/profile` endpoint is protected by `@login_required`:
```python
@app.route('/api/profile', methods=['GET'])
@login_required  # <-- Checks if session['user_id'] exists
def get_profile():
    ...
```

If `session['user_id']` is missing, it returns 401.

## Possible Causes

### 1. Cookie Not Being Sent (Most Likely)
**Symptoms**: Cookie exists but not sent with request
**Check**:
- Browser DevTools → Network tab → Profile request
- Look for `Cookie:` header in request headers
- If missing → CORS or cookie configuration issue

### 2. Cookie Not Being Set Correctly
**Symptoms**: No cookie after login
**Check**:
- Browser DevTools → Application → Cookies
- Look for `session` cookie
- Check cookie attributes: Secure, HttpOnly, SameSite

### 3. Session Not in Database
**Symptoms**: Cookie exists but session not found
**Check**:
- Backend logs for session errors
- Database `sessions` table
- Flask-Session initialization errors

### 4. Cookie Domain/Path Mismatch
**Symptoms**: Cookie set but not sent to correct domain
**Check**:
- Cookie domain matches backend domain
- Cookie path is `/` (should be)

### 5. Frontend API URL Wrong
**Symptoms**: Frontend calling wrong backend
**Check**:
- `NEXT_PUBLIC_API_URL` environment variable
- Network tab shows correct backend URL

## Debugging Steps

### Step 1: Check Browser DevTools

1. **Open DevTools** (F12)
2. **Go to Application tab → Cookies**
3. **Check for `session` cookie**:
   - Does it exist?
   - Domain: Should match backend domain
   - Path: Should be `/`
   - Secure: Should be checked (production)
   - HttpOnly: Should be checked
   - SameSite: Should be `None` (production)

4. **Go to Network tab**
5. **Navigate to profile page**
6. **Find the `/api/profile` request**
7. **Check Request Headers**:
   - Is there a `Cookie:` header?
   - Does it contain `session=...`?
   - If missing → cookie not being sent

### Step 2: Check Backend Logs

In Railway backend logs, look for:
```
❌ Authentication failed for /api/profile
   Session keys: []
   User ID in session: NOT FOUND
   Cookies received: []
```

This tells you:
- If session exists
- If cookies are being received
- What's in the session

### Step 3: Test with curl

```bash
# 1. Login and save cookie
curl -X POST https://<backend-url>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c cookies.txt \
  -v

# 2. Check cookie file
cat cookies.txt

# 3. Test profile endpoint
curl https://<backend-url>/api/profile \
  -b cookies.txt \
  -v
```

**Expected**: Should return user profile
**If 401**: Cookie not working, check cookie attributes

### Step 4: Check CORS Configuration

Verify backend CORS allows frontend origin:
```python
CORS(app, 
     origins=[
         'https://fifa-tickets-frontendapp-production.up.railway.app',
     ],
     supports_credentials=True,  # <-- Critical
     ...
)
```

### Step 5: Verify Cookie Attributes

The cookie MUST have:
- `Secure` (production) - Required for HTTPS
- `SameSite=None` (production) - Required for cross-origin
- `HttpOnly` - Security

Check if our cookie fix is deployed:
- Look at `Set-Cookie` header in login response
- Should see: `Secure; SameSite=None; HttpOnly`

## Quick Fixes

### Fix 1: Verify Cookie is Being Set

Check login response headers:
```bash
curl -X POST https://<backend-url>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -v 2>&1 | grep -i "set-cookie"
```

Should see:
```
Set-Cookie: session=...; HttpOnly; Secure; SameSite=None; Path=/
```

### Fix 2: Check Frontend API URL

Verify `NEXT_PUBLIC_API_URL` is set correctly:
- In Railway frontend service
- Should be: `https://<your-backend-url>`
- Must be set at build time

### Fix 3: Check Session Storage

Verify sessions table exists and has data:
```sql
SELECT * FROM sessions LIMIT 5;
```

If empty → Flask-Session not working

## Most Likely Issue

Based on the symptoms, the most likely issue is:

**Cookie not being sent with the profile request**

This could be because:
1. Cookie attributes not set correctly (Secure/SameSite)
2. CORS not configured properly
3. Frontend not sending cookies (but `withCredentials: true` is set)

## Solution Checklist

- [ ] Verify cookie is set after login (DevTools → Application → Cookies)
- [ ] Verify cookie is sent with profile request (DevTools → Network → Headers)
- [ ] Check backend logs for authentication failure details
- [ ] Verify `NEXT_PUBLIC_API_URL` is correct
- [ ] Verify CORS allows frontend origin
- [ ] Verify cookie has Secure and SameSite=None (production)
- [ ] Test with curl to isolate frontend vs backend issue

