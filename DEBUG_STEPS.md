# Step-by-Step Production Debugging

## Step 1: Verify Backend is Running

Test the health endpoints:

```bash
# Replace <backend-url> with your actual Railway backend URL
curl https://<backend-url>/health
curl https://<backend-url>/health/detailed
```

**Expected**: Both should return 200 with database status.

## Step 2: Check if Sessions Table Exists

The sessions table should be created automatically. Check your PostgreSQL database:

```sql
SELECT * FROM sessions LIMIT 5;
```

If the table doesn't exist, Flask-Session might not have initialized properly.

## Step 3: Test Login and Session Creation

```bash
# Login
curl -X POST https://<backend-url>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -v \
  -c cookies.txt

# Check what cookie was set
cat cookies.txt
```

**Check for**:
- Status code 200
- `Set-Cookie` header with `session=...`
- Cookie has `Secure`, `HttpOnly`, `SameSite=None` flags

## Step 4: Test Session Debug Endpoint

```bash
# Check session state
curl https://<backend-url>/api/debug/session \
  -b cookies.txt \
  -v
```

**Expected**: Should show session keys including `user_id` and `username`.

## Step 5: Test Authenticated Endpoint

```bash
# Test /api/auth/me
curl https://<backend-url>/api/auth/me \
  -b cookies.txt \
  -v

# Test /api/tickets
curl https://<backend-url>/api/tickets \
  -b cookies.txt \
  -v
```

**If 401**:
- Cookie not being sent? Check cookie file
- Session not in database? Check sessions table
- SECRET_KEY changed? Check backend logs

## Step 6: Check Backend Logs in Railway

Look for:
1. **Login success messages**:
   ```
   ✅ Login successful for user <username> (ID: <id>)
   Session permanent: True
   User ID in session: <id>
   ```

2. **Authentication failures**:
   ```
   ❌ Authentication failed for /api/auth/me
   Session keys: []
   User ID in session: NOT FOUND
   ```

3. **Session errors**:
   - Flask-Session initialization errors
   - Database connection errors
   - Table creation errors

## Step 7: Verify Environment Variables

In Railway backend service, verify:
- `FLASK_ENV=production` ✅
- `SECRET_KEY=<stable-key>` ✅ (must be set and stable)
- `DATABASE_URL` ✅ (auto-set by Railway)

## Step 8: Check Frontend Configuration

In browser DevTools:
1. **Network tab**: Check API requests
   - Are requests going to correct backend URL?
   - Check request headers for `Cookie` header
   - Check response headers for `Set-Cookie`

2. **Application tab → Cookies**:
   - Is session cookie present?
   - Cookie attributes: Secure, HttpOnly, SameSite
   - Cookie domain and path

3. **Console tab**:
   - Any JavaScript errors?
   - CORS errors?
   - Network errors?

## Step 9: Test with Debug Script

Use the provided debug script:

```bash
python backend/debug_production.py <BACKEND_URL> admin admin123
```

This will test the entire authentication flow and report issues.

## Common Issues and Solutions

### Issue: Sessions table doesn't exist
**Solution**: Flask-Session might not have initialized. Check backend logs for errors. Manually create table if needed.

### Issue: Cookie not being set
**Check**:
- CORS configuration allows credentials
- Frontend URL is in CORS origins
- Cookie SameSite=None requires Secure=True (HTTPS)

### Issue: Cookie set but not sent
**Check**:
- Frontend axios has `withCredentials: true` ✅ (already set)
- Backend CORS has `supports_credentials=True` ✅ (already set)
- Cookie domain/path matches

### Issue: Session exists but auth fails
**Check**:
- SECRET_KEY hasn't changed
- Session in database matches cookie
- Session hasn't expired

### Issue: Frontend can't reach backend
**Check**:
- `NEXT_PUBLIC_API_URL` is set correctly
- Backend URL is accessible
- CORS allows frontend origin

