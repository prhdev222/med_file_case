import jwt
import datetime
from functools import wraps
from flask import current_app, request, jsonify, g
from models.user import AdminUser

class JWTManager:
    @staticmethod
    def generate_token(user_id, username, role):
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),  # Token expires in 24 hours
            'iat': datetime.datetime.utcnow()  # Issued at
        }
        
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def decode_token(token):
        """Decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def get_token_from_request():
        """Extract token from request headers"""
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(' ')[1]
                return token
            except IndexError:
                return None
        return None

def jwt_required(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = JWTManager.get_token_from_request()
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing'
            }), 401
        
        payload = JWTManager.decode_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'message': 'Token is invalid or expired'
            }), 401
        
        # Store user info in g for use in the route
        g.current_user = {
            'user_id': payload['user_id'],
            'username': payload['username'],
            'role': payload['role']
        }
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user['role'] != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Get current user from JWT token"""
    if hasattr(g, 'current_user'):
        return AdminUser.query.get(g.current_user['user_id'])
    return None