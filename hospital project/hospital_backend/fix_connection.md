# Fix Database Connection Issue

## Problem
Hostname `db.lrzlkoxqwtzwmbehfngn.supabase.co` cannot be resolved.

## Solution: Get Correct Connection String from Supabase

### Method 1: Direct Connection (Port 5432)

1. Go to: https://supabase.com/dashboard/project/lrzlkoxqwtzwmbehfngn/settings/database
2. Scroll to **Connection string** section
3. Select **URI** tab (not Connection pooling)
4. Copy the connection string
5. It should look like:
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
   OR
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

### Method 2: Connection Pooling (Recommended - Port 6543)

1. Go to Supabase Dashboard → Settings → Database
2. Under **Connection string**, select **Connection pooling** tab
3. Select **Session mode**
4. Copy the connection string
5. Format will be:
   ```
   postgresql://postgres.lrzlkoxqwtzwmbehfngn:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

### Method 3: Check Your Current Connection String

The error suggests the hostname format might be wrong. Supabase might use:
- `aws-0-us-east-1.pooler.supabase.com` (pooled)
- `db.xxxxx.supabase.co` (direct)
- `xxxxx.supabase.co` (alternative)

### Steps to Fix

1. **Get the exact connection string from Supabase Dashboard**
   - Don't construct it manually
   - Copy directly from the dashboard

2. **Update your `.env` file:**
   ```env
   DATABASE_URL=postgresql://postgres.lrzlkoxqwtzwmbehfngn:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

3. **Replace `YOUR_PASSWORD` with your actual database password**

4. **Test again:**
   ```bash
   python3 debug_db.py
   ```

### Common Issues

- **Wrong hostname format**: Use the exact one from Supabase dashboard
- **Wrong port**: Direct connection uses 5432, pooled uses 6543
- **Password not replaced**: Make sure `[YOUR-PASSWORD]` is replaced
- **Network/DNS**: Check internet connection

### Quick Check

Run this to see what your current connection string looks like (password masked):
```bash
python3 check_env.py
```



