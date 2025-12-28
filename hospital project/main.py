from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from database import get_supabase, init_db
from routers import users, appointments, operations, hospitals, payments, admin
from auth import get_current_user, get_password_hash
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from typing import Optional
import os
import logging
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize default doctor account on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    try:
        init_db()
        supabase = get_supabase()
        if supabase:
            try:
                # Check if any doctor exists
                result = supabase.table("users").select("id").eq("role", "doctor").limit(1).execute()
                if not result.data:
                    # Create default doctor
                    default_doctor = {
                        "name": "Dr. Admin",
                        "mobile": "9999999999",
                        "role": "doctor",
                        "password_hash": get_password_hash("admin123"),
                        "address_line1": "Hospital Main Building",
                        "is_active": True
                    }
                    supabase.table("users").insert(default_doctor).execute()
                    print("✓ Default doctor created: Mobile: 9999999999, Password: admin123")
            except Exception as e:
                print(f"Warning: Could not create default doctor: {e}")
    except Exception as e:
        print(f"Warning: Database initialization issue: {e}")
    
    # Start WhatsApp scheduler
    try:
        from services.scheduler_service import start_scheduler
        start_scheduler()
        print("✓ WhatsApp scheduler started")
    except Exception as e:
        print(f"Warning: Could not start scheduler: {e}")
    
    yield
    
    # Shutdown
    try:
        from services.scheduler_service import stop_scheduler
        stop_scheduler()
        print("✓ WhatsApp scheduler stopped")
    except Exception as e:
        print(f"Warning: Error stopping scheduler: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Hospital Booking System",
    description="Hospital appointment and operation booking system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware (for web and mobile compatibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve pricing config
from fastapi.responses import JSONResponse
import json

@app.get("/static/pricing_config.json")
async def get_pricing_config():
    """Serve pricing configuration"""
    try:
        with open("pricing_config.json", "r") as f:
            return JSONResponse(content=json.load(f))
    except FileNotFoundError:
        # Return default pricing if file doesn't exist
        default_pricing = {
            "plans": [
                {
                    "name": "Starter",
                    "price": "999",
                    "period": "month",
                    "description": "Perfect for small clinics",
                    "features": ["Up to 5 doctors", "Unlimited appointments", "Basic scheduling", "Email support"],
                    "popular": False
                },
                {
                    "name": "Professional",
                    "price": "2499",
                    "period": "month",
                    "description": "Ideal for growing practices",
                    "features": ["Up to 20 doctors", "Unlimited appointments", "Advanced scheduling", "Priority support"],
                    "popular": True
                },
                {
                    "name": "Enterprise",
                    "price": "4999",
                    "period": "month",
                    "description": "For large hospitals",
                    "features": ["Unlimited doctors", "Unlimited appointments", "Full operation management", "24/7 support"],
                    "popular": False
                }
            ],
            "annual_discount": 20,
            "currency": "INR",
            "currency_symbol": "₹"
        }
        return JSONResponse(content=default_pricing)

templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(users.router)
app.include_router(appointments.router)
app.include_router(operations.router)
app.include_router(hospitals.router)
app.include_router(payments.router)
from routers import whatsapp_logs
app.include_router(whatsapp_logs.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        supabase = get_supabase()
        if supabase:
            # Test database connection
            supabase.table("hospitals").select("id").limit(1).execute()
            return {
                "status": "ok",
                "message": "Server is running",
                "database": "connected",
                "supabase_url": config.SUPABASE_URL[:30] + "..." if config.SUPABASE_URL else None
            }
        else:
            return {
                "status": "ok",
                "message": "Server is running",
                "database": "in-memory (Supabase not configured)"
            }
    except Exception as e:
        return {
            "status": "ok",
            "message": "Server is running",
            "database": "error",
            "error": str(e)
        }

# Store session tokens (in production, use Redis or database)
user_sessions = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": None,
        "now": datetime.now,
        "timedelta": timedelta
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "user": None,
        "now": datetime.now,
        "timedelta": timedelta
    })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {
        "request": request,
        "user": None,
        "now": datetime.now,
        "timedelta": timedelta
    })

@app.get("/register-hospital", response_class=HTMLResponse)
async def register_hospital_page(request: Request):
    """Hospital registration page"""
    return templates.TemplateResponse("register_hospital.html", {
        "request": request,
        "user": None,
        "now": datetime.now,
        "timedelta": timedelta
    })

@app.get("/hospital-payment-setup", response_class=HTMLResponse)
async def hospital_payment_setup_page(
    request: Request,
    hospital_id: Optional[int] = Query(None)
):
    """Hospital payment setup page (shown after registration)"""
    return templates.TemplateResponse("hospital_payment_setup.html", {
        "request": request,
        "user": None,
        "hospital_id": hospital_id,
        "now": datetime.now,
        "timedelta": timedelta
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """User dashboard - authentication handled client-side"""
    # Allow access - authentication will be checked client-side via API calls
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": None,  # Will be loaded client-side
        "now": datetime.now,
        "timedelta": timedelta
    })

@app.get("/doctor-dashboard", response_class=HTMLResponse)
async def doctor_dashboard(request: Request):
    """Doctor dashboard - authentication handled client-side"""
    # Allow access - authentication will be checked client-side via API calls
    return templates.TemplateResponse("doctor_dashboard.html", {
        "request": request,
        "user": None,  # Will be loaded client-side
        "now": datetime.now,
        "timedelta": timedelta
    })

@app.get("/book-appointment", response_class=HTMLResponse)
async def book_appointment_page(request: Request):
    """Book appointment page - authentication handled client-side"""
    return templates.TemplateResponse("book_appointment.html", {
        "request": request,
        "user": None,  # Will be loaded client-side
        "now": datetime.now,
        "timedelta": timedelta
    })

@app.get("/book-operation", response_class=HTMLResponse)
async def book_operation_page(request: Request):
    """Book operation page - authentication handled client-side"""
    return templates.TemplateResponse("book_operation.html", {
        "request": request,
        "user": None,  # Will be loaded client-side
        "now": datetime.now,
        "timedelta": timedelta
    })

@app.get("/payment/{appointment_id}", response_class=HTMLResponse)
async def payment_page(
    appointment_id: int,
    request: Request
):
    """Payment page for appointment - authentication handled client-side"""
    return templates.TemplateResponse("payment.html", {
        "request": request,
        "user": None,  # Will be loaded client-side
        "appointment_id": appointment_id,
        "type": "appointment"
    })

@app.get("/payment-operation/{operation_id}", response_class=HTMLResponse)
async def payment_operation_page(
    operation_id: int,
    request: Request
):
    """Payment page for operation - authentication handled client-side"""
    return templates.TemplateResponse("payment.html", {
        "request": request,
        "user": None,  # Will be loaded client-side
        "operation_id": operation_id,
        "type": "operation"
    })

@app.get("/admin/pricing", response_class=HTMLResponse)
async def admin_pricing_page(
    request: Request
):
    """Admin pricing management page - authentication handled client-side"""
    return templates.TemplateResponse("admin_pricing.html", {
        "request": request,
        "user": None,  # Will be loaded client-side
        "now": datetime.now,
        "timedelta": timedelta
    })

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting Hospital Booking System Web Server")
    print("="*60)
    print(f"📁 Web Interface: http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    print(f"🔍 API Docs: http://{config.SERVER_HOST}:{config.SERVER_PORT}/docs")
    print(f"💚 Health Check: http://{config.SERVER_HOST}:{config.SERVER_PORT}/health")
    print(f"🌐 Shared Database: Supabase (same as mobile project)")
    print(f"📱 Mobile API: http://{config.SERVER_HOST}:8000")
    print("="*60)
    print("Press CTRL+C to stop the server\n")
    uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT)

