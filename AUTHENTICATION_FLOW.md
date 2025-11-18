# End-to-End Authentication Flow Documentation

## Overview

This application uses **server-side sessions** with **HTTP-only cookies** for authentication. The backend uses Flask sessions stored in PostgreSQL, and the frontend (Next.js) automatically sends cookies with each request.

## Architecture

### Backend: Flask Server-Side Sessions
- **Storage**: PostgreSQL database (via Flask-Session)
- **Session Type**: Server-side (session data stored on server, only session ID in cookie)
- **Cookie**: HTTP-only, Secure (in production), SameSite=None (for cross-origin)
- **Persistence**: Sessions persist across server restarts (stored in database)

### Frontend: Next.js with Axios
- **HTTP Client**: Axios with `withCredentials: true` (sends cookies automatically)
- **State Management**: SWR for user state, React hooks for auth actions
- **Cookie Handling**: Browser automatically manages cookies (HTTP-only, so JavaScript can't access)

---

## Complete Authentication Flow

### 1. User Login Flow

```
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│   Browser   │                    │   Frontend  │                    │   Backend   │
│  (Next.js)  │                    │   (React)   │                    │   (Flask)   │
└──────┬──────┘                    └──────┬──────┘                    └──────┬──────┘
       │                                    │                                    │
       │  1. User enters credentials        │                                    │
       │───────────────────────────────────>│                                    │
       │                                    │                                    │
       │                                    │  2. POST /api/auth/login           │
       │                                    │     {username, password}            │
       │                                    │───────────────────────────────────>│
       │                                    │                                    │
       │                                    │  3. Verify credentials              │
       │                                    │     - Query User from DB           │
       │                                    │     - Check password hash           │
       │                                    │                                    │
       │                                    │  4. Create session                 │
       │                                    │     session['user_id'] = user.id    │
       │                                    │     session['username'] = username  │
       │                                    │     session.permanent = True        │
       │                                    │                                    │
       │                                    │  5. Store session in PostgreSQL    │
       │                                    │     (Flask-Session)                 │
       │                                    │                                    │
       │                                    │  6. Set session cookie             │
       │                                    │     Set-Cookie: session=...         │
       │                                    │     HttpOnly; Secure; SameSite=None│
       │                                    │<───────────────────────────────────│
       │                                    │                                    │
       │  7. Browser stores cookie          │                                    │
       │     (automatic, HTTP-only)         │                                    │
       │<───────────────────────────────────│                                    │
       │                                    │                                    │
       │  8. Update UI state                │                                    │
       │     - Store user in SWR cache      │                                    │
       │     - Redirect to /dashboard       │                                    │
       │                                    │                                    │
```

#### Step-by-Step Login Process

**Frontend (`frontend/app/login/page.tsx`):**
1. User submits login form
2. Calls `useAuth().login(credentials)`

**Frontend Hook (`frontend/hooks/use-auth.ts`):**
3. Calls `authApi.login(credentials)`
4. Axios sends POST to `/api/auth/login` with `withCredentials: true`

**Backend (`backend/app.py` - `/api/auth/login`):**
5. Receives JSON: `{"username": "...", "password": "..."}`
6. Queries database for user: `User.query.filter_by(username=username).first()`
7. Verifies password: `user.check_password(password)`
8. **Creates session**:
   ```python
   session['user_id'] = user.id
   session['username'] = user.username
   session.permanent = True  # Persist across browser restarts
   ```
9. Flask-Session stores session data in PostgreSQL `sessions` table
10. Flask sets HTTP-only cookie with session ID
11. Returns JSON: `{"id": 1, "username": "admin"}`

**Frontend:**
12. Browser automatically stores cookie (HTTP-only, can't be accessed by JavaScript)
13. `useAuth` hook updates SWR cache with user data
14. Redirects to `/dashboard`

---

### 2. Authenticated Request Flow

```
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│   Browser   │                    │   Frontend  │                    │   Backend   │
│  (Next.js)  │                    │   (React)   │                    │   (Flask)   │
└──────┬──────┘                    └──────┬──────┘                    └──────┬──────┘
       │                                    │                                    │
       │  1. Component needs user data      │                                    │
       │     useAuth() hook                 │                                    │
       │                                    │                                    │
       │                                    │  2. GET /api/auth/me               │
       │                                    │     Cookie: session=...             │
       │                                    │───────────────────────────────────>│
       │                                    │                                    │
       │                                    │  3. @login_required decorator      │
       │                                    │     - Checks session['user_id']     │
       │                                    │     - If missing → 401              │
       │                                    │                                    │
       │                                    │  4. Load user from database         │
       │                                    │     User.query.get(session['user_id'])│
       │                                    │                                    │
       │                                    │  5. Return user data               │
       │                                    │     {id, username}                 │
       │                                    │<───────────────────────────────────│
       │                                    │                                    │
       │  6. Update UI with user data       │                                    │
       │                                    │                                    │
```

#### Example: Getting Current User

**Frontend (`frontend/hooks/use-auth.ts`):**
```typescript
const { data: user } = useSWR('/api/auth/me', 
  () => authApi.me().then(res => res.data)
);
```

**What happens:**
1. SWR calls `authApi.me()` which sends GET to `/api/auth/me`
2. Axios automatically includes cookie: `Cookie: session=eyJ1c2VyX2lkIjox...`
3. Backend receives request with cookie
4. Flask extracts session ID from cookie
5. Flask-Session loads session data from PostgreSQL
6. `@login_required` decorator checks `session['user_id']`
7. If present, returns user data; if missing, returns 401

---

### 3. Protected Route Flow

```
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│   Browser   │                    │   Frontend  │                    │   Backend   │
│  (Next.js)  │                    │   (React)   │                    │   (Flask)   │
└──────┬──────┘                    └──────┬──────┘                    └──────┬──────┘
       │                                    │                                    │
       │  1. User navigates to /dashboard  │                                    │
       │                                    │                                    │
       │                                    │  2. GET /api/tickets               │
       │                                    │     Cookie: session=...            │
       │                                    │───────────────────────────────────>│
       │                                    │                                    │
       │                                    │  3. @login_required decorator      │
       │                                    │     def login_required(f):         │
       │                                    │       if 'user_id' not in session: │
       │                                    │         return 401                  │
       │                                    │                                    │
       │                                    │  4. If authenticated:              │
       │                                    │     - Execute route handler        │
       │                                    │     - Query tickets from DB         │
       │                                    │     - Return JSON data             │
       │                                    │<───────────────────────────────────│
       │                                    │                                    │
       │  5. Display tickets in UI         │                                    │
       │                                    │                                    │
```

#### Backend Protection (`backend/app.py`):

```python
def login_required(f):
    """Decorator to require login for protected routes"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Check if this is an API route
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            else:
                return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/tickets', methods=['GET'])
@login_required  # <-- Protects this route
def get_tickets():
    """Get all tickets (all users can see all tickets)"""
    tickets = Ticket.query.order_by(Ticket.date.desc()).all()
    return jsonify([ticket.to_dict() for ticket in tickets])
```

**How it works:**
1. Request comes in with cookie
2. Flask-Session loads session from database using cookie
3. `@login_required` checks if `session['user_id']` exists
4. If yes → execute route handler
5. If no → return 401 Unauthorized

---

## Key Components

### Backend Session Management

**Session Storage (`backend/app.py`):**
```python
# Configure Flask-Session to use PostgreSQL
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True

Session(app)  # Initialize Flask-Session
```

**What this means:**
- Sessions stored in PostgreSQL `sessions` table
- Session data encrypted and signed
- Sessions persist across server restarts
- Multiple backend instances can share sessions (same database)

**Session Cookie Configuration:**
```python
# Production: Secure, SameSite=None (for cross-origin)
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Cross-origin allowed
app.config['SESSION_COOKIE_HTTPONLY'] = True  # JavaScript can't access
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
```

### Frontend Cookie Handling

**Axios Configuration (`frontend/lib/api.ts`):**
```typescript
export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // <-- Critical: sends cookies with requests
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**What `withCredentials: true` does:**
- Tells browser to include cookies in cross-origin requests
- Required for CORS with credentials
- Browser automatically sends `Cookie: session=...` header

**User State Management (`frontend/hooks/use-auth.ts`):**
```typescript
// SWR automatically fetches /api/auth/me on mount
const { data: user, error, mutate } = useSWR('/api/auth/me', 
  () => authApi.me().then(res => res.data)
);
```

**How it works:**
- SWR calls `/api/auth/me` when component mounts
- If cookie is valid → returns user data → `user` is set
- If cookie is invalid → 401 error → `error` is set
- Components can check `user` to determine if logged in

---

## Security Features

### 1. HTTP-Only Cookies
- **Why**: Prevents XSS attacks (JavaScript can't access cookie)
- **Implementation**: `SESSION_COOKIE_HTTPONLY = True`
- **Result**: Cookie only accessible to browser, not JavaScript

### 2. Secure Cookies (Production)
- **Why**: Prevents cookie theft over unencrypted connections
- **Implementation**: `SESSION_COOKIE_SECURE = True` (production only)
- **Result**: Cookie only sent over HTTPS

### 3. SameSite=None (Production)
- **Why**: Allows cross-origin requests (frontend and backend on different domains)
- **Implementation**: `SESSION_COOKIE_SAMESITE = 'None'` (production only)
- **Note**: Requires `Secure=True` (browser requirement)

### 4. Signed Sessions
- **Why**: Prevents tampering with session data
- **Implementation**: `SESSION_USE_SIGNER = True`
- **Result**: Session data is cryptographically signed

### 5. Server-Side Session Storage
- **Why**: Session data not exposed to client
- **Implementation**: Flask-Session with PostgreSQL
- **Result**: Only session ID in cookie, actual data on server

---

## Session Lifecycle

### Session Creation
1. User logs in → Backend creates session
2. Session data stored in PostgreSQL: `{user_id: 1, username: "admin"}`
3. Session ID encrypted and signed
4. Cookie set: `session=<encrypted_session_id>`
5. Cookie expires in 31 days (or when browser closes in dev)

### Session Usage
1. Frontend makes request → Browser sends cookie automatically
2. Backend receives cookie → Extracts session ID
3. Flask-Session loads session from database
4. Route handler accesses `session['user_id']`
5. Request processed with user context

### Session Expiration
- **Time-based**: 31 days (if `session.permanent = True`)
- **Browser-based**: When browser closes (if not permanent, dev mode)
- **Manual**: When user logs out (`session.clear()`)

### Session Invalidation
- User logs out → `session.clear()` → Session deleted from database
- Server restart → Session persists (stored in database)
- SECRET_KEY changes → All sessions invalidated (can't decrypt)

---

## CORS Configuration

**Backend (`backend/app.py`):**
```python
CORS(app, 
     origins=[
         'http://localhost:3000',  # Local dev
         'https://fifa-tickets-frontendapp-production.up.railway.app',  # Production
     ],
     supports_credentials=True,  # <-- Critical: allows cookies
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
)
```

**Why `supports_credentials=True`:**
- Allows cookies to be sent in cross-origin requests
- Required for session cookies to work
- Must match frontend `withCredentials: true`

---

## Common Scenarios

### Scenario 1: User Logs In
1. Frontend: `POST /api/auth/login` with credentials
2. Backend: Validates, creates session, sets cookie
3. Frontend: Receives user data, updates state, redirects
4. Browser: Stores cookie automatically

### Scenario 2: User Accesses Protected Route
1. Frontend: `GET /api/tickets` (with cookie)
2. Backend: `@login_required` checks session
3. Backend: If valid → returns data; if invalid → 401
4. Frontend: If 401 → redirects to login

### Scenario 3: User Logs Out
1. Frontend: `POST /api/auth/logout` (with cookie)
2. Backend: `session.clear()` → Deletes session from database
3. Backend: Cookie expires (or cleared)
4. Frontend: Clears user state, redirects to login

### Scenario 4: Session Expired
1. Frontend: Makes request with expired cookie
2. Backend: Can't find session in database
3. Backend: Returns 401 Unauthorized
4. Frontend: `useAuth` hook detects error, redirects to login

---

## Advantages of This Approach

1. **Security**: HTTP-only cookies prevent XSS attacks
2. **Persistence**: Sessions survive server restarts (database storage)
3. **Scalability**: Multiple backend instances share sessions
4. **Simplicity**: No token management on frontend
5. **Automatic**: Browser handles cookie sending/receiving

## Disadvantages

1. **CSRF Risk**: Requires CSRF protection (not currently implemented)
2. **Cookie Size**: Limited to 4KB (but only session ID stored)
3. **CORS Complexity**: Requires careful CORS configuration
4. **Database Dependency**: Sessions require database connection

---

## Summary

**Authentication Type**: Server-side sessions with HTTP-only cookies

**Flow**:
1. Login → Backend creates session → Cookie set
2. Requests → Browser sends cookie → Backend validates session
3. Logout → Backend clears session → Cookie removed

**Key Points**:
- Session data stored on server (PostgreSQL)
- Only session ID in cookie (encrypted and signed)
- Frontend never sees session data (HTTP-only)
- Browser automatically manages cookies
- Sessions persist across server restarts

This is a secure, scalable authentication mechanism suitable for production use.

