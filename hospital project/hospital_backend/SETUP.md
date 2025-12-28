# Setup Guide

## Step 1: Create Virtual Environment

```bash
cd hospital_backend
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
# or
venv\Scripts\activate      # Windows
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Create .env File

Create a `.env` file in the `hospital_backend` folder with:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
SUPABASE_API_KEY=your_supabase_api_key_here
JWT_SECRET=supersecretkey
```

**Required:**
- `DATABASE_URL` - Your Supabase PostgreSQL connection string
- `SUPABASE_API_KEY` - Your Supabase API key (for REST API calls if needed)

**Optional:**
- `JWT_SECRET` - Secret key for JWT tokens (defaults to "supersecretkey")

**To get your Supabase connection string:**
1. Go to Supabase Dashboard
2. Settings → Database
3. Copy the "Connection string" under "Connection pooling"
4. Replace `[YOUR-PASSWORD]` with your database password

## Step 4: Setup Supabase Tables

1. Go to Supabase → SQL Editor
2. Copy the contents of `supabase_simple.sql` from parent directory
3. Paste and run in SQL Editor

## Step 5: Test Database Connection

```bash
python3 test_db.py
```

You should see: `✓ Database connected successfully!`

## Step 6: Run the Server

```bash
uvicorn main:app --reload
```

## Step 7: Access API

- **API**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Test DB**: http://127.0.0.1:8000/test-db

## Troubleshooting

### Database Connection Failed
- Check your `.env` file has correct `DATABASE_URL`
- Verify Supabase database is running
- Check if password in connection string is correct

### Module Not Found
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Port Already in Use
- Change port: `uvicorn main:app --reload --port 8001`

