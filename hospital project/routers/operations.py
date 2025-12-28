from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from database import get_db
from models import OperationStatus, Specialty
# Note: Operation, User SQLAlchemy models removed - using Supabase now
from schemas import OperationCreate, OperationResponse
from auth import get_current_user, get_current_doctor
from typing import List

router = APIRouter(prefix="/api/operations", tags=["operations"])

@router.post("/book", response_model=OperationResponse)
def book_operation(
    operation: OperationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Book an operation (for patients and pharma professionals)"""
    # Check if date is in the past
    if operation.date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book operation for past dates"
        )
    
    # Verify doctor exists and is a doctor
    doctor = db.query(User).filter(
        and_(User.id == operation.doctor_id, User.role == "doctor")
    ).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Create operation
    db_operation = Operation(
        patient_id=current_user.id,
        specialty=operation.specialty,
        date=operation.date,
        doctor_id=operation.doctor_id,
        status=OperationStatus.PENDING,
        notes=operation.notes
    )
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    
    # Add patient and doctor names for response
    response_dict = {
        "id": db_operation.id,
        "patient_id": db_operation.patient_id,
        "specialty": db_operation.specialty,
        "date": db_operation.date,
        "doctor_id": db_operation.doctor_id,
        "status": db_operation.status,
        "created_at": db_operation.created_at,
        "notes": db_operation.notes,
        "patient_name": current_user.name,
        "doctor_name": doctor.name
    }
    return OperationResponse(**response_dict)

@router.get("/my-operations", response_model=List[OperationResponse])
def get_my_operations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all operations for current user"""
    operations = db.query(Operation).filter(
        Operation.patient_id == current_user.id
    ).order_by(Operation.date).all()
    
    result = []
    for op in operations:
        doctor = db.query(User).filter(User.id == op.doctor_id).first()
        response_dict = {
            "id": op.id,
            "patient_id": op.patient_id,
            "specialty": op.specialty,
            "date": op.date,
            "doctor_id": op.doctor_id,
            "status": op.status,
            "created_at": op.created_at,
            "notes": op.notes,
            "patient_name": current_user.name,
            "doctor_name": doctor.name if doctor else "Unknown"
        }
        result.append(OperationResponse(**response_dict))
    
    return result

@router.get("/doctor-operations", response_model=List[OperationResponse])
def get_doctor_operations(
    db: Session = Depends(get_db),
    current_doctor: dict = Depends(get_current_doctor)
):
    """Get all operations for current doctor"""
    operations = db.query(Operation).filter(
        Operation.doctor_id == current_doctor.id
    ).order_by(Operation.date).all()
    
    result = []
    for op in operations:
        patient = db.query(User).filter(User.id == op.patient_id).first()
        response_dict = {
            "id": op.id,
            "patient_id": op.patient_id,
            "specialty": op.specialty,
            "date": op.date,
            "doctor_id": op.doctor_id,
            "status": op.status,
            "created_at": op.created_at,
            "notes": op.notes,
            "patient_name": patient.name if patient else "Unknown",
            "doctor_name": current_doctor.name
        }
        result.append(OperationResponse(**response_dict))
    
    return result

@router.put("/{operation_id}/confirm")
def confirm_operation(
    operation_id: int,
    db: Session = Depends(get_db),
    current_doctor: dict = Depends(get_current_doctor)
):
    """Confirm an operation (doctor only)"""
    operation = db.query(Operation).filter(
        and_(
            Operation.id == operation_id,
            Operation.doctor_id == current_doctor.id
        )
    ).first()
    
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operation not found"
        )
    
    operation.status = OperationStatus.CONFIRMED
    db.commit()
    return {"message": "Operation confirmed"}

@router.put("/{operation_id}/cancel")
def cancel_operation(
    operation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cancel an operation"""
    operation = db.query(Operation).filter(
        Operation.id == operation_id
    ).first()
    
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operation not found"
        )
    
    # Only allow cancellation by the patient or the doctor
    if operation.patient_id != current_user.id and operation.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this operation"
        )
    
    operation.status = OperationStatus.CANCELLED
    db.commit()
    return {"message": "Operation cancelled"}

@router.get("/by-specialty/{specialty}")
def get_operations_by_specialty(
    specialty: Specialty,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get operations filtered by specialty"""
    if current_user.role == "doctor":
        operations = db.query(Operation).filter(
            and_(
                Operation.specialty == specialty,
                Operation.doctor_id == current_user.id
            )
        ).order_by(Operation.date).all()
    else:
        operations = db.query(Operation).filter(
            and_(
                Operation.specialty == specialty,
                Operation.patient_id == current_user.id
            )
        ).order_by(Operation.date).all()
    
    result = []
    for op in operations:
        patient = db.query(User).filter(User.id == op.patient_id).first()
        doctor = db.query(User).filter(User.id == op.doctor_id).first()
        response_dict = {
            "id": op.id,
            "patient_id": op.patient_id,
            "specialty": op.specialty,
            "date": op.date,
            "doctor_id": op.doctor_id,
            "status": op.status,
            "created_at": op.created_at,
            "notes": op.notes,
            "patient_name": patient.name if patient else "Unknown",
            "doctor_name": doctor.name if doctor else "Unknown"
        }
        result.append(OperationResponse(**response_dict))
    
    return result

