import logging
import logging.handlers
import json
import os
from datetime import datetime
from flask import g
import re  # Added for enhanced filtering
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format.
    Enhanced with prevention-focused security filtering.
    """
    
    # Define fields that should never be logged (prevention approach)
    FORBIDDEN_FIELDS = {
        'password', 'token', 'secret', 'key', 'authorization', 'auth',
        'credentials', 'credit_card', 'ssn', 'cvv', 'card_number',
        'pin', 'cvv2', 'cvc', 'account_number', 'iban', 'bic',
        'api_key', 'access_token', 'refresh_token', 'session_id',
        'private_key', 'certificate', 'jwt', 'bearer', 'otp', 'sms_code'
    }
    
    def format(self, record):
        """
        Convert a LogRecord into a JSON-formatted string.
        Prevention-focused: sensitive data never enters logs.
        """
        # Get basic log information
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',  # UTC timestamp in ISO 8601 format
            'level': record.levelname,                        # Log level (INFO, ERROR, etc.)
            'logger': record.name,                            # Logger name (e.g. 'ecommerce.http')
            'message': record.getMessage(),                   # Direct message (no sanitization needed)
            'module': record.module,                          # Python module name
            'function': record.funcName,                      # Function where log was called
            'line': record.lineno,                            # Line number for debugging
        }
        
        # Add request context if available (from Flask g object)
        try:
            if hasattr(g, 'request_id'):
                log_entry['request_id'] = g.request_id
                
            if hasattr(g, 'user_id'):
                log_entry['user_id'] = g.user_id  # Only user ID, not personal data
        except RuntimeError:
            # Not in application context, skip request context
            pass
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Process extra fields with strict prevention filtering
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 
                          'funcName', 'created', 'msecs', 'relativeCreated', 
                          'thread', 'threadName', 'processName', 'process',
                          'exc_info', 'exc_text', 'stack_info']:
                # Prevention: Only add non-sensitive fields
                if self._is_safe_field(key):
                    log_entry[key] = self._process_safe_value(value)
        
        return json.dumps(log_entry, ensure_ascii=False)
    
    def _is_safe_field(self, field_name: str) -> bool:
        """Check if a field name is safe to log (prevention approach)."""
        lower_name = field_name.lower()
        return not any(forbidden in lower_name for forbidden in self.FORBIDDEN_FIELDS)
    
    def _process_safe_value(self, value: Any) -> Any:
        """Process values ensuring no sensitive data (prevention approach)."""
        if isinstance(value, dict):
            return self._filter_sensitive_dict(value)
        elif isinstance(value, list):
            return [self._process_safe_value(item) for item in value]
        else:
            return value
    
    def _filter_sensitive_dict(self, data: Dict) -> Dict:
        """Filter dictionary to remove sensitive fields (prevention approach)."""
        result = {}
        for key, value in data.items():
            if self._is_safe_field(str(key)):
                if isinstance(value, (dict, list)):
                    result[key] = self._process_safe_value(value)
                else:
                    result[key] = value
        return result


def setup_logging(log_level=logging.INFO, log_file_path='logs/app.log'):
    """
    Configure application logging with prevention-focused security.
    Modern approach: prevent sensitive data at source.
    """
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger('ecommerce')
    logger.setLevel(log_level)
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    formatter = JSONFormatter()  # Updated formatter with prevention
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation (for production)
    # Rotates when file reaches 10MB, keeps 5 backup files
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=10*1024*1024,  # 10MB - Balance between detail and manageability
        backupCount=5           # Keep 5 old files for historical analysis
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)  # Same prevention-focused format
    logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    # Log system initialization
    logger.info("Prevention-focused logging system initialized",
                extra={'log_level': str(log_level), 
                       'log_file': log_file_path,
                       'event': 'secure_logging_initialized'})
    
    return logger


class KwargsLoggerAdapter(logging.LoggerAdapter):
    """Adapter to absorb arbitrary kwargs into the standard 'extra' dictionary."""
    def process(self, msg, kwargs):
        extra = dict(self.extra) if self.extra else {}
        if 'extra' in kwargs:
            extra.update(kwargs.pop('extra'))
            
        standard_kwargs = {'exc_info', 'stack_info', 'stacklevel'}
        for k in list(kwargs.keys()):
            if k not in standard_kwargs:
                extra[k] = kwargs.pop(k)
                
        if extra:
            kwargs['extra'] = extra
            
        return msg, kwargs


def get_logger(name=None):
    """
    Get a logger instance. If name is None, returns the main app logger.
    Enhanced with prevention-focused approach.
    """
    if name:
        logger = logging.getLogger(f'ecommerce.{name}')
    else:
        logger = logging.getLogger('ecommerce')
    return KwargsLoggerAdapter(logger, {})


# Enhanced convenience functions with prevention approach
def log_info(message, safe_data=None, **kwargs):
    """Log INFO level message with prevention-focused filtering."""
    logger = get_logger()
    
    # Prevention: Filter out sensitive data from kwargs
    safe_kwargs = {k: v for k, v in kwargs.items() 
                   if k.lower() not in JSONFormatter.FORBIDDEN_FIELDS}
    
    # Add safe_data if provided
    if safe_data and isinstance(safe_data, dict):
        safe_kwargs.update({k: v for k, v in safe_data.items() 
                           if k.lower() not in JSONFormatter.FORBIDDEN_FIELDS})
    
    logger.info(message, **safe_kwargs)


def log_warning(message, safe_data=None, **kwargs):
    """Log WARNING level message with prevention-focused filtering."""
    logger = get_logger()
    
    # Prevention: Filter out sensitive data
    safe_kwargs = {k: v for k, v in kwargs.items() 
                   if k.lower() not in JSONFormatter.FORBIDDEN_FIELDS}
    
    if safe_data and isinstance(safe_data, dict):
        safe_kwargs.update({k: v for k, v in safe_data.items() 
                           if k.lower() not in JSONFormatter.FORBIDDEN_FIELDS})
    
    logger.warning(message, **safe_kwargs)


def log_error(message, error=None, safe_data=None, **kwargs):
    """Log ERROR level message with prevention-focused filtering."""
    logger = get_logger()
    
    # Prevention: Filter out sensitive data
    safe_kwargs = {k: v for k, v in kwargs.items() 
                   if k.lower() not in JSONFormatter.FORBIDDEN_FIELDS}
    
    # Add error information safely
    if error:
        safe_kwargs['error_type'] = type(error).__name__
        safe_kwargs['error_message'] = str(error) if str(error) else 'Error occurred'
    
    if safe_data and isinstance(safe_data, dict):
        safe_kwargs.update({k: v for k, v in safe_data.items() 
                           if k.lower() not in JSONFormatter.FORBIDDEN_FIELDS})
    
    logger.error(message, **safe_kwargs)


def log_exception(message, error=None, safe_data=None, **kwargs):
    """Log ERROR level message with exception traceback and prevention filtering."""
    logger = get_logger()
    
    # Prevention: Filter out sensitive data
    safe_kwargs = {k: v for k, v in kwargs.items() 
                   if k.lower() not in JSONFormatter.FORBIDDEN_FIELDS}
    
    if error:
        safe_kwargs['error_type'] = type(error).__name__
        safe_kwargs['error_message'] = str(error) if str(error) else 'Error occurred'
    
    if safe_data and isinstance(safe_data, dict):
        safe_kwargs.update({k: v for k, v in safe_data.items() 
                           if k.lower() not in JSONFormatter.FORBIDDEN_FIELDS})
    
    logger.exception(message, **safe_kwargs)


def log_metric(name, value, unit=None, safe_data=None, **kwargs):
    """
    Log a custom metric with prevention-focused context filtering.
    """
    logger = get_logger('metrics')
    
    # Prevention: Filter out sensitive data
    safe_kwargs = {k: v for k, v in kwargs.items() 
                   if k.lower() not in JSONFormatter.FORBIDDEN_FIELDS}
    
    metric_data = {
        'metric_name': name,
        'value': value,
        'unit': unit,
        'event': 'custom_metric',
        **safe_kwargs
    }
    
    # Add safe_data if provided
    if safe_data and isinstance(safe_data, dict):
        metric_data.update({k: v for k, v in safe_data.items() 
                           if k.lower() not in JSONFormatter.FORBIDDEN_FIELDS})
    
    message = f"Metric recorded: {name} = {value}"
    if unit:
        message += f" {unit}"
        
    logger.info(message, **metric_data)