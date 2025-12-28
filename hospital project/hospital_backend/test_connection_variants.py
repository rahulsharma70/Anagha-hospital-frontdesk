"""
Test different Supabase connection string formats
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

PROJECT_REF = "lrzlkoxqwtzwmbehfngn"
current_url = os.getenv("DATABASE_URL", "")

print("=" * 70)
print("Testing Different Connection String Formats")
print("=" * 70)

if not current_url:
    print("\n✗ DATABASE_URL not found in .env")
    exit(1)

# Extract password if possible
password = None
if "@" in current_url and ":" in current_url.split("@")[0]:
    try:
        password = current_url.split(":")[2].split("@")[0] if len(current_url.split(":")) > 2 else None
    except:
        pass

if not password:
    print("\n⚠️  Could not extract password from current DATABASE_URL")
    print("Please provide your database password to test different formats")
    password = input("Enter your Supabase database password: ").strip()

# Test different connection string formats
formats_to_test = [
    {
        "name": "Direct Connection (Port 5432)",
        "url": f"postgresql://postgres:{password}@db.{PROJECT_REF}.supabase.co:5432/postgres"
    },
    {
        "name": "Connection Pooling - Session Mode (Port 6543)",
        "url": f"postgresql://postgres.{PROJECT_REF}:{password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    },
    {
        "name": "Connection Pooling - Transaction Mode (Port 6543)",
        "url": f"postgresql://postgres.{PROJECT_REF}:{password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true"
    },
    {
        "name": "Alternative Direct Format",
        "url": f"postgresql://postgres:{password}@{PROJECT_REF}.supabase.co:5432/postgres"
    }
]

print(f"\nTesting {len(formats_to_test)} connection formats...\n")

successful_format = None

for i, format_info in enumerate(formats_to_test, 1):
    print(f"{i}. Testing: {format_info['name']}")
    print(f"   URL: {format_info['url'].replace(password, '***')}")
    
    try:
        engine = create_engine(format_info['url'], connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            print(f"   ✓ SUCCESS! This format works!")
            successful_format = format_info
            break
    except Exception as e:
        error_msg = str(e)
        if "could not translate host name" in error_msg:
            print(f"   ✗ Hostname not found")
        elif "password authentication failed" in error_msg:
            print(f"   ✗ Wrong password")
        elif "timeout" in error_msg.lower():
            print(f"   ✗ Connection timeout")
        else:
            print(f"   ✗ Error: {error_msg[:60]}...")
    print()

if successful_format:
    print("=" * 70)
    print("✓ WORKING CONNECTION STRING FOUND!")
    print("=" * 70)
    print(f"\nUpdate your .env file with:")
    print(f"\nDATABASE_URL={successful_format['url']}")
    print(f"\nThen test again with: python3 test_db.py")
else:
    print("=" * 70)
    print("✗ None of the formats worked")
    print("=" * 70)
    print("\nPlease:")
    print("1. Go to Supabase Dashboard → Settings → Database")
    print("2. Copy the exact connection string from there")
    print("3. Make sure password is correct")
    print("4. Check your internet connection")



