"""
Quick script to check .env file configuration
Run: python3 check_env.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Environment Variables Check")
print("=" * 60)

db_url = os.getenv("DATABASE_URL")
api_key = os.getenv("SUPABASE_API_KEY")

print(f"\n1. DATABASE_URL: {'✓ Set' if db_url else '✗ Missing'}")
if db_url:
    if db_url.startswith("https://"):
        print("   ⚠️  WARNING: This looks like a REST API URL!")
        print("   You need a PostgreSQL connection string instead.")
        print("   Format: postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres")
    elif db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
        print("   ✓ Format looks correct (PostgreSQL connection string)")
        # Mask password for security
        if "@" in db_url:
            parts = db_url.split("@")
            if ":" in parts[0]:
                user_pass = parts[0].split(":")
                if len(user_pass) > 1:
                    masked = f"{user_pass[0]}:****@{parts[1]}"
                    print(f"   Example: {masked}")
    else:
        print("   ⚠️  Format might be incorrect")
        print("   Should start with: postgresql:// or postgres://")

print(f"\n2. SUPABASE_API_KEY: {'✓ Set' if api_key else '✗ Missing'}")
if api_key:
    print(f"   Length: {len(api_key)} characters")

print("\n" + "=" * 60)
print("How to get DATABASE_URL:")
print("=" * 60)
print("1. Go to Supabase Dashboard")
print("2. Settings → Database")
print("3. Under 'Connection string', select 'URI'")
print("4. Copy the connection string")
print("5. Replace [YOUR-PASSWORD] with your database password")
print("\nExample format:")
print("postgresql://postgres.xxxxx:PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
print("=" * 60)

