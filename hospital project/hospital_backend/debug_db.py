"""
Debug database connection issues
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

print("=" * 70)
print("Database Connection Debugger")
print("=" * 70)

# Check environment variables
db_url = os.getenv("DATABASE_URL")
print(f"\n1. DATABASE_URL exists: {'✓' if db_url else '✗'}")

if db_url:
    # Check format
    print(f"2. DATABASE_URL format check:")
    if db_url.startswith("https://"):
        print("   ✗ ERROR: This is a REST API URL, not a database connection string!")
        print("   You need: postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres")
    elif db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
        print("   ✓ Format looks correct (PostgreSQL)")
        
        # Try to parse and show details (without password)
        try:
            if "@" in db_url:
                parts = db_url.split("@")
                if len(parts) == 2:
                    user_part = parts[0]
                    host_part = parts[1]
                    if ":" in user_part:
                        user = user_part.split(":")[-1].replace("postgresql://", "").replace("postgres://", "")
                        print(f"   User: {user}")
                    if ":" in host_part:
                        host = host_part.split(":")[0]
                        port = host_part.split(":")[1].split("/")[0]
                        db = host_part.split("/")[-1] if "/" in host_part else "postgres"
                        print(f"   Host: {host}")
                        print(f"   Port: {port}")
                        print(f"   Database: {db}")
        except Exception as e:
            print(f"   Could not parse: {e}")
    else:
        print("   ⚠️  Format might be incorrect")
    
    # Try connection
    print(f"\n3. Attempting connection...")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Try a simple query
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"   ✓ Connection successful!")
            print(f"   PostgreSQL version: {version[:50]}...")
            
            # Check if tables exist
            print(f"\n4. Checking tables...")
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f"   ✓ Found {len(tables)} tables:")
                for table in tables:
                    print(f"     - {table}")
            else:
                print("   ⚠️  No tables found. Run supabase_simple.sql in Supabase SQL Editor")
                
    except Exception as e:
        print(f"   ✗ Connection failed!")
        print(f"   Error: {str(e)}")
        print(f"\n   Common issues:")
        print(f"   1. Wrong password in DATABASE_URL")
        print(f"   2. Database not accessible (firewall/network)")
        print(f"   3. Wrong host/port")
        print(f"   4. Database doesn't exist")
        print(f"\n   To fix:")
        print(f"   1. Go to Supabase Dashboard → Settings → Database")
        print(f"   2. Copy the connection string (URI format)")
        print(f"   3. Replace [YOUR-PASSWORD] with actual password")
        print(f"   4. Update .env file")
else:
    print("\n✗ DATABASE_URL not found in .env file")

print("\n" + "=" * 70)



