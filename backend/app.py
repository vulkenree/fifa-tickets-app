from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from models import db, User, Ticket, Match, ChatConversation, ChatMessage
from datetime import datetime, date
import re
import os
import secrets
import csv
import sys
import logging
from llm_service import LLMService
from jwt_utils import generate_token, get_user_from_token

# Configure logging to ensure all messages are captured in Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True  # Override any existing configuration
)
logger = logging.getLogger(__name__)

# FIFA 2026 World Cup date range
FIFA_MIN_DATE = date(2026, 6, 11)
FIFA_MAX_DATE = date(2026, 7, 19)

app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Smart database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Fix postgres:// to postgresql:// (Railway/Heroku compatibility)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    logger.info("Using PostgreSQL database")
else:
    # Default to SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/fifa_tickets.db'
    logger.info("Using SQLite database (local development)")

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

# Initialize LLM service
llm_service = LLMService()

# Configure CORS for Next.js frontend
CORS(app, 
     origins=[
         'http://localhost:3000',  # Local dev
         'https://fifa-tickets-frontendapp-production.up.railway.app',  # Production
         os.environ.get('FRONTEND_URL', '')  # Custom domain if set
     ],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
)

def login_required(f):
    """Decorator to require JWT authentication for protected routes"""
    def decorated_function(*args, **kwargs):
        user_data = get_user_from_token()
        
        if not user_data:
            # Check if this is an API route
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            else:
                return redirect(url_for('login'))
        
        # Add user_id to kwargs so endpoints can access it
        kwargs['user_id'] = user_data['user_id']
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
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
    # This route is for server-side rendering (if needed)
    # API login is handled by /api/auth/login
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # This route is for server-side rendering (if needed)
    # API registration is handled by /api/auth/register
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # JWT is stateless, so logout is handled client-side
    return redirect(url_for('login'))

# API Auth endpoints for Next.js frontend
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API login endpoint for Next.js - returns JWT token"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        # Generate JWT token
        token = generate_token(user.id, user.username)
        
        logger.info(f"✅ Login successful for user {username} (ID: {user.id})")
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username
            }
        })
    else:
        logger.warning(f"❌ Login failed for username: {username}")
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """API logout endpoint - JWT is stateless, so logout is handled client-side"""
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """API registration endpoint - returns JWT token"""
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
    
    # Generate JWT token
    token = generate_token(user.id, user.username)
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username
        }
    }), 201

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user(user_id):
    """Get current authenticated user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username
    })

@app.route('/api/debug/session', methods=['GET'])
def debug_session():
    """Debug endpoint to check JWT authentication state"""
    user_data = get_user_from_token()
    debug_info = {
        'authenticated': user_data is not None,
        'user_data': user_data,
        'auth_header': request.headers.get('Authorization'),
        'request_origin': request.headers.get('Origin'),
        'flask_env': os.environ.get('FLASK_ENV'),
    }
    return jsonify(debug_info)

@app.route('/dashboard')
def dashboard():
    # Dashboard is handled by Next.js frontend
    return redirect(url_for('index'))


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
def get_tickets(user_id):
    """Get all tickets (all users can see all tickets)"""
    tickets = Ticket.query.order_by(Ticket.date.desc()).all()
    return jsonify([ticket.to_dict() for ticket in tickets])

@app.route('/api/tickets', methods=['POST'])
@login_required
def create_ticket(user_id):
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
        user_id=user_id,
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
def update_ticket(ticket_id, user_id):
    """Update an existing ticket"""
    ticket = Ticket.query.filter_by(id=ticket_id, user_id=user_id).first()
    
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
def delete_ticket(ticket_id, user_id):
    """Delete a ticket"""
    ticket = Ticket.query.filter_by(id=ticket_id, user_id=user_id).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    db.session.delete(ticket)
    db.session.commit()
    
    return jsonify({'message': 'Ticket deleted successfully'})

def init_match_data():
    """Initialize FIFA 2026 match schedule data from CSV if not already loaded or if data needs correction"""
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'fifa_match_schedule.csv')
    
    # Force reload all match data to fix timezone issues
    logger.info("Force reloading all match data to fix timezone issues...")
    
    # Delete all existing matches
    Match.query.delete()
    db.session.commit()
    logger.info("Deleted all existing match records")
    
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
                logger.info(f"Loaded {match_count} FIFA 2026 matches from CSV with timezone-safe parsing")
        except FileNotFoundError:
            logger.warning(f"Match schedule CSV not found at {csv_path}")
        except Exception as e:
            logger.error(f"Error loading match data: {e}")

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

# Chat API endpoints
@app.route('/api/chat/message', methods=['POST'])
@login_required
def send_chat_message(user_id):
    """Send a message to the AI assistant"""
    data = request.get_json()
    message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        # Get or create conversation
        if conversation_id:
            conversation = ChatConversation.query.filter_by(
                id=conversation_id, 
                user_id=user_id
            ).first()
            if not conversation:
                return jsonify({'error': 'Conversation not found'}), 404
        else:
            # Create new conversation
            conversation = ChatConversation(
                user_id=user_id,
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            db.session.add(conversation)
            db.session.flush()  # Get the ID
        
        # Save user message
        user_message = ChatMessage(
            conversation_id=conversation.id,
            role='user',
            content=message
        )
        db.session.add(user_message)
        
        # Get AI response
        response = llm_service.process_message(
            user_id=user_id,
            message=message,
            conversation_id=conversation.id
        )
        
        # Save AI response
        ai_message = ChatMessage(
            conversation_id=conversation.id,
            role='assistant',
            content=response['content']
        )
        db.session.add(ai_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'conversation_id': conversation.id,
            'response': response['content'],
            'function_called': response.get('function_called'),
            'function_result': response.get('function_result'),
            'error': response.get('error', False)
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in send_chat_message: {e}")
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/api/chat/conversations', methods=['GET'])
@login_required
def get_chat_conversations(user_id):
    """Get all conversations for the current user"""
    try:
        conversations = ChatConversation.query.filter_by(
            user_id=user_id
        ).order_by(ChatConversation.updated_at.desc()).all()
        
        return jsonify([conv.to_dict() for conv in conversations])
    except Exception as e:
        logger.error(f"Error in get_chat_conversations: {e}")
        return jsonify({'error': 'Failed to get conversations'}), 500

@app.route('/api/chat/conversations/<int:conversation_id>', methods=['GET'])
@login_required
def get_chat_conversation(conversation_id, user_id):
    """Get a specific conversation with its messages"""
    try:
        conversation = ChatConversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        messages = ChatMessage.query.filter_by(
            conversation_id=conversation_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        return jsonify({
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        })
    except Exception as e:
        logger.error(f"Error in get_chat_conversation: {e}")
        return jsonify({'error': 'Failed to get conversation'}), 500

@app.route('/api/chat/conversations/<int:conversation_id>', methods=['DELETE'])
@login_required
def delete_chat_conversation(conversation_id, user_id):
    """Delete a conversation"""
    try:
        conversation = ChatConversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        db.session.delete(conversation)
        db.session.commit()
        
        return jsonify({'message': 'Conversation deleted successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in delete_chat_conversation: {e}")
        return jsonify({'error': 'Failed to delete conversation'}), 500

@app.route('/api/chat/conversations/<int:conversation_id>/save', methods=['POST'])
@login_required
def save_chat_conversation(conversation_id, user_id):
    """Mark a conversation as saved"""
    try:
        conversation = ChatConversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        conversation.is_saved = True
        db.session.commit()
        
        return jsonify({'message': 'Conversation saved successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in save_chat_conversation: {e}")
        return jsonify({'error': 'Failed to save conversation'}), 500

@app.route('/api/chat/conversations/<int:conversation_id>/unsave', methods=['POST'])
@login_required
def unsave_chat_conversation(conversation_id, user_id):
    """Mark a conversation as not saved"""
    try:
        conversation = ChatConversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        conversation.is_saved = False
        db.session.commit()
        
        return jsonify({'message': 'Conversation unsaved successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in unsave_chat_conversation: {e}")
        return jsonify({'error': 'Failed to unsave conversation'}), 500

# Profile API endpoints
@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile(user_id):
    """Get current user profile"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'favorite_team': user.favorite_team,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else None
        })
    except Exception as e:
        logger.error(f"Error in get_profile: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile(user_id):
    """Update user profile"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Username changes are not allowed
        if 'username' in data:
            return jsonify({'error': 'Username cannot be changed'}), 400
        
        # Update favorite team if provided
        if 'favorite_team' in data:
            favorite_team = data['favorite_team']
            if favorite_team and len(favorite_team) > 100:
                return jsonify({'error': 'Favorite team name too long'}), 400
            user.favorite_team = favorite_team if favorite_team else None
        
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'favorite_team': user.favorite_team,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else None
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in update_profile: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

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
        logger.info("Default admin user created: username='admin', password='admin123'")

@app.route('/api/venues', methods=['GET'])
def get_venues():
    """Get all unique venues with coordinates"""
    venues = [
        # USA venues
        {"name": "Atlanta", "city": "Atlanta", "country": "USA", "lat": 33.7490, "lng": -84.3880},
        {"name": "Boston", "city": "Boston", "country": "USA", "lat": 42.3601, "lng": -71.0589},
        {"name": "Dallas", "city": "Dallas", "country": "USA", "lat": 32.7767, "lng": -96.7970},
        {"name": "Houston", "city": "Houston", "country": "USA", "lat": 29.7604, "lng": -95.3698},
        {"name": "Kansas City", "city": "Kansas City", "country": "USA", "lat": 39.0997, "lng": -94.5786},
        {"name": "Los Angeles", "city": "Los Angeles", "country": "USA", "lat": 34.0522, "lng": -118.2437},
        {"name": "Miami", "city": "Miami", "country": "USA", "lat": 25.7617, "lng": -80.1918},
        {"name": "New York/New Jersey", "city": "New York/New Jersey", "country": "USA", "lat": 40.7128, "lng": -74.0060},
        {"name": "Philadelphia", "city": "Philadelphia", "country": "USA", "lat": 39.9526, "lng": -75.1652},
        {"name": "San Francisco Bay Area", "city": "San Francisco Bay Area", "country": "USA", "lat": 37.7749, "lng": -122.4194},
        {"name": "Seattle", "city": "Seattle", "country": "USA", "lat": 47.6062, "lng": -122.3321},
        
        # Canada venues
        {"name": "Toronto", "city": "Toronto", "country": "Canada", "lat": 43.6532, "lng": -79.3832},
        {"name": "Vancouver", "city": "Vancouver", "country": "Canada", "lat": 49.2827, "lng": -123.1207},
        
        # Mexico venues
        {"name": "Guadalajara", "city": "Guadalajara", "country": "Mexico", "lat": 20.6597, "lng": -103.3496},
        {"name": "Mexico City", "city": "Mexico City", "country": "Mexico", "lat": 19.4326, "lng": -99.1332},
        {"name": "Monterrey", "city": "Monterrey", "country": "Mexico", "lat": 25.6866, "lng": -100.3161},
    ]
    return jsonify(venues)

if __name__ == '__main__':
    # Only run development server if not in production
    if os.environ.get('FLASK_ENV') != 'production':
        port = int(os.environ.get('PORT', 5001))
        app.run(debug=True, host='0.0.0.0', port=port)
