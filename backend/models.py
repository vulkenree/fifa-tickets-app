from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Match(db.Model):
    """FIFA 2026 Match Schedule Lookup Table"""
    id = db.Column(db.Integer, primary_key=True)
    match_number = db.Column(db.String(10), unique=True, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            'match_number': self.match_number,
            'date': self.date.strftime('%Y-%m-%d'),
            'venue': self.venue
        }
    
    def __repr__(self):
        return f'<Match {self.match_number} - {self.venue}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased for scrypt hashes
    favorite_team = db.Column(db.String(100), nullable=True)  # FIFA 2026 favorite team
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to tickets
    tickets = db.relationship('Ticket', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Relationship to chat conversations
    chat_conversations = db.relationship('ChatConversation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    match_number = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    ticket_category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    ticket_info = db.Column(db.Text)
    ticket_price = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'name': self.name,
            'match_number': self.match_number,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'venue': self.venue,
            'ticket_category': self.ticket_category,
            'quantity': self.quantity,
            'ticket_info': self.ticket_info,
            'ticket_price': self.ticket_price,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Ticket {self.match_number} - {self.name}>'

class ChatConversation(db.Model):
    """Chat conversation metadata"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)  # Auto-generated or user-set title
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_saved = db.Column(db.Boolean, default=False)  # Whether user saved this conversation
    
    # Relationship to messages
    messages = db.relationship('ChatMessage', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None,
            'is_saved': self.is_saved,
            'message_count': len(self.messages)
        }
    
    def __repr__(self):
        return f'<ChatConversation {self.id} - {self.title}>'

class ChatMessage(db.Model):
    """Individual chat messages"""
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.id} - {self.role}>'
