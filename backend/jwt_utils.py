"""JWT utility functions for authentication"""
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# JWT configuration
JWT_SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DAYS = 7


def generate_token(user_id: int, username: str) -> str:
    """Generate a JWT token for a user"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError('Token has expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')


def get_user_from_token() -> dict:
    """Extract user information from Authorization header"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    # Support both "Bearer <token>" and just "<token>" formats
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        token = auth_header
    
    try:
        payload = verify_token(token)
        return payload
    except ValueError:
        return None

