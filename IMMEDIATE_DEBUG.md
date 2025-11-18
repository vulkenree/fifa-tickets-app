# Immediate Debugging Steps

## Quick Test Script

Run this to quickly diagnose the issue:

```bash
python backend/quick_debug.py <YOUR_BACKEND_URL> admin admin123
```

Replace `<YOUR_BACKEND_URL>` with your actual Railway backend URL.

## What to Check First

### 1. Check Railway Backend Logs

In Railway dashboard → Backend service → Logs, look for:

**Good signs:**
```
✅ Using PostgreSQL database
✅ Flask-Session initialized with SQLAlchemy backend
✅ Sessions table exists in database
✅ Login successful for user admin (ID: X)
```

**Bad signs:**
```
❌ ERROR: Flask-Session initialization failed
⚠️  Warning: Sessions table not found
❌ Authentication failed for /api/auth/me
```

### 2. Verify Environment Variables

In Railway → Backend service → Variables, check:
- `FLASK_ENV=production` ✅
- `SECRET_KEY=<some-value>` ✅ (MUST be set)
- `DATABASE_URL` ✅ (auto-set by Railway)

### 3. Check if Sessions Table Exists

If you have database access, run:
```sql
SELECT * FROM sessions LIMIT 5;
```

If the table doesn't exist, that's the problem.

### 4. Test in Browser DevTools

1. Open production frontend
2. Open DevTools (F12)
3. Go to Network tab
4. Try to login
5. Check:
   - Login request returns 200?
   - Response has `Set-Cookie` header?
   - Cookie has `Secure`, `HttpOnly`, `SameSite=None`?
   - Next request (to /api/auth/me) includes Cookie header?

### 5. Common Issues

#### Issue: "Sessions table not found"
**Fix**: Flask-Session might not have created it. The table should be created automatically, but if not:
- Check backend logs for Flask-Session errors
- Verify database connection is working
- Restart backend service

#### Issue: Cookie not being set
**Check**:
- Backend logs show "Login successful"?
- Response headers include Set-Cookie?
- CORS configuration allows credentials?

#### Issue: Cookie set but not sent
**Check**:
- Browser DevTools → Application → Cookies shows session cookie?
- Network tab shows Cookie header in subsequent requests?
- Cookie domain/path is correct?

#### Issue: 401 after login
**Most likely causes**:
1. Sessions table doesn't exist
2. SECRET_KEY changed
3. Cookie not being sent from frontend
4. Flask-Session not working properly

## Next Steps Based on Results

### If quick_debug.py shows "NO SESSION COOKIE RECEIVED"
→ Problem: Backend not setting cookie
→ Check: Backend logs, CORS config, cookie settings

### If quick_debug.py shows cookie but "401 UNAUTHORIZED"
→ Problem: Session not being read
→ Check: Sessions table exists, SECRET_KEY stable, Flask-Session working

### If sessions table doesn't exist
→ Problem: Flask-Session not initialized
→ Fix: Check backend logs for errors, verify flask-session is installed

## Get Backend URL

If you don't know your backend URL:
1. Go to Railway dashboard
2. Click on your backend service
3. Look for the "Domains" or "Settings" section
4. The URL should be something like: `https://fifa-tickets-backend-production.up.railway.app`

## Share Results

After running the diagnostic, share:
1. Output from `quick_debug.py`
2. Relevant backend logs (especially errors)
3. Whether sessions table exists
4. Environment variables (without showing SECRET_KEY value)

