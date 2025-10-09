from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from models import db, User, Ticket
from datetime import datetime, date
import re
import os
import secrets

# FIFA 2026 World Cup date range
FIFA_MIN_DATE = date(2026, 6, 11)
FIFA_MAX_DATE = date(2026, 7, 19)

app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fifa_tickets.db')
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

def validate_match_number(match_number):
    """Validate that match number starts with M followed by digits"""
    pattern = r'^M\d+$'
    return bool(re.match(pattern, match_number))

def login_required(f):
    """Decorator to require login for protected routes"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
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

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/user')
@login_required
def get_current_user():
    """Get current user information"""
    user = User.query.get(session['user_id'])
    return jsonify({
        'id': user.id,
        'username': user.username
    })

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
    
    # Validate match number format
    if not validate_match_number(data['match_number']):
        return jsonify({'error': 'Match number must start with M followed by digits (e.g., M1, M23)'}), 400
    
    # Validate date format
    try:
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
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
    
    # Validate match number format
    if not validate_match_number(data['match_number']):
        return jsonify({'error': 'Match number must start with M followed by digits (e.g., M1, M23)'}), 400
    
    # Validate date format
    try:
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create a default admin user if none exists
        if not User.query.first():
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")
    
    # Only run development server if not in production
    if os.environ.get('FLASK_ENV') != 'production':
        port = int(os.environ.get('PORT', 5001))
        app.run(debug=True, host='0.0.0.0', port=port)
