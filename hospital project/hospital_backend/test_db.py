"""
Test database connection script
Run: python3 test_db.py
"""
import os
from dotenv import load_dotenv
from database import test_connection, engine, SUPABASE_API_KEY

if __name__ == "__main__":
    load_dotenv()
    
    print("=" * 50)
    print("Testing Configuration")
    print("=" * 50)
    
    # Check environment variables
    db_url = os.getenv("DATABASE_URL")
    api_key = os.getenv("SUPABASE_API_KEY")
    
    print(f"\nDATABASE_URL: {'✓ Set' if db_url else '✗ Missing'}")
    print(f"SUPABASE_API_KEY: {'✓ Set' if api_key else '✗ Missing'}")
    
    print("\n" + "-" * 50)
    print("Testing Database Connection...")
    print("-" * 50)
    
    if test_connection():
        print("\n" + "=" * 50)
        print("✓ All checks passed!")
        print("=" * 50)
        print("\nYou can now run: uvicorn main:app --reload")
        print("API will be available at: http://127.0.0.1:8000")
    else:
        print("\n" + "=" * 50)
        print("✗ Configuration check failed!")
        print("=" * 50)
        print("\nPlease check your .env file:")
        print("1. DATABASE_URL should be set")
        print("2. Format: postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres")
        print("3. Make sure .env file is in the hospital_backend folder")

