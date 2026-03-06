from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from logging_config import get_logger, log_metric
from request_tracking import get_current_request_context
import time
import traceback

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



def log_api_call(endpoint_name):
    """
    Decorator to log API calls with detailed metrics and error tracking.
    
    ARCHITECTURE NOTE:
    This decorator acts as a specific "Probe" that uses the unified logging system.
    It calculates its own duration (specific to the function) but uses 
    `log_metric` from `logging_config` to ensure the OUTPUT is consistent 
    with the rest of the application.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger = get_logger('api')
            request_context = get_current_request_context()
            
            try:
                # Log API call start
                logger.info(
                    f"API call started: {endpoint_name}",
                    event='api_call_started',
                    endpoint=endpoint_name,
                    **request_context
                )
                
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Log success
                logger.info(
                    f"API call completed: {endpoint_name}",
                    event='api_call_completed',
                    endpoint=endpoint_name,
                    status='success',
                    duration_ms=round(duration_ms, 2),
                    **request_context
                )
                
                # Record performance metric
                log_metric(
                    name=f'api_{endpoint_name}_duration',
                    value=round(duration_ms, 2),
                    unit='milliseconds',
                    endpoint=endpoint_name,
                    **request_context
                )
                
                return result
                
            except Exception as e:
                # Calculate duration even for failed calls
                duration_ms = (time.time() - start_time) * 1000
                
                # Log error
                logger.error(
                    f"API call failed: {endpoint_name} - {str(e)}",
                    event='api_call_failed',
                    endpoint=endpoint_name,
                    status='failed',
                    duration_ms=round(duration_ms, 2),
                    error=str(e),
                    traceback=traceback.format_exc(),
                    **request_context
                )
                
                # Record error metric
                log_metric(
                    name=f'api_{endpoint_name}_errors',
                    value=1,
                    unit='count',
                    endpoint=endpoint_name,
                    error_type=type(e).__name__,
                    **request_context
                )
                
                raise  # Re-raise the exception
                
        return wrapper
    return decorator


def log_performance(operation_name):
    """
    Decorator to measure and log performance of any function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger = get_logger('performance')
            request_context = get_current_request_context()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Log performance
                logger.info(
                    f"Operation completed: {operation_name}",
                    event='performance_metric',
                    operation=operation_name,
                    duration_ms=round(duration_ms, 2),
                    status='success',
                    **request_context
                )
                
                # Record metric
                log_metric(
                    name=f'operation_{operation_name}_duration',
                    value=round(duration_ms, 2),
                    unit='milliseconds',
                    operation=operation_name,
                    **request_context
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Operation failed: {operation_name} - {str(e)}",
                    event='performance_error',
                    operation=operation_name,
                    duration_ms=round(duration_ms, 2),
                    error=str(e),
                    **request_context
                )
                
                raise
                
        return wrapper
    return decorator