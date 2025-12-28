"""
Error Monitoring with Sentry Integration
Provides centralized error tracking and monitoring
"""
import os
import logging
from typing import Optional
from functools import wraps
from fastapi import Request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sentry Configuration
SENTRY_DSN = os.getenv("SENTRY_DSN")
sentry_sdk = None

if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.httpx import HttpxIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                HttpxIntegration(),
            ],
            # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring
            traces_sample_rate=0.1,  # Adjust based on your needs
            # Set profiles_sample_rate to profile performance
            profiles_sample_rate=0.1,
            # Environment
            environment=os.getenv("ENVIRONMENT", "development"),
            # Release tracking
            release=os.getenv("RELEASE_VERSION", "1.0.0"),
            # Only send errors in production
            send_default_pii=False,  # Don't send PII
        )
        logger.info("✅ Sentry initialized successfully")
    except ImportError:
        logger.warning("⚠️ Sentry SDK not installed. Install with: pip install sentry-sdk[fastapi]")
        sentry_sdk = None
else:
    logger.info("ℹ️ Sentry DSN not configured. Error monitoring disabled.")


def capture_exception(error: Exception, context: Optional[dict] = None):
    """Capture exception in Sentry"""
    if sentry_sdk:
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            sentry_sdk.capture_exception(error)
    else:
        logger.error(f"Unhandled exception: {error}", exc_info=True)


def capture_message(message: str, level: str = "info", context: Optional[dict] = None):
    """Capture message in Sentry"""
    if sentry_sdk:
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            sentry_sdk.capture_message(message, level=level)
    else:
        logger.log(logging.INFO if level == "info" else logging.WARNING, message)


def log_error_with_context(error: Exception, request: Optional[Request] = None, user_id: Optional[int] = None):
    """Log error with request context"""
    context = {}
    
    if request:
        context["request"] = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        }
        # Add headers (excluding sensitive ones)
        if hasattr(request, "headers"):
            headers = dict(request.headers)
            # Remove sensitive headers
            sensitive_headers = ["authorization", "cookie", "x-api-key"]
            for header in sensitive_headers:
                headers.pop(header.lower(), None)
            context["headers"] = headers
    
    if user_id:
        context["user_id"] = user_id
    
    capture_exception(error, context)


def error_handler(func):
    """Decorator for error handling with Sentry"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Extract request if available
            request = None
            user_id = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            # Try to get user_id from kwargs
            current_user = kwargs.get("current_user")
            if current_user and isinstance(current_user, dict):
                user_id = current_user.get("id")
            
            log_error_with_context(e, request, user_id)
            raise
    
    return wrapper

