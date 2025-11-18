# Railway Production Setup Guide

## Critical Configuration

### Backend Service Environment Variables

Set these in Railway backend service settings:

```
FLASK_ENV=production
SECRET_KEY=<generate-a-secure-random-key-and-keep-it-stable>
DATABASE_URL=<automatically-set-by-railway-if-using-railway-postgres>
FRONTEND_URL=https://fifa-tickets-frontendapp-production.up.railway.app
```

**IMPORTANT**: 
- `SECRET_KEY` must be set and **NEVER changed** once in production
- Changing SECRET_KEY will invalidate all existing sessions
- Generate a secure key: `python -c "import secrets; print(secrets.token_hex(32))"`

### Frontend Service Environment Variables

Set these in Railway frontend service settings:

**Build-time variables** (set in Railway build settings):
```
NEXT_PUBLIC_API_URL=https://<your-backend-railway-url>
```

**Example**:
```
NEXT_PUBLIC_API_URL=https://fifa-tickets-backend-production.up.railway.app
```

**CRITICAL**: 
- `NEXT_PUBLIC_API_URL` must be set **during build time**
- This is baked into the Next.js build
- If not set, frontend will try to connect to `http://localhost:8000` (will fail)
- You may need to set this as a build argument in Railway

### How to Set Build Arguments in Railway

1. Go to your frontend service in Railway
2. Click on "Settings"
3. Find "Build Command" or "Build Arguments"
4. Add: `NEXT_PUBLIC_API_URL=https://<your-backend-url>`
5. Or set it as an environment variable that's available during build

**Alternative**: If Railway doesn't support build-time env vars, you may need to:
- Use a custom Dockerfile that accepts build args
- Or set it in `next.config.ts` dynamically (not recommended for production)

## Database Setup

### Using Railway PostgreSQL

1. Create a PostgreSQL service in Railway
2. Railway automatically sets `DATABASE_URL` environment variable
3. Backend will automatically connect on startup

### Session Table

The sessions table is automatically created by Flask-Session on first startup.
No manual migration needed.

## Verification Checklist

After deployment, verify:

- [ ] Backend `/health` endpoint returns 200
- [ ] Backend `/health/detailed` shows database connected
- [ ] Frontend can reach backend (check browser console)
- [ ] Login works and sets session cookie
- [ ] `/api/auth/me` works after login
- [ ] `/api/tickets` returns data after login
- [ ] Sessions persist after server restart

## Testing Production

Use the provided debug script:
```bash
python backend/debug_production.py <BACKEND_URL> <username> <password>
```

Or test manually:
```bash
# 1. Login
curl -X POST https://<backend-url>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c cookies.txt

# 2. Check session
curl https://<backend-url>/api/debug/session -b cookies.txt

# 3. Get tickets
curl https://<backend-url>/api/tickets -b cookies.txt
```

## Troubleshooting

### Frontend shows "Network Error" or can't connect
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend URL is accessible
- Check CORS configuration in backend

### 401 Unauthorized after login
- Check backend logs for authentication failures
- Verify session cookie is being set (check browser DevTools)
- Test `/api/debug/session` endpoint
- Ensure SECRET_KEY hasn't changed

### Sessions not persisting
- Verify Flask-Session is installed (`flask-session>=0.5.0`)
- Check database connection
- Verify sessions table exists in database
- Check backend logs for session errors

