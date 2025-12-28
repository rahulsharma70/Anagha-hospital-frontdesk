from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from models import HospitalStatus
# Note: Hospital SQLAlchemy model removed - using Supabase now
from schemas import HospitalCreate, HospitalResponse
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from services.whatsapp_service import open_whatsapp_session, get_whatsapp_driver, check_whatsapp_session_health, close_whatsapp_session

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])

# Email configuration
ADMIN_EMAIL = "info@uabiotech.in"
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def send_hospital_registration_email(hospital_data: dict):
    """Send email to admin for hospital registration approval"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER if SMTP_USER else "noreply@hospitalbooking.com"
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"New Hospital Registration Request: {hospital_data['name']}"
        
        # Create email body
        body = f"""
        New Hospital Registration Request
        
        Hospital Details:
        -----------------
        Name: {hospital_data['name']}
        Email: {hospital_data['email']}
        Mobile: {hospital_data['mobile']}
        Address Line 1: {hospital_data.get('address_line1', 'N/A')}
        Address Line 2: {hospital_data.get('address_line2', 'N/A')}
        Address Line 3: {hospital_data.get('address_line3', 'N/A')}
        City: {hospital_data.get('city', 'N/A')}
        State: {hospital_data.get('state', 'N/A')}
        Pincode: {hospital_data.get('pincode', 'N/A')}
        
        Payment UPI IDs:
        ----------------
        Default UPI ID: {hospital_data.get('upi_id', 'N/A')}
        Google Pay: {hospital_data.get('gpay_upi_id', 'N/A')}
        PhonePe: {hospital_data.get('phonepay_upi_id', 'N/A')}
        Paytm: {hospital_data.get('paytm_upi_id', 'N/A')}
        BHIM UPI: {hospital_data.get('bhim_upi_id', 'N/A')}
        
        Registration Date: {hospital_data.get('registration_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
        Hospital ID: {hospital_data.get('id', 'N/A')}
        
        Please review and approve/reject this registration.
        
        To approve, use the hospital ID: {hospital_data.get('id', 'N/A')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        if SMTP_USER and SMTP_PASSWORD:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"✓ Email sent to {ADMIN_EMAIL} for hospital registration")
        else:
            # If SMTP not configured, just print (for development)
            print(f"\n{'='*60}")
            print("HOSPITAL REGISTRATION REQUEST")
            print(f"{'='*60}")
            print(body)
            print(f"{'='*60}\n")
            print(f"NOTE: Configure SMTP settings to send emails to {ADMIN_EMAIL}")
            
    except Exception as e:
        print(f"Error sending email: {e}")
        # Don't fail registration if email fails

@router.post("/register", response_model=HospitalResponse)
def register_hospital(
    hospital: HospitalCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new hospital (requires admin approval)"""
    # Check if email already exists
    existing_hospital = db.query(Hospital).filter(Hospital.email == hospital.email).first()
    if existing_hospital:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital with this email already registered"
        )
    
    # Create hospital
    db_hospital = Hospital(
        name=hospital.name,
        email=hospital.email,
        mobile=hospital.mobile,
        address_line1=hospital.address_line1,
        address_line2=hospital.address_line2,
        address_line3=hospital.address_line3,
        city=hospital.city,
        state=hospital.state,
        pincode=hospital.pincode,
        status=HospitalStatus.PENDING,
        # UPI IDs
        upi_id=hospital.upi_id,
        gpay_upi_id=hospital.gpay_upi_id,
        phonepay_upi_id=hospital.phonepay_upi_id,
        paytm_upi_id=hospital.paytm_upi_id,
        bhim_upi_id=hospital.bhim_upi_id
    )
    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)
    
    # Send email notification in background
    hospital_data = {
        "id": db_hospital.id,
        "name": db_hospital.name,
        "email": db_hospital.email,
        "mobile": db_hospital.mobile,
        "address_line1": db_hospital.address_line1,
        "address_line2": db_hospital.address_line2,
        "address_line3": db_hospital.address_line3,
        "city": db_hospital.city,
        "state": db_hospital.state,
        "pincode": db_hospital.pincode,
        "upi_id": db_hospital.upi_id,
        "gpay_upi_id": db_hospital.gpay_upi_id,
        "phonepay_upi_id": db_hospital.phonepay_upi_id,
        "paytm_upi_id": db_hospital.paytm_upi_id,
        "bhim_upi_id": db_hospital.bhim_upi_id,
        "registration_date": db_hospital.registration_date.strftime('%Y-%m-%d %H:%M:%S') if db_hospital.registration_date else None
    }
    background_tasks.add_task(send_hospital_registration_email, hospital_data)
    
    return db_hospital

@router.get("/payment-info")
def get_hospital_payment_info(
    hospital_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get hospital payment UPI IDs for homepage (public endpoint)"""
    if hospital_id:
        hospital = db.query(Hospital).filter(
            and_(Hospital.id == hospital_id, Hospital.status == HospitalStatus.APPROVED)
        ).first()
    else:
        # Get first approved hospital as default
        hospital = db.query(Hospital).filter(
            Hospital.status == HospitalStatus.APPROVED
        ).first()
    
    if not hospital:
        # Return default values if no hospital found
        return {
            "upi_id": "hospital@upi",
            "gpay_upi_id": "hospital@upi",
            "phonepay_upi_id": "hospital@upi",
            "paytm_upi_id": "hospital@upi",
            "bhim_upi_id": "hospital@upi"
        }
    
    default_upi = hospital.upi_id or "hospital@upi"
    return {
        "upi_id": default_upi,
        "gpay_upi_id": hospital.gpay_upi_id or default_upi,
        "phonepay_upi_id": hospital.phonepay_upi_id or default_upi,
        "paytm_upi_id": hospital.paytm_upi_id or default_upi,
        "bhim_upi_id": hospital.bhim_upi_id or default_upi
    }

@router.get("/", response_model=List[HospitalResponse])
def get_hospitals(
    status_filter: Optional[HospitalStatus] = None,
    db: Session = Depends(get_db)
):
    """Get list of hospitals (filtered by status if provided)"""
    query = db.query(Hospital)
    if status_filter:
        query = query.filter(Hospital.status == status_filter)
    hospitals = query.order_by(Hospital.registration_date.desc()).all()
    return hospitals

@router.get("/approved", response_model=List[HospitalResponse])
def get_approved_hospitals(db: Session = Depends(get_db)):
    """Get list of approved hospitals"""
    hospitals = db.query(Hospital).filter(
        Hospital.status == HospitalStatus.APPROVED
    ).order_by(Hospital.name).all()
    return hospitals

@router.put("/{hospital_id}/approve")
def approve_hospital(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Approve a hospital registration (admin function)"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    hospital.status = HospitalStatus.APPROVED
    hospital.approved_date = datetime.utcnow()
    db.commit()
    
    return {"message": "Hospital approved successfully", "hospital": hospital}

@router.put("/{hospital_id}/reject")
def reject_hospital(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Reject a hospital registration (admin function)"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    hospital.status = HospitalStatus.REJECTED
    db.commit()
    
    return {"message": "Hospital rejected", "hospital": hospital}


# WhatsApp Admin Endpoints

class WhatsAppSettingsUpdate(BaseModel):
    whatsapp_enabled: Optional[str] = None
    whatsapp_confirmation_template: Optional[str] = None
    whatsapp_followup_template: Optional[str] = None
    whatsapp_reminder_template: Optional[str] = None


@router.put("/{hospital_id}/whatsapp-settings")
def update_whatsapp_settings(
    hospital_id: int,
    settings: WhatsAppSettingsUpdate,
    db: Session = Depends(get_db)
):
    """Update WhatsApp settings for a hospital (admin function)"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    if settings.whatsapp_enabled is not None:
        hospital.whatsapp_enabled = settings.whatsapp_enabled
    if settings.whatsapp_confirmation_template is not None:
        hospital.whatsapp_confirmation_template = settings.whatsapp_confirmation_template
    if settings.whatsapp_followup_template is not None:
        hospital.whatsapp_followup_template = settings.whatsapp_followup_template
    if settings.whatsapp_reminder_template is not None:
        hospital.whatsapp_reminder_template = settings.whatsapp_reminder_template
    
    db.commit()
    db.refresh(hospital)
    
    return {
        "message": "WhatsApp settings updated",
        "whatsapp_enabled": hospital.whatsapp_enabled,
        "whatsapp_confirmation_template": hospital.whatsapp_confirmation_template,
        "whatsapp_followup_template": hospital.whatsapp_followup_template,
        "whatsapp_reminder_template": hospital.whatsapp_reminder_template
    }


@router.get("/{hospital_id}/whatsapp-status")
def get_whatsapp_status(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Check WhatsApp session status for a hospital"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    is_healthy = check_whatsapp_session_health(hospital_id)
    
    return {
        "hospital_id": hospital_id,
        "whatsapp_enabled": hospital.whatsapp_enabled == "true",
        "session_active": is_healthy,
        "message": "Session active" if is_healthy else "Session expired or not initialized"
    }


@router.post("/{hospital_id}/whatsapp-init")
def initialize_whatsapp_session(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Initialize WhatsApp Web session for a hospital (opens browser for QR scan)"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    # Enable WhatsApp if not already enabled
    if hospital.whatsapp_enabled != "true":
        hospital.whatsapp_enabled = "true"
        db.commit()
    
    # Initialize driver (will open browser for QR scan)
    # Hospital admin scans QR once only. Session remains logged in.
    driver = open_whatsapp_session(hospital_id)
    
    if driver:
        return {
            "message": "WhatsApp session initialization started. Please scan QR code in the browser window.",
            "status": "initializing"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize WhatsApp session"
        )


@router.post("/{hospital_id}/whatsapp-close")
def close_whatsapp_session_endpoint(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Close WhatsApp session for a hospital"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    close_whatsapp_session(hospital_id)
    
    return {
        "message": "WhatsApp session closed successfully",
        "hospital_id": hospital_id
    }

