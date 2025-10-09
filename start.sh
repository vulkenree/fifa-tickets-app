#!/bin/bash
set -e

echo "🚀 Starting FIFA 2026 Ticket Management App (Production Mode)"

# Create data directory for persistent storage
mkdir -p /app/data

# Initialize database
echo "📊 Initializing database..."
python << EOF
from app import app, db, User
import os

# Use data directory for production database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/data/fifa_tickets.db'

with app.app_context():
    db.create_all()
    if not User.query.first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✅ Default admin user created: username=admin, password=admin123')
        print('⚠️  Please change the admin password after first login!')
    else:
        print('✅ Database already initialized')
EOF

# Start gunicorn
echo "🌐 Starting Gunicorn server on port ${PORT}..."
exec gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --timeout 30 \
    --graceful-timeout 10 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
