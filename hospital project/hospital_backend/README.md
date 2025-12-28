# Hospital SaaS Backend

FastAPI backend for Hospital Booking System with Supabase PostgreSQL.

## 🚀 Quick Setup

### 1. Create Virtual Environment

```bash
cd hospital_backend
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Supabase Database

1. Go to Supabase → SQL Editor
2. Copy and paste `supabase_simple.sql` from parent directory
3. Run the SQL to create tables

### 4. Configure Environment

Your Supabase project: `lrzlkoxqwtzwmbehfngn`

Create `.env` file with:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.lrzlkoxqwtzwmbehfngn.supabase.co:5432/postgres
SUPABASE_API_KEY=your_supabase_api_key
JWT_SECRET=your-secret-key-here
```

**To get your database password:**
1. Go to: https://supabase.com/dashboard/project/lrzlkoxqwtzwmbehfngn
2. Settings → Database
3. Find "Database password" or reset it if needed

**Quick helper:**
```bash
python3 quick_setup.py  # Shows connection string format
```

### 5. Test Database Connection

```bash
python3 -c "from database import test_connection; test_connection()"
```

### 6. Run the Server

```bash
uvicorn main:app --reload
```

### 7. Access API

- **API**: http://127.0.0.1:8000
- **Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Test DB**: http://127.0.0.1:8000/test-db

## 📁 Project Structure

```
hospital_backend/
├── main.py              # FastAPI app
├── database.py          # Database connection
├── requirements.txt     # Dependencies
├── .env                 # Environment variables (create from .env.example)
└── README.md           # This file
```

## 🔐 Security Notes

- Never commit `.env` file to git
- Use strong JWT_SECRET in production
- Enable CORS only for your frontend domains in production
- Use environment variables for all secrets

## 🚢 Deployment

### Railway.app (Recommended)

1. Push code to GitHub
2. Connect Railway to your repo
3. Add environment variables in Railway dashboard
4. Deploy!

### Render.com

1. Connect GitHub repo
2. Add environment variables
3. Deploy

## 📱 Next Steps

- [ ] Add authentication endpoints
- [ ] Add OTP service integration
- [ ] Add appointment booking logic
- [ ] Add hospital-level filtering
- [ ] Add JWT token generation
