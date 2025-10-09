#!/bin/bash

# FIFA 2026 Ticket App - Production Startup Script

echo "🏆 Starting FIFA 2026 Ticket App..."

# Set production environment
export FLASK_ENV=production

# Initialize database if it doesn't exist
echo "📊 Initializing database..."
python -c "
from app import app, db, User
with app.app_context():
    db.create_all()
    if not User.query.first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✅ Default admin user created: username=admin, password=admin123')
    else:
        print('✅ Database already initialized')
"

# Start the application with gunicorn
echo "🚀 Starting application server..."
exec gunicorn --config gunicorn.conf.py app:app
