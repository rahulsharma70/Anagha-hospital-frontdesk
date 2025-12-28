import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file.")

# Validate DATABASE_URL format
if DATABASE_URL.startswith("https://"):
    raise ValueError(
        "DATABASE_URL should be a PostgreSQL connection string, not a REST API URL.\n"
        "Format: postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres\n"
        "Get it from: Supabase Dashboard → Settings → Database → Connection string"
    )

if not DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgres://"):
    raise ValueError(
        "DATABASE_URL must start with 'postgresql://' or 'postgres://'\n"
        "Current format appears incorrect. Please check your .env file."
    )

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            print("✓ Database connected successfully!")
            if SUPABASE_API_KEY:
                print("✓ SUPABASE_API_KEY is configured")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("\nPlease check:")
        print("1. DATABASE_URL in .env file is correct")
        print("2. Supabase database is running")
        print("3. Password in connection string is correct")
        return False

