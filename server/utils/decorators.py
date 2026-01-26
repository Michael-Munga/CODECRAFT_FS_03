from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User


def admin_required(fn):
    """
    Decorator to ensure only admin users can access a route
    """
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return {'error': 'Admin access required'}, 403
        
        return fn(*args, **kwargs)
    return wrapper


def role_required(role):
    """
    Generic decorator to require a specific role
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user or current_user.role != role:
                return {'error': f'{role.title()} access required'}, 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator