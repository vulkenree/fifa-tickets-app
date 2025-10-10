from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from models import db, User, Ticket, Match
from datetime import datetime, date
import re
import os
import secrets
import csv

# FIFA 2026 World Cup date range
FIFA_MIN_DATE = date(2026, 6, 11)
FIFA_MAX_DATE = date(2026, 7, 19)

app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Session config for Next.js frontend
app.config['SESSION_COOKIE_SAMESITE'] = 'None' if os.environ.get('FLASK_ENV') == 'production' else 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True if os.environ.get('FLASK_ENV') == 'production' else False
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Smart database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Fix postgres:// to postgresql:// (Railway/Heroku compatibility)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"✅ Using PostgreSQL database")
else:
    # Default to SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/fifa_tickets.db'
    print(f"✅ Using SQLite database (local development)")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if os.environ.get('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Production settings
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

# Initialize database
db.init_app(app)

# Configure CORS for Next.js frontend
CORS(app, 
     origins=[
         'http://localhost:3000',  # Local dev
         os.environ.get('FRONTEND_URL', 'https://your-frontend.railway.app')
     ],
     supports_credentials=True,  # Allow cookies
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
)

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
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/ping')
def ping():
    """Simple ping endpoint for Railway health checks"""
    return jsonify({
        'status': 'ok',
        'message': 'FIFA 2026 Ticket App is running',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password or not confirm_password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html', show_register=True)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('login.html', show_register=True)
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('login.html', show_register=True)
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('login.html', show_register=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# API Auth endpoints for Next.js frontend
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API login endpoint for Next.js"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({
            'id': user.id,
            'username': user.username
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    """API logout endpoint"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """API registration endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # Log the user in after registration
    session['user_id'] = user.id
    session.permanent = True
    
    return jsonify({
        'id': user.id,
        'username': user.username
    }), 201

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current authenticated user"""
    user = User.query.get(session['user_id'])
    return jsonify({
        'id': user.id,
        'username': user.username
    })

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/health')
def health_check():
    """Health check endpoint for Railway and monitoring"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        database_status = 'connected'
    except Exception as e:
        database_status = f'error: {str(e)}'
    
    # Always return 200 for basic health check
    # Railway just needs to know the app is responding
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'FIFA 2026 Ticket App',
        'version': '1.0.0',
        'database': database_status,
        'port': os.environ.get('PORT', 'not_set'),
        'environment': os.environ.get('FLASK_ENV', 'not_set')
    }), 200

@app.route('/health/detailed')
def detailed_health_check():
    """Detailed health check with database connectivity test"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'FIFA 2026 Ticket App',
            'version': '1.0.0',
            'database': 'connected',
            'port': os.environ.get('PORT', 'not_set'),
            'environment': os.environ.get('FLASK_ENV', 'not_set')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'FIFA 2026 Ticket App',
            'error': str(e),
            'database': 'disconnected',
            'port': os.environ.get('PORT', 'not_set'),
            'environment': os.environ.get('FLASK_ENV', 'not_set')
        }), 503

@app.route('/api/tickets', methods=['GET'])
@login_required
def get_tickets():
    """Get all tickets (all users can see all tickets)"""
    tickets = Ticket.query.order_by(Ticket.date.desc()).all()
    return jsonify([ticket.to_dict() for ticket in tickets])

@app.route('/api/tickets', methods=['POST'])
@login_required
def create_ticket():
    """Create a new ticket"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'match_number', 'date', 'venue', 'ticket_category', 'quantity']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate match number exists in FIFA 2026 schedule
    match = Match.query.filter_by(match_number=data['match_number']).first()
    if not match:
        return jsonify({'error': 'Invalid match number. Please select from the dropdown.'}), 400
    
    # Validate date format - parse explicitly to avoid timezone issues
    try:
        date_parts = data['date'].split('-')
        if len(date_parts) != 3:
            raise ValueError("Invalid date format")
        date_obj = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])).date()
    except (ValueError, IndexError):
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate date is within FIFA 2026 World Cup period
    if not (FIFA_MIN_DATE <= date_obj <= FIFA_MAX_DATE):
        return jsonify({'error': f'Date must be between {FIFA_MIN_DATE.strftime("%B %d, %Y")} and {FIFA_MAX_DATE.strftime("%B %d, %Y")} (FIFA 2026 World Cup period)'}), 400
    
    # Validate quantity
    try:
        quantity = int(data['quantity'])
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be a positive number'}), 400
    except ValueError:
        return jsonify({'error': 'Quantity must be a valid number'}), 400
    
    # Validate ticket price if provided
    ticket_price = None
    if data.get('ticket_price'):
        try:
            ticket_price = float(data['ticket_price'])
            if ticket_price < 0:
                return jsonify({'error': 'Ticket price cannot be negative'}), 400
        except ValueError:
            return jsonify({'error': 'Ticket price must be a valid number'}), 400
    
    # Create ticket
    ticket = Ticket(
        user_id=session['user_id'],
        name=data['name'],
        match_number=data['match_number'],
        date=date_obj,
        venue=data['venue'],
        ticket_category=data['ticket_category'],
        quantity=quantity,
        ticket_info=data.get('ticket_info', ''),
        ticket_price=ticket_price
    )
    
    db.session.add(ticket)
    db.session.commit()
    
    return jsonify(ticket.to_dict()), 201

@app.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
@login_required
def update_ticket(ticket_id):
    """Update an existing ticket"""
    ticket = Ticket.query.filter_by(id=ticket_id, user_id=session['user_id']).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'match_number', 'date', 'venue', 'ticket_category', 'quantity']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate match number exists in FIFA 2026 schedule
    match = Match.query.filter_by(match_number=data['match_number']).first()
    if not match:
        return jsonify({'error': 'Invalid match number. Please select from the dropdown.'}), 400
    
    # Validate date format - parse explicitly to avoid timezone issues
    try:
        date_parts = data['date'].split('-')
        if len(date_parts) != 3:
            raise ValueError("Invalid date format")
        date_obj = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])).date()
    except (ValueError, IndexError):
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate date is within FIFA 2026 World Cup period
    if not (FIFA_MIN_DATE <= date_obj <= FIFA_MAX_DATE):
        return jsonify({'error': f'Date must be between {FIFA_MIN_DATE.strftime("%B %d, %Y")} and {FIFA_MAX_DATE.strftime("%B %d, %Y")} (FIFA 2026 World Cup period)'}), 400
    
    # Validate quantity
    try:
        quantity = int(data['quantity'])
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be a positive number'}), 400
    except ValueError:
        return jsonify({'error': 'Quantity must be a valid number'}), 400
    
    # Validate ticket price if provided
    ticket_price = None
    if data.get('ticket_price'):
        try:
            ticket_price = float(data['ticket_price'])
            if ticket_price < 0:
                return jsonify({'error': 'Ticket price cannot be negative'}), 400
        except ValueError:
            return jsonify({'error': 'Ticket price must be a valid number'}), 400
    
    # Update ticket
    ticket.name = data['name']
    ticket.match_number = data['match_number']
    ticket.date = date_obj
    ticket.venue = data['venue']
    ticket.ticket_category = data['ticket_category']
    ticket.quantity = quantity
    ticket.ticket_info = data.get('ticket_info', '')
    ticket.ticket_price = ticket_price
    
    db.session.commit()
    
    return jsonify(ticket.to_dict())

@app.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    """Delete a ticket"""
    ticket = Ticket.query.filter_by(id=ticket_id, user_id=session['user_id']).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    db.session.delete(ticket)
    db.session.commit()
    
    return jsonify({'message': 'Ticket deleted successfully'})

def init_match_data():
    """Initialize FIFA 2026 match schedule data from CSV if not already loaded or if data needs correction"""
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'fifa_match_schedule.csv')
    
    # Force reload all match data to fix timezone issues
    print("🔄 Force reloading all match data to fix timezone issues...")
    
    # Delete all existing matches
    Match.query.delete()
    db.session.commit()
    print("🗑️  Deleted all existing match records")
    
    if True:  # Always reload from CSV
        # Load data from CSV if no matches exist
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                match_count = 0
                for row in reader:
                    # Parse date explicitly to avoid timezone issues
                    date_parts = row['date'].split('-')
                    date_obj = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])).date()
                    
                    match = Match(
                        match_number=row['match_number'],
                        date=date_obj,
                        venue=row['venue']
                    )
                    db.session.add(match)
                    match_count += 1
                db.session.commit()
                print(f"✅ Loaded {match_count} FIFA 2026 matches from CSV with timezone-safe parsing")
        except FileNotFoundError:
            print(f"⚠️  Warning: Match schedule CSV not found at {csv_path}")
        except Exception as e:
            print(f"❌ Error loading match data: {e}")

@app.route('/api/matches', methods=['GET'])
def get_matches():
    """Get all FIFA 2026 matches for dropdown"""
    # Sort by numeric part of match_number (M1, M2, M10, etc.)
    matches = Match.query.all()
    sorted_matches = sorted(matches, key=lambda m: int(m.match_number.replace('M', '')))
    return jsonify([m.to_dict() for m in sorted_matches])

@app.route('/api/debug/matches', methods=['GET'])
def debug_matches():
    """Debug endpoint to check specific match data"""
    match_numbers = request.args.get('matches', 'M70,M71,M72,M73,M74,M75').split(',')
    matches = Match.query.filter(Match.match_number.in_(match_numbers)).all()
    result = []
    for match in matches:
        result.append({
            'match_number': match.match_number,
            'date': match.date.strftime('%Y-%m-%d'),
            'date_raw': str(match.date),
            'venue': match.venue
        })
    return jsonify(result)

@app.route('/api/matches/<match_number>', methods=['GET'])
def get_match_details(match_number):
    """Get date and venue for a specific match number"""
    match = Match.query.filter_by(match_number=match_number).first()
    if match:
        return jsonify(match.to_dict())
    return jsonify({'error': 'Match not found'}), 404

# Initialize database and data when app starts (works in both dev and production)
with app.app_context():
    db.create_all()
    
    # Initialize match schedule data from CSV
    init_match_data()
    
    # Create a default admin user if none exists
    if not User.query.first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: username='admin', password='admin123'")

if __name__ == '__main__':
    # Only run development server if not in production
    if os.environ.get('FLASK_ENV') != 'production':
        port = int(os.environ.get('PORT', 5001))
        app.run(debug=True, host='0.0.0.0', port=port)
