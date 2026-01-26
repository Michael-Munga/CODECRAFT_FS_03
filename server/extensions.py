from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import MetaData

# Naming convention for migrations
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Initialize extensions
db = SQLAlchemy(metadata=MetaData(naming_convention=convention))
bcrypt = Bcrypt()
ma = Marshmallow()
limiter = Limiter(
    key_func=get_remote_address,  # Use IP address as the rate limit key
    default_limits=["200 per day", "50 per hour"],  # Default limits
    storage_uri="memory://",  # In-memory storage (use Redis in production)
    strategy="fixed-window",  # Rate limiting strategy
    default_limits_exempt_when=lambda: False,  # Don't exempt any routes by default
    headers_enabled=True,  # Include rate limit headers in responses
    retry_after="http-date"  # Format for Retry-After header
)