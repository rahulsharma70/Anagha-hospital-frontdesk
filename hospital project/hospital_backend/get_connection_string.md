# How to Get Your Supabase PostgreSQL Connection String

Your Supabase project: `lrzlkoxqwtzwmbehfngn`

## Method 1: From Supabase Dashboard (Recommended)

1. Go to: https://supabase.com/dashboard/project/lrzlkoxqwtzwmbehfngn
2. Click **Settings** (gear icon) in the left sidebar
3. Click **Database** in the settings menu
4. Scroll down to **Connection string** section
5. Select **URI** tab (not Connection pooling)
6. Copy the connection string
7. Replace `[YOUR-PASSWORD]` with your database password

## Method 2: Construct Manually

Based on your project reference, your connection string should be:

```
postgresql://postgres:YOUR_PASSWORD@db.lrzlkoxqwtzwmbehfngn.supabase.co:5432/postgres
```

**Steps:**
1. Replace `YOUR_PASSWORD` with your actual database password
2. If you don't know your password:
   - Go to Supabase Dashboard → Settings → Database
   - Click "Reset database password" if needed
   - Or check your project settings

## Method 3: Connection Pooling (Better for Production)

For better performance, use the pooled connection:

```
postgresql://postgres.lrzlkoxqwtzwmbehfngn:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

(Region might be different - check your Supabase dashboard)

## Update Your .env File

Once you have the connection string, update your `.env` file:

```env
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@db.lrzlkoxqwtzwmbehfngn.supabase.co:5432/postgres
SUPABASE_API_KEY=your_existing_api_key
```

## Test Connection

After updating, run:
```bash
python3 check_env.py
python3 test_db.py
```

