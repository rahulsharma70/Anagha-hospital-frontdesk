from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, datetime
from database import get_db
from models import AppointmentStatus
# Note: Appointment, User, Hospital SQLAlchemy models removed - using Supabase now
from schemas import AppointmentCreate, AppointmentResponse
from auth import get_current_user, get_current_doctor
from typing import List
import logging

# Import services
from services.csv_service import save_appointment_csv
from services.whatsapp_service import send_whatsapp_message_by_hospital_id
from services.message_templates import get_confirmation_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

def is_valid_time_slot(time_slot: str) -> bool:
    """Validate time slot is within allowed hours"""
    valid_slots = [
        "09:30", "10:00", "10:30", "11:00", "11:30", "12:00",
        "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
        "18:00", "18:30", "19:00", "19:30", "20:00", "20:30"
    ]
    return time_slot in valid_slots

@router.post("/book", response_model=AppointmentResponse)
def book_appointment(
    appointment: AppointmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Book an appointment (for patients and pharma professionals)"""
    # Validate time slot
    if not is_valid_time_slot(appointment.time_slot):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time slot. Must be between 9:30 AM - 3:30 PM or 6:00 PM - 8:30 PM"
        )
    
    # Check if date is in the past
    if appointment.date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book appointment for past dates"
        )
    
    # Verify doctor exists and is a doctor
    doctor = db.query(User).filter(
        and_(User.id == appointment.doctor_id, User.role == "doctor")
    ).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Check if time slot is already booked for this doctor on this date
    existing_appointment = db.query(Appointment).filter(
        and_(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.date == appointment.date,
            Appointment.time_slot == appointment.time_slot,
            Appointment.status != AppointmentStatus.CANCELLED
        )
    ).first()
    
    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time slot already booked"
        )
    
    # Get hospital (from user or doctor)
    hospital_id = current_user.hospital_id or doctor.hospital_id
    hospital = None
    if hospital_id:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    
    # Create appointment
    db_appointment = Appointment(
        user_id=current_user.id,
        doctor_id=appointment.doctor_id,
        hospital_id=hospital_id,
        date=appointment.date,
        time_slot=appointment.time_slot,
        status=AppointmentStatus.PENDING
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    # Save to CSV and send WhatsApp (background tasks)
    if hospital_id:
        # Prepare CSV data
        # Note: Specialty is not stored in User model, it's in Operation model
        # For appointments, we can leave specialty empty or get from appointment if available
        csv_data = {
            "name": current_user.name,
            "mobile": current_user.mobile,
            "date": str(appointment.date),
            "time_slot": appointment.time_slot,
            "doctor": doctor.name,
            "specialty": "",  # Specialty not stored per doctor in current model
            "followup_date": ""
        }
        
        # Save to CSV in background
        background_tasks.add_task(save_appointment_csv, hospital_id, csv_data)
        
        # Send WhatsApp confirmation if enabled
        if hospital and hospital.whatsapp_enabled == "true":
            message = get_confirmation_message(
                patient_name=current_user.name,
                doctor_name=doctor.name,
                date=str(appointment.date),
                time_slot=appointment.time_slot,
                hospital_name=hospital.name,
                specialty=None,  # Specialty not stored per doctor in current model
                custom_template=hospital.whatsapp_confirmation_template
            )
            background_tasks.add_task(
                send_whatsapp_message_by_hospital_id,
                hospital_id=hospital_id,
                mobile=current_user.mobile,
                message=message
            )
    
    # Add user and doctor names for response
    response_dict = {
        "id": db_appointment.id,
        "user_id": db_appointment.user_id,
        "doctor_id": db_appointment.doctor_id,
        "date": db_appointment.date,
        "time_slot": db_appointment.time_slot,
        "status": db_appointment.status,
        "created_at": db_appointment.created_at,
        "user_name": current_user.name,
        "doctor_name": doctor.name
    }
    return AppointmentResponse(**response_dict)

@router.get("/my-appointments", response_model=List[AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all appointments for current user"""
    appointments = db.query(Appointment).filter(
        Appointment.user_id == current_user.id
    ).order_by(Appointment.date, Appointment.time_slot).all()
    
    result = []
    for apt in appointments:
        doctor = db.query(User).filter(User.id == apt.doctor_id).first()
        response_dict = {
            "id": apt.id,
            "user_id": apt.user_id,
            "doctor_id": apt.doctor_id,
            "date": apt.date,
            "time_slot": apt.time_slot,
            "status": apt.status,
            "created_at": apt.created_at,
            "user_name": current_user.name,
            "doctor_name": doctor.name if doctor else "Unknown"
        }
        result.append(AppointmentResponse(**response_dict))
    
    return result

@router.get("/doctor-appointments", response_model=List[AppointmentResponse])
def get_doctor_appointments(
    db: Session = Depends(get_db),
    current_doctor: dict = Depends(get_current_doctor)
):
    """Get all appointments for current doctor"""
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == current_doctor.id
    ).order_by(Appointment.date, Appointment.time_slot).all()
    
    result = []
    for apt in appointments:
        user = db.query(User).filter(User.id == apt.user_id).first()
        response_dict = {
            "id": apt.id,
            "user_id": apt.user_id,
            "doctor_id": apt.doctor_id,
            "date": apt.date,
            "time_slot": apt.time_slot,
            "status": apt.status,
            "created_at": apt.created_at,
            "user_name": user.name if user else "Unknown",
            "doctor_name": current_doctor.name
        }
        result.append(AppointmentResponse(**response_dict))
    
    return result

@router.put("/{appointment_id}/confirm")
def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_doctor: dict = Depends(get_current_doctor)
):
    """Confirm an appointment (doctor only)"""
    appointment = db.query(Appointment).filter(
        and_(
            Appointment.id == appointment_id,
            Appointment.doctor_id == current_doctor.id
        )
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    appointment.status = AppointmentStatus.CONFIRMED
    db.commit()
    return {"message": "Appointment confirmed"}

@router.put("/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cancel an appointment"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Only allow cancellation by the user who booked it or the doctor
    if appointment.user_id != current_user.id and appointment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this appointment"
        )
    
    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    return {"message": "Appointment cancelled"}


@router.put("/{appointment_id}/mark-visited")
def mark_appointment_visited(
    appointment_id: int,
    followup_date: date = None,
    db: Session = Depends(get_db),
    current_doctor: dict = Depends(get_current_doctor)
):
    """Mark appointment as visited and optionally set follow-up date (doctor only)"""
    appointment = db.query(Appointment).filter(
        and_(
            Appointment.id == appointment_id,
            Appointment.doctor_id == current_doctor.id
        )
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    appointment.status = AppointmentStatus.VISITED
    appointment.visit_date = date.today()
    
    if followup_date:
        appointment.followup_date = followup_date
    
    db.commit()
    return {
        "message": "Appointment marked as visited",
        "visit_date": appointment.visit_date,
        "followup_date": appointment.followup_date
    }

@router.get("/available-slots")
def get_available_slots(
    doctor_id: int,
    appointment_date: date,
    db: Session = Depends(get_db)
):
    """Get available time slots for a doctor on a specific date"""
    # Verify doctor exists
    doctor = db.query(User).filter(
        and_(User.id == doctor_id, User.role == "doctor")
    ).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Get all time slots
    all_slots = [
        "09:30", "10:00", "10:30", "11:00", "11:30", "12:00",
        "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
        "18:00", "18:30", "19:00", "19:30", "20:00", "20:30"
    ]
    
    # Get booked appointments
    booked_appointments = db.query(Appointment).filter(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.date == appointment_date,
            Appointment.status != AppointmentStatus.CANCELLED
        )
    ).all()
    
    booked_slots = [apt.time_slot for apt in booked_appointments]
    available_slots = [slot for slot in all_slots if slot not in booked_slots]
    
    return {
        "doctor_id": doctor_id,
        "doctor_name": doctor.name,
        "date": appointment_date,
        "available_slots": available_slots,
        "booked_slots": booked_slots
    }

