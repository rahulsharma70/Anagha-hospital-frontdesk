"""
Configuration file for environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is required in .env file")

# Supabase Configuration
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")  # Optional: if using Supabase REST API

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 30  # 30 days

# OTP Service Configuration (Optional)
MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY", "")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

def get_config():
    """Get all configuration as dictionary"""
    return {
        "database_url_configured": bool(DATABASE_URL),
        "supabase_api_key_configured": bool(SUPABASE_API_KEY),
        "jwt_secret_configured": bool(JWT_SECRET),
    }

