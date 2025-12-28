# ... existing code ...
from services.error_monitoring import capture_exception, log_error_with_context, capture_message
from services.audit_logger import log_login_attempt
# ... existing code ...

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with Sentry integration"""
    log_error_with_context(exc, request)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Error has been logged."}
    )

# ... existing code ...
