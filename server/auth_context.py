
from flask import g, request
from functools import wraps
from logging_config import get_logger
from request_tracking import set_user_context
from flask import jsonify

def authenticate_user_context(user_id):
    """
    Set authentication context for the current request.
    """
    # Set user context in Flask's g object
    set_user_context(user_id, authenticated=True)
    
    # Log the authentication event
    auth_logger = get_logger('auth')
    auth_logger.info(
        f"User {user_id} authenticated successfully",
        event='user_authenticated',
        user_id=user_id,
        request_id=getattr(g, 'request_id', None),
        remote_addr=getattr(g, 'request_remote_addr', None),
        user_agent=getattr(g, 'request_user_agent', None)[:100]
    )


def logout_user_context():
    """
    Clear authentication context for the current request.
    """
    # Clear user context
    g.user_id = None
    g.user_authenticated = False
    
    # Log the logout event
    auth_logger = get_logger('auth')
    auth_logger.info(
        "User logged out",
        event='user_logged_out',
        request_id=getattr(g, 'request_id', None),
        remote_addr=getattr(g, 'request_remote_addr', None)
    )


def requires_authentication(f):
    """
    Decorator to ensure user is authenticated before accessing protected endpoints.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated (this would depend on your auth system)
        if not getattr(g, 'user_authenticated', False) or not getattr(g, 'user_id', None):
            # Log unauthorized access attempt
            auth_logger = get_logger('auth')
            auth_logger.warning(
                "Unauthorized access attempt",
                event='unauthorized_access',
                path=request.path,
                method=request.method,
                remote_addr=getattr(g, 'request_remote_addr', None),
                request_id=getattr(g, 'request_id', None)
            )
            
            # Return 401 Unauthorized response
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please log in to access this resource'
            }), 401
        
        # User is authenticated, proceed with the original function
        # Pass user_id as an argument to the decorated function
        return f(user_id=g.user_id, *args, **kwargs)
    
    return decorated_function


def log_user_action(action, user_id=None, **kwargs):
    """
    Log a user action with authentication context.
    """
    # Use provided user_id or current authenticated user
    target_user_id = user_id or getattr(g, 'user_id', None)
    
    # Prepare log data
    log_data = {
        'event': 'user_action',
        'action': action,
        'user_id': target_user_id,
        'request_id': getattr(g, 'request_id', None),
        'method': getattr(g, 'request_method', request.method if 'request' in globals() else None),
        'path': getattr(g, 'request_path', request.path if 'request' in globals() else None),
        **kwargs
    }
    
    # Log the user action
    auth_logger = get_logger('auth')
    auth_logger.info(
        f"User {target_user_id} performed action: {action}",
        **log_data
    )


def with_authentication_context(user_id_func=None):
    """
    Decorator factory to set authentication context for functions that need it.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            original_user_id = getattr(g, 'user_id', None)
            original_authenticated = getattr(g, 'user_authenticated', False)
            
            try:
                # Set temporary user context if provided
                if user_id_func:
                    temp_user_id = user_id_func()
                    if temp_user_id:
                        set_user_context(temp_user_id, authenticated=True)
                
                return func(*args, **kwargs)
            finally:
                # Restore original context
                if original_user_id is not None:
                    set_user_context(original_user_id, authenticated=original_authenticated)
                else:
                    g.user_id = original_user_id
                    g.user_authenticated = original_authenticated
        
        return wrapper
    return decorator


def jwt_auth_integration(jwt):
    """
    Integrate authentication context with Flask-JWT-Extended.
    """
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """
        Called when creating new tokens to get user identity.
        """
        if isinstance(user, (int, str)):
            return user
        return user.id if hasattr(user, 'id') else user.get('id')
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_payload):
        """
        Called when verifying tokens to get user object.
        This is where we can set authentication context.
        """
        user_id = jwt_payload['sub']
        
        # Set authentication context for the current request
        authenticate_user_context(user_id)
        
        # Return user object (you would load this from your database)
        # For this example, we'll return a mock user
        return {'id': user_id}