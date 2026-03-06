from flask import g, request, jsonify
import time
import uuid
from functools import wraps
# Import the unified logging tool (The "Pen")
from logging_config import log_metric, get_logger

# ==========================================
# METADATA LAYER (The "Receptionist")
# ==========================================
# This module is responsible for SETTING context.
# It assigns IDs and starts timers, but it delegates
# the actual writing of logs to the logging_config module.

def request_context_middleware(app):
    """
    Flask middleware to add comprehensive request context tracking.
    """
    
    @app.before_request
    def setup_request_context():
        """Initialize request context with timing and correlation data"""
        # Generate unique request ID for tracing
        g.request_id = str(uuid.uuid4())
        
        # Store request start time for performance measurement
        g.start_time = time.time()
        
        # Store request metadata for logging
        g.request_method = request.method
        g.request_path = request.path
        g.request_full_path = request.full_path        
        g.request_remote_addr = request.remote_addr
        g.request_content_type = request.content_type  
        g.request_content_length = request.content_length  
        g.request_user_agent = request.headers.get('User-Agent', 'Unknown')  
        
        # Initialize user context (will be set by auth system)
        g.user_id = None
        g.user_authenticated = False
    
    @app.after_request
    def finalize_request_context(response):
        """
        Add request context to response.
        """
        # Calculate request duration for performance metrics
        duration_ms = (time.time() - g.start_time) * 1000
        
        # Add request ID to response headers for client correlation
        response.headers['X-Request-ID'] = g.request_id
        
        # Add performance metrics to response headers
        response.headers['X-Response-Time'] = f'{duration_ms:.2f}ms'
        
        return response


def get_current_request_context():
    """
    Get current request context data for logging.
    """
    context = {
        'request_id': getattr(g, 'request_id', None),
        'user_id': getattr(g, 'user_id', None),
        'method': getattr(g, 'request_method', None),
        'path': getattr(g, 'request_path', None),
        'full_path': getattr(g, 'request_full_path', None),        
        'remote_addr': getattr(g, 'request_remote_addr', None),
        'content_type': getattr(g, 'request_content_type', None),  
        'content_length': getattr(g, 'request_content_length', None),  
        'user_agent': getattr(g, 'request_user_agent', None),   
    }
    
    # Only include non-None values
    return {k: v for k, v in context.items() if v is not None}


def set_user_context(user_id, authenticated=True):
    """
    Set user authentication context for current request.
    """
    g.user_id = user_id
    g.user_authenticated = authenticated
    
    # Log authentication context
    logger = get_logger('auth')
    logger.info(
        f"User {user_id} authenticated for request",
        user_id=user_id,
        request_id=getattr(g, 'request_id', None),
        event='user_authenticated'
    )



class PerformanceTimer:
    """
    Context manager for measuring performance of code blocks.
    """
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            
            # Use the unified logging tool to record this metric
            # This ensures consistent formatting and security (prevention of sensitive data)
            log_metric(
                name=self.operation_name, 
                value=round(duration_ms, 2),
                unit='ms',
                description='PerformanceTimer measurement'
            )


def with_performance_monitoring(operation_name):
    """
    Decorator to monitor performance of function execution.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceTimer(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Backward compatibility for existing references
request_id_middleware = request_context_middleware