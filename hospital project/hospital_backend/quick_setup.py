"""
Quick setup helper for Supabase connection
This will help you construct the correct DATABASE_URL
"""
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_REF = "lrzlkoxqwtzwmbehfngn"

print("=" * 70)
print("Supabase Connection String Helper")
print("=" * 70)
print(f"\nYour Supabase Project: {PROJECT_REF}")
print(f"Dashboard URL: https://supabase.com/dashboard/project/{PROJECT_REF}\n")

print("=" * 70)
print("Option 1: Direct Connection (Port 5432)")
print("=" * 70)
print(f"postgresql://postgres:YOUR_PASSWORD@db.{PROJECT_REF}.supabase.co:5432/postgres\n")

print("=" * 70)
print("Option 2: Connection Pooling (Port 6543 - Recommended)")
print("=" * 70)
print("Note: Check your Supabase dashboard for the correct pooler URL")
print("Format: postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres")
print("Example: postgresql://postgres.lrzlkoxqwtzwmbehfngn:PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres\n")

print("=" * 70)
print("Steps to Get Your Password:")
print("=" * 70)
print("1. Go to: https://supabase.com/dashboard/project/lrzlkoxqwtzwmbehfngn")
print("2. Settings → Database")
print("3. Find 'Database password' section")
print("4. If you don't know it, click 'Reset database password'")
print("5. Copy the password\n")

print("=" * 70)
print("Update Your .env File:")
print("=" * 70)
print("DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.lrzlkoxqwtzwmbehfngn.supabase.co:5432/postgres")
print("SUPABASE_API_KEY=your_existing_api_key\n")

print("=" * 70)
print("After updating .env, test with:")
print("=" * 70)
print("python3 check_env.py")
print("python3 test_db.py")
print("=" * 70)

