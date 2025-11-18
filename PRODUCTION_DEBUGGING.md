# Production Debugging Guide

## Issues Fixed

### 1. Session Configuration Issues ✅
- **Fixed**: Added `session.permanent = True` to login endpoint (was missing, only in register)
- **Fixed**: Added explicit `PERMANENT_SESSION_LIFETIME` configuration (31 days)
- **Added**: Debug logging for authentication failures in production

### 2. Session Storage - FIXED ✅
- **Fixed**: Implemented Flask-Session with SQLAlchemy backend
- Sessions are now stored in PostgreSQL database
- Sessions persist across server restarts
- Sessions are shared between multiple backend instances (if using same database)
- Added `flask-session>=0.5.0` to requirements.txt

## Production Configuration Requirements

### Backend Environment Variables
- `FLASK_ENV=production` - Must be set for production
- `SECRET_KEY` - Must be set and stable (do not change between deployments)
- `DATABASE_URL` - PostgreSQL connection string
- `FRONTEND_URL` - Frontend URL for CORS (optional, defaults to Railway URL)

### Frontend Environment Variables
- `NEXT_PUBLIC_API_URL` - **CRITICAL**: Must be set to backend URL during build
  - Example: `https://fifa-tickets-backend-production.up.railway.app`
  - This is a build-time variable, must be set in Railway build settings

## Testing Production

### 1. Test Health Endpoints
```bash
curl https://<backend-url>/health
curl https://<backend-url>/health/detailed
```

### 2. Test Authentication Flow
Use the provided `debug_production.py` script:
```bash
python backend/debug_production.py <BACKEND_URL> <username> <password>
```

### 3. Test Session Debug Endpoint
```bash
curl https://<backend-url>/api/debug/session
```

### 4. Check Backend Logs
Look for:
- Login success messages
- Authentication failure messages with session details
- Database connection errors

## Common Issues

### Issue: 401 Unauthorized After Login
**Symptoms**: Login succeeds but immediate API calls fail with 401

**Possible Causes**:
1. **Session storage**: In-memory sessions lost (most likely)
2. **SECRET_KEY changed**: All sessions invalidated
3. **Cookie not sent**: CORS or cookie configuration issue
4. **Frontend API URL wrong**: Frontend calling wrong backend URL

**Debug Steps**:
1. Check `/api/debug/session` endpoint after login
2. Check backend logs for authentication failures
3. Verify `NEXT_PUBLIC_API_URL` is set correctly
4. Check browser DevTools → Network → Cookies tab

### Issue: No Tickets Showing
**Symptoms**: Database has data but frontend shows empty

**Possible Causes**:
1. Authentication failing (see above)
2. Frontend API URL pointing to wrong backend
3. CORS blocking requests
4. Database connection issues

**Debug Steps**:
1. Test `/api/tickets` endpoint directly with session cookie
2. Check browser console for errors
3. Verify database connectivity with `/health/detailed`

## Next Steps for Production Stability

1. **Implement Persistent Session Storage** (High Priority)
   - Add Flask-Session to requirements.txt
   - Configure database-backed sessions
   - This will solve the session loss issue

2. **Verify Environment Variables**
   - Ensure SECRET_KEY is stable
   - Verify NEXT_PUBLIC_API_URL is set during build
   - Check DATABASE_URL is correct

3. **Monitor Logs**
   - Watch for authentication failures
   - Monitor session creation/deletion
   - Check database connection errors

## Debug Endpoints

- `/health` - Basic health check
- `/health/detailed` - Detailed health with database status
- `/api/debug/session` - Session state information (for debugging)

