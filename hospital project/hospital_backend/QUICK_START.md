# Quick Start - Testing Complete Flow

## 🚀 Step-by-Step Testing

### 1. Install Dependencies (if not done)

```bash
cd hospital_backend
pip install -r requirements.txt
```

### 2. Verify Environment

```bash
python3 check_env.py
```

Should show:
- ✓ DATABASE_URL: Set
- ✓ SUPABASE_API_KEY: Set

### 3. Test Database Connection

```bash
python3 test_db.py
```

Should show:
- ✓ Database connected successfully!

### 4. Start the Server

```bash
uvicorn main:app --reload
```

Server starts at: **http://127.0.0.1:8000**

### 5. Quick Test (in new terminal)

```bash
# Option A: Quick bash test
./quick_test.sh

# Option B: Python complete flow test
python3 test_complete_flow.py
```

### 6. Interactive API Testing

Open in browser: **http://127.0.0.1:8000/docs**

This gives you a visual interface to test all endpoints!

## 📋 Testing Checklist

- [ ] Server starts: `uvicorn main:app --reload`
- [ ] Health check: http://127.0.0.1:8000/health
- [ ] Database test: http://127.0.0.1:8000/test-db
- [ ] API docs: http://127.0.0.1:8000/docs
- [ ] Run complete flow: `python3 test_complete_flow.py`

## 🎯 What Gets Tested

The `test_complete_flow.py` script tests:

1. ✅ Server health
2. ✅ Database connection
3. ✅ Hospital registration
4. ✅ Hospital approval
5. ✅ Patient registration
6. ✅ Pharma registration
7. ✅ Doctor registration
8. ✅ User login (JWT token)
9. ✅ Appointment booking
10. ✅ Operation booking
11. ✅ Get appointments

## 📝 Note

**Important**: Make sure you've:
1. ✅ Created tables in Supabase (run `supabase_simple.sql`)
2. ✅ Updated `.env` with correct `DATABASE_URL`
3. ✅ Server is running before running tests

## 🔗 Useful Links

- API Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health
- Test DB: http://127.0.0.1:8000/test-db
- Config: http://127.0.0.1:8000/config



