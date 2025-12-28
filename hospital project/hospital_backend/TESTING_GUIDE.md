# Complete Testing Guide

## Prerequisites

1. ✅ Supabase tables created (run `supabase_simple.sql`)
2. ✅ `.env` file configured with correct `DATABASE_URL`
3. ✅ Dependencies installed (`pip install -r requirements.txt`)
4. ✅ Server running (`uvicorn main:app --reload`)

## Quick Test Flow

### Step 1: Start the Server

```bash
cd hospital_backend
source venv/bin/activate  # If using virtual environment
uvicorn main:app --reload
```

Server should start at: http://127.0.0.1:8000

### Step 2: Test Database Connection

```bash
# In a new terminal
cd hospital_backend
python3 test_db.py
```

Expected output:
```
✓ Database connected successfully!
✓ SUPABASE_API_KEY is configured
```

### Step 3: Run Complete Flow Test

```bash
python3 test_complete_flow.py
```

This will test:
1. ✅ Health check
2. ✅ Database connection
3. ✅ Hospital registration
4. ✅ Hospital approval
5. ✅ User registration (patient, pharma, doctor)
6. ✅ User login
7. ✅ Appointment booking
8. ✅ Operation booking
9. ✅ Get appointments

## Manual Testing via API Docs

### Access Interactive API Docs

Open in browser: http://127.0.0.1:8000/docs

### Test Flow (Step by Step)

#### 1. Register Hospital
- Endpoint: `POST /api/hospitals/register`
- Body:
```json
{
  "name": "Test Hospital",
  "email": "test@hospital.com",
  "mobile": "9876543210",
  "address_line1": "123 Test St",
  "city": "Test City",
  "state": "Test State"
}
```
- Note the `id` from response

#### 2. Approve Hospital (Admin)
- Endpoint: `PUT /api/hospitals/{id}/approve`
- Replace `{id}` with hospital ID from step 1

#### 3. Register Patient
- Endpoint: `POST /api/users/register`
- Body:
```json
{
  "name": "Test Patient",
  "mobile": "9876543211",
  "role": "patient",
  "password": "test123",
  "hospital_id": 1,
  "address_line1": "Test Address"
}
```

#### 4. Register Doctor
- Endpoint: `POST /api/users/register`
- Body:
```json
{
  "name": "Dr. Test",
  "mobile": "9876543212",
  "role": "doctor",
  "password": "test123",
  "hospital_id": 1,
  "degree": "MBBS",
  "institute_name": "Test Medical College",
  "experience1": "5 years experience"
}
```

#### 5. Login as Patient
- Endpoint: `POST /api/users/login`
- Body:
```json
{
  "mobile": "9876543211",
  "password": "test123"
}
```
- Copy the `access_token` from response

#### 6. Book Appointment
- Endpoint: `POST /api/appointments/book`
- Headers: `Authorization: Bearer {token}`
- Body:
```json
{
  "doctor_id": 2,
  "date": "2024-12-26",
  "time_slot": "10:00"
}
```

#### 7. Get My Appointments
- Endpoint: `GET /api/appointments/my-appointments`
- Headers: `Authorization: Bearer {token}`

## Testing Checklist

- [ ] Server starts without errors
- [ ] Database connection successful
- [ ] Health endpoint returns 200
- [ ] Hospital registration works
- [ ] Hospital approval works
- [ ] Patient registration works
- [ ] Pharma registration works (with company name)
- [ ] Doctor registration works (with degree/institute)
- [ ] User login returns JWT token
- [ ] Appointment booking works
- [ ] Operation booking works
- [ ] Get appointments returns data
- [ ] CORS headers present (for Flutter/Web)

## Common Issues

### Database Connection Failed
- Check `.env` file has correct `DATABASE_URL`
- Verify Supabase database is running
- Test with: `python3 test_db.py`

### 401 Unauthorized
- Token expired or invalid
- Login again to get new token
- Check Authorization header format: `Bearer {token}`

### 404 Not Found
- Check endpoint URL is correct
- Verify server is running
- Check API base path: `/api/...`

### 500 Internal Server Error
- Check server logs
- Verify database tables exist
- Check Supabase connection

## Next Steps After Testing

Once all tests pass:
1. ✅ Backend is ready
2. ✅ Can connect Flutter app
3. ✅ Can connect Web frontend
4. ✅ Ready for deployment



