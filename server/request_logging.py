from flask import request, g
import time
import json
from logging_config import get_logger
from request_tracking import get_current_request_context


class ComprehensiveRequestLogger:
    """
    Enhanced middleware class for comprehensive request/response logging.
    
    ARCHITECTURE ROLE: The "Action Layer" (The Writer)
    This class is responsible for the actual recording of the request/response lifecycle.
    It relies on `request_tracking` (The Metadata Layer) to provide the context (IDs, start times),
    and then it performs the formatted logging.
    
    Prevention-focused: sensitive data never enters logs.
    """
    
    # Sensitive headers that should never be logged
    SENSITIVE_HEADERS = {
        'authorization', 'cookie', 'x-api-key', 'x-auth-token',
        'x-access-token', 'www-authenticate', 'proxy-authenticate',
        'x-forwarded-for', 'x-real-ip'
    }
    
    def __init__(self, app=None):
        self.logger = get_logger('http')
        self.security_logger = get_logger('security')
        self.performance_logger = get_logger('performance')
        self.error_logger = get_logger('errors')
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize the middleware with a Flask app.
        """
        app.before_request(self.log_request)
        app.after_request(self.log_response)
    
    def log_request(self):
        """
        Log incoming request details with automatic sensitive data prevention.
        Prevention-focused: sensitive data never reaches the logger.
        """
        # Store start time for duration calculation if not already set by tracking
        if not hasattr(g, 'start_time'):
            g.start_time = time.time()

        # Get all request details from one source of truth
        request_details = get_current_request_context()
        request_details['event'] = 'request_start'

        # Prevention: Apply safe user agent filtering
        if 'user_agent' in request_details:
            request_details['user_agent'] = self._safe_user_agent(request_details['user_agent'])

        # Prevention: Safely log headers (excluding sensitive ones)
        safe_headers = {}
        for header_name, header_value in request.headers:
            if header_name.lower() not in self.SENSITIVE_HEADERS:
                safe_headers[header_name] = header_value

        if safe_headers:
            request_details['headers'] = safe_headers

        # Prevention: Filter sensitive parameters from query strings
        if request.args:
            safe_args = self._filter_sensitive_params(dict(request.args))
            if safe_args:
                request_details['query_params'] = safe_args

        # Log the request with full context
        self.logger.info(
            f"{request_details.get('method')} {request_details.get('path')} - Request received",
            extra=request_details
        )

        # Enhanced security logging
        if request.method in ['POST', 'PUT', 'DELETE']:
            self.security_logger.info(
                f"{request.method} request to {request.path}",
                extra={
                    'event': 'security_request',
                    'method': request_details.get('method'),
                    'path': request_details.get('path'),
                    'remote_addr': request_details.get('remote_addr'),
                    'request_id': request_details.get('request_id'),
                    'content_length': request_details.get('content_length')
                }
            )
    
    def log_response(self, response):
        """
        Log response details with prevention-focused filtering.
        """
        # Calculate request duration
        start_time = getattr(g, 'start_time', time.time())
        duration_ms = (time.time() - start_time) * 1000
        
        # Get response details
        response_details = {
            'event': 'response_end',
            'status_code': response.status_code,
            'duration_ms': round(duration_ms, 2),
            'content_length': response.content_length or 0,
            'content_type': response.content_type or 'unknown',
        }
        
        # Add request context correlation
        request_context = get_current_request_context()
        response_details.update(request_context)
        
        # Log level based on status code
        if 200 <= response.status_code < 300:
            log_method = self.logger.info
            message = f"{request.method} {request.path} - Success"
            
            # Log performance metrics for successful requests
            self.performance_logger.info(
                f"Performance: {request.method} {request.path}",
                extra={
                    'event': 'performance_metric',
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration_ms, 2),
                    'remote_addr': request_context.get('remote_addr'),
                    'user_id': request_context.get('user_id'),
                    'request_id': request_context.get('request_id')
                }
            )
            
        elif 400 <= response.status_code < 500:
            log_method = self.logger.warning
            message = f"{request.method} {request.path} - Client error"
            
            # Log client errors for monitoring
            self.error_logger.warning(
                f"Client error {response.status_code} for {request.method} {request.path}",
                extra={
                    'status_code': response.status_code,
                    'path': request.path,
                    'method': request.method,
                    'remote_addr': request_context.get('remote_addr'),
                    'user_id': request_context.get('user_id'),
                    'request_id': request_context.get('request_id')
                }
            )
        else:
            log_method = self.logger.error
            message = f"{request.method} {request.path} - Server error"
            
            # Log server errors for immediate attention
            self.error_logger.error(
                f"Server error {response.status_code} for {request.method} {request.path}",
                extra={
                    'status_code': response.status_code,
                    'path': request.path,
                    'method': request.method,
                    'remote_addr': request_context.get('remote_addr'),
                    'user_id': request_context.get('user_id'),
                    'request_id': request_context.get('request_id')
                }
            )
        
        # Log the response
        log_method(message, extra=response_details)
        
        return response
    
    def _safe_user_agent(self, user_agent: str) -> str:
        """Extract safe information from user agent (prevention approach)."""
        # Don't log potentially sensitive device identifiers
        if 'Mozilla' in user_agent or 'Chrome' in user_agent:
            return 'Browser Client'
        elif 'curl' in user_agent.lower() or 'python' in user_agent.lower():
            return 'Programmatic Client'
        else:
            return 'Unknown Client'
    
    def _filter_sensitive_params(self, params: dict) -> dict:
        """Filter sensitive parameters from query strings (prevention approach)."""
        safe_params = {}
        sensitive_keywords = ['password', 'token', 'key', 'secret', 'auth', 'credential']
        
        for key, value in params.items():
            if not any(keyword in key.lower() for keyword in sensitive_keywords):
                safe_params[key] = value
        
        return safe_params


def setup_comprehensive_logging(app):
    """
    Setup comprehensive request/response logging for the Flask app.
    Prevention-focused implementation.
    """
    # Initialize the comprehensive logger
    logger_instance = ComprehensiveRequestLogger(app)
    
    # Log system initialization
    logger = get_logger()
    logger.info("Prevention-focused request logging initialized",
            extra={'event': 'secure_logging_setup_complete'})
    
    return logger_instance