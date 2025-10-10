# FIFA 2026 Tickets App

Monorepo for FIFA 2026 ticket management application.

## Structure
- `frontend/` - Next.js + React + TypeScript frontend
- `backend/` - Flask + SQLAlchemy backend

## Local Development

### Backend (Flask)
```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
python app.py
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:3000 (frontend) and http://localhost:5001 (backend)

## Production Deployment (Railway)

Both services deploy from GitHub:
- Backend: Root directory = `/backend`
- Frontend: Root directory = `/frontend`

See deployment documentation below.

## Features

- **Authentication**: User registration and login
- **Ticket Management**: Create, read, update, delete FIFA 2026 tickets
- **Match Lookup**: Auto-populate date and venue from match number
- **Filtering & Search**: Filter tickets by user, venue, category, date
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: SWR for data fetching and caching

## Tech Stack

### Frontend
- Next.js 14 with App Router
- React 19 with TypeScript
- Tailwind CSS + shadcn/ui components
- SWR for data fetching
- React Hook Form with Zod validation

### Backend
- Flask 3.1+ with SQLAlchemy
- PostgreSQL (production) / SQLite (development)
- Flask-CORS for cross-origin requests
- Session-based authentication
- RESTful API design

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Tickets
- `GET /api/tickets` - Get all tickets
- `POST /api/tickets` - Create ticket
- `PUT /api/tickets/:id` - Update ticket
- `DELETE /api/tickets/:id` - Delete ticket

### Matches
- `GET /api/matches` - Get FIFA 2026 match schedule
- `GET /api/matches/:number` - Get specific match details

## Environment Variables

### Backend
- `SECRET_KEY` - Flask secret key for sessions
- `DATABASE_URL` - PostgreSQL connection string
- `FLASK_ENV` - Environment (development/production)
- `FRONTEND_URL` - Frontend URL for CORS

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Development

1. Clone the repository
2. Set up backend: `cd backend && uv venv && source .venv/bin/activate && uv pip install -e .`
3. Set up frontend: `cd frontend && npm install`
4. Start backend: `cd backend && python app.py`
5. Start frontend: `cd frontend && npm run dev`
6. Visit http://localhost:3000

## Deployment

See `DEPLOYMENT.md` for detailed Railway deployment instructions.