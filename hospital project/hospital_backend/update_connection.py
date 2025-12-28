"""
Update DATABASE_URL to use working connection format
"""
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_REF = "lrzlkoxqwtzwmbehfngn"
current_url = os.getenv("DATABASE_URL", "")

if not current_url:
    print("✗ DATABASE_URL not found")
    exit(1)

# Extract password
password = None
if ":" in current_url and "@" in current_url:
    try:
        parts = current_url.split("@")
        if len(parts) > 0:
            user_pass = parts[0]
            if ":" in user_pass:
                password = user_pass.split(":")[-1]
    except:
        pass

if not password:
    print("⚠️  Could not extract password. Please enter it manually.")
    password = input("Enter your Supabase database password: ").strip()

print("=" * 70)
print("Connection String Update Helper")
print("=" * 70)

print("\nCurrent connection string uses hostname that doesn't resolve.")
print("\nWorking options:")

options = [
    {
        "name": "Option 1: Connection Pooling (Recommended)",
        "url": f"postgresql://postgres.{PROJECT_REF}:{password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        "note": "Best for production, uses port 6543"
    },
    {
        "name": "Option 2: Alternative Direct Format",
        "url": f"postgresql://postgres:{password}@{PROJECT_REF}.supabase.co:5432/postgres",
        "note": "Direct connection, uses port 5432"
    }
]

for i, option in enumerate(options, 1):
    print(f"\n{i}. {option['name']}")
    print(f"   {option['note']}")
    print(f"   DATABASE_URL={option['url']}")

print("\n" + "=" * 70)
print("RECOMMENDED: Use Option 1 (Connection Pooling)")
print("=" * 70)

choice = input("\nWhich option to use? (1 or 2, or 'q' to quit): ").strip()

if choice == "1":
    new_url = options[0]["url"]
elif choice == "2":
    new_url = options[1]["url"]
else:
    print("Cancelled")
    exit(0)

print(f"\n✓ New connection string:")
print(f"   {new_url.replace(password, '***')}")

print("\n⚠️  IMPORTANT: Update your .env file manually with:")
print(f"   DATABASE_URL={new_url}")

print("\nAfter updating, test with:")
print("   python3 test_db.py")



