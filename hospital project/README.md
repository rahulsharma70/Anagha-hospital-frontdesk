# Hospital Booking System

A comprehensive hospital management system for booking appointments and operations, designed for patients, pharma professionals, and doctors.

## Features

### 👤 User Roles
- **Patient**: Book appointments and operations
- **Pharma Professional**: Book appointments and operations on behalf of patients
- **Doctor**: View and manage appointments/operations (restricted access)

### 📅 Appointment Booking
- Flexible time slots:
  - **Morning**: 9:30 AM - 3:30 PM
  - **Evening**: 6:00 PM - 8:30 PM
- Real-time availability checking
- Doctor selection
- Appointment confirmation/cancellation

### 🏥 Operation Booking
- Multiple specialties:
  - Ortho
  - Gyn
  - Surgery
- Doctor assignment
- Status tracking (Pending/Confirmed/Cancelled)

### 🔒 Security Features
- JWT-based authentication
- Role-based access control
- Doctor-only registration (pre-registered doctors only)
- Secure password hashing

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup Steps

1. **Clone or navigate to the project directory**
```bash
cd "/Users/rahulsharma/Desktop/hospital project"
```

2. **Create a virtual environment (recommended)**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

5. **Access the application**
- Open your browser and navigate to: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

## Default Credentials

A default doctor account is automatically created on first run:
- **Mobile**: 9999999999
- **Password**: admin123

## Database

The application uses SQLite by default (for easy setup). The database file `hospital.db` will be created automatically.

To use PostgreSQL instead:
1. Update `DATABASE_URL` in `database.py`
2. Install PostgreSQL and create a database
3. Update the connection string: `postgresql://user:password@localhost/hospital`

## Project Structure

```
hospital_app/
├── main.py                 # FastAPI application entry point
├── database.py            # Database configuration
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── auth.py                # Authentication utilities
├── routers/
│   ├── users.py          # User management endpoints
│   ├── appointments.py   # Appointment endpoints
│   └── operations.py     # Operation endpoints
├── templates/            # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── doctor_dashboard.html
│   ├── book_appointment.html
│   └── book_operation.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── requirements.txt      # Python dependencies
```

## API Endpoints

### Authentication
- `POST /api/users/register` - Register new user (patient/pharma)
- `POST /api/users/login` - Login user
- `GET /api/users/me` - Get current user info
- `GET /api/users/doctors` - Get list of doctors

### Appointments
- `POST /api/appointments/book` - Book appointment
- `GET /api/appointments/my-appointments` - Get user's appointments
- `GET /api/appointments/doctor-appointments` - Get doctor's appointments
- `GET /api/appointments/available-slots` - Get available time slots
- `PUT /api/appointments/{id}/confirm` - Confirm appointment (doctor only)
- `PUT /api/appointments/{id}/cancel` - Cancel appointment

### Operations
- `POST /api/operations/book` - Book operation
- `GET /api/operations/my-operations` - Get user's operations
- `GET /api/operations/doctor-operations` - Get doctor's operations
- `PUT /api/operations/{id}/confirm` - Confirm operation (doctor only)
- `PUT /api/operations/{id}/cancel` - Cancel operation

## Usage

### For Patients/Pharma Professionals

1. **Register**: Create an account at `/register`
2. **Login**: Login at `/login`
3. **Book Appointment**: 
   - Select a doctor
   - Choose date and time slot
   - Confirm booking
4. **Book Operation**:
   - Select specialty (Ortho/Gyn/Surgery)
   - Choose doctor and date
   - Add notes if needed

### For Doctors

1. **Login**: Use pre-registered credentials
2. **View Dashboard**: See all appointments and operations
3. **Confirm/Cancel**: Manage appointment and operation statuses
4. **Register New Doctors**: Only existing doctors can register new doctors

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables
- `DATABASE_URL`: Database connection string (default: SQLite)
- `SECRET_KEY`: JWT secret key (change in production)

## Production Deployment

1. Set a strong `SECRET_KEY` in environment variables
2. Use PostgreSQL for database
3. Configure proper CORS settings
4. Use a production WSGI server (e.g., Gunicorn)
5. Set up SSL/HTTPS
6. Configure proper logging

## Next Steps: Mobile Application

The website backend is ready. The next phase is to develop the Android mobile application that will:
- Connect to the same API endpoints
- Provide native mobile experience
- Be deployable to Google Play Store
- Support all features available on the website

## License

This project is for educational and commercial use.

## Support

For issues or questions, please contact the development team.

