"""
WhatsApp Message Logs API
Provides endpoints to view message logs and statistics
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
# Note: Hospital SQLAlchemy model removed - using Supabase now
from services.message_logger import get_message_logs
from typing import Optional, List
from datetime import date

router = APIRouter(prefix="/api/whatsapp-logs", tags=["whatsapp-logs"])


@router.get("/{hospital_id}")
def get_hospital_message_logs(
    hospital_id: int,
    log_date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    status_filter: Optional[str] = Query(None, description="Filter by status: 'success' or 'failed'"),
    db: Session = Depends(get_db)
):
    """
    Get WhatsApp message logs for a hospital.
    
    Features:
    - View all sent messages
    - Filter by date
    - Filter by status (success/failed)
    - View retry attempts
    """
    # Verify hospital exists
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    # Get logs
    logs = get_message_logs(hospital_id, date=log_date, status=status_filter)
    
    # Calculate statistics
    total = len(logs)
    successful = len([l for l in logs if l.get("status") == "success"])
    failed = len([l for l in logs if l.get("status") == "failed"])
    
    return {
        "hospital_id": hospital_id,
        "hospital_name": hospital.name,
        "date": log_date or date.today().isoformat(),
        "statistics": {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round((successful / total * 100) if total > 0 else 0, 2)
        },
        "logs": logs
    }


@router.get("/{hospital_id}/failed")
def get_failed_messages(
    hospital_id: int,
    log_date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get failed WhatsApp messages for a hospital.
    Useful for retry mechanism.
    """
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    failed_logs = get_message_logs(hospital_id, date=log_date, status="failed")
    
    return {
        "hospital_id": hospital_id,
        "failed_count": len(failed_logs),
        "failed_messages": failed_logs
    }



