#!/bin/bash
set -e

echo "Starting FIFA 2026 Ticket App..."

# Initialize database
python -c "
from app import app, db, User
with app.app_context():
    db.create_all()
    if not User.query.first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created')
"

# Start gunicorn with Railway's PORT
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 30 --access-logfile - --error-logfile - app:app
