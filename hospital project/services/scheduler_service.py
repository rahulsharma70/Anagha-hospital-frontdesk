"""
Background Scheduler Service for Follow-ups and Reminders
Uses APScheduler to send automated WhatsApp messages

Two Types of Messages:
1. Follow-up reminder
2. Upcoming appointment reminder
"""
import logging
from datetime import date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import SessionLocal
from models import AppointmentStatus
# Note: Appointment, Hospital, User SQLAlchemy models removed - using Supabase now
from services.whatsapp_service import send_whatsapp_message_by_hospital_id, check_whatsapp_session_health, get_whatsapp_driver
from services.message_templates import get_followup_message, get_reminder_message

logger = logging.getLogger(__name__)

# APScheduler background scheduler
scheduler = BackgroundScheduler()

def get_db_session():
    """Get database session for scheduler tasks."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def get_followups_due(today: date):
    """
    Get all follow-ups due today.
    Returns appointments with status='visited' and followup_date=today.
    """
    db = get_db_session()
    try:
        appointments = db.query(Appointment).filter(
            and_(
                Appointment.status == AppointmentStatus.VISITED,
                Appointment.followup_date == today,
                Appointment.hospital_id.isnot(None)
            )
        ).all()
        
        followups = []
        for appointment in appointments:
            hospital = db.query(Hospital).filter(Hospital.id == appointment.hospital_id).first()
            patient = db.query(User).filter(User.id == appointment.user_id).first()
            doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
            
            if hospital and patient and doctor:
                followups.append({
                    'name': patient.name,
                    'mobile': patient.mobile,
                    'doctor': doctor.name,
                    'followup_date': appointment.followup_date,
                    'hospital': hospital.name,
                    'hospital_id': appointment.hospital_id,
                    'appointment_id': appointment.id
                })
        
        return followups
    finally:
        db.close()


def send_followup_reminders():
    """
    Send follow-up reminders for appointments marked as visited.
    Runs daily via APScheduler.
    """
    today = date.today()
    followups = get_followups_due(today)
    
    for f in followups:
        # Get driver for hospital
        driver = get_whatsapp_driver(f['hospital_id'])
        if not driver:
            logger.warning(f"WhatsApp session not available for hospital {f['hospital_id']}")
            continue
        
        # Check if WhatsApp is enabled for hospital
        db = get_db_session()
        try:
            hospital = db.query(Hospital).filter(Hospital.id == f['hospital_id']).first()
            if not hospital or hospital.whatsapp_enabled != "true":
                continue
        finally:
            db.close()
        
        # Generate message
        msg = f"""Hello {f['name']},
This is a reminder for your follow-up visit with {f['doctor']}.
📅 Date: {f['followup_date'].strftime('%d %b %Y')}
– {f['hospital']}"""
        
        # Send WhatsApp message
        from services.whatsapp_service import send_whatsapp_message
        success = send_whatsapp_message(driver, f['mobile'], msg, hospital_id=f['hospital_id'])
        
        if success:
            logger.info(f"Follow-up reminder sent to {f['mobile']} for appointment {f['appointment_id']}")
        else:
            logger.error(f"Failed to send follow-up reminder to {f['mobile']}")


def send_appointment_reminders():
    """
    Send reminders for upcoming appointments (1 day before).
    Runs daily via APScheduler.
    """
    tomorrow = date.today() + timedelta(days=1)
    upcoming = get_upcoming_appointments(tomorrow)
    
    for apt in upcoming:
        # Get driver for hospital
        driver = get_whatsapp_driver(apt['hospital_id'])
        if not driver:
            logger.warning(f"WhatsApp session not available for hospital {apt['hospital_id']}")
            continue
        
        # Check if WhatsApp is enabled for hospital
        db = get_db_session()
        try:
            hospital = db.query(Hospital).filter(Hospital.id == apt['hospital_id']).first()
            if not hospital or hospital.whatsapp_enabled != "true":
                continue
        finally:
            db.close()
        
        # Format time
        from services.message_templates import format_time
        time_formatted = format_time(apt['time_slot'])
        
        # Generate message
        msg = f"""Hello {apt['name']},
Reminder: Your appointment with {apt['doctor']} is scheduled for:
🗓 Date: {apt['date'].strftime('%d %b %Y')}
⏰ Time: {time_formatted}
Please arrive on time.
– {apt['hospital']}"""
        
        # Send WhatsApp message
        from services.whatsapp_service import send_whatsapp_message
        success = send_whatsapp_message(driver, apt['mobile'], msg, hospital_id=apt['hospital_id'])
        
        if success:
            logger.info(f"Appointment reminder sent to {apt['mobile']} for appointment {apt['appointment_id']}")
        else:
            logger.error(f"Failed to send appointment reminder to {apt['mobile']}")


def start_scheduler():
    """
    Start the background scheduler.
    Schedules follow-up reminders and appointment reminders to run daily.
    """
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return
    
    # Schedule follow-up reminders - runs daily (interval, hours=24)
    scheduler.add_job(
        send_followup_reminders,
        'interval',
        hours=24,
        id='followup_reminders',
        replace_existing=True
    )
    
    # Schedule appointment reminders - runs daily (interval, hours=24)
    scheduler.add_job(
        send_appointment_reminders,
        'interval',
        hours=24,
        id='appointment_reminders',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("APScheduler background scheduler started")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")

