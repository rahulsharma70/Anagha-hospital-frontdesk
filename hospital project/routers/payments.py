from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import get_db
from models import PaymentStatus, PaymentMethod
# Note: Payment, Appointment, Operation, User, Hospital SQLAlchemy models removed - using Supabase now
from auth import get_current_user
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import uuid

# Try to import QR code library
try:
    import qrcode
    import io
    import base64
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

router = APIRouter(prefix="/api/payments", tags=["payments"])

class PaymentCreate(BaseModel):
    appointment_id: Optional[int] = None
    operation_id: Optional[int] = None
    amount: str = "500"

class QRGenerateRequest(BaseModel):
    upi_id: str
    amount: str = "500"
    transaction_id: Optional[str] = None

def generate_upi_qr_code(upi_id: str, amount: str, transaction_id: str) -> str:
    """Generate UPI QR code as base64 string"""
    if not QR_AVAILABLE:
        # Return placeholder if QR library not available
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjUwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iI2Y5ZmFmYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2YjcyODAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5VUEkgUVIgQ29kZTwvdGV4dD48L3N2Zz4="
    
    # UPI payment URL format
    upi_url = f"upi://pay?pa={upi_id}&am={amount}&tn=Appointment%20Payment&tr={transaction_id}"
    
    try:
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(upi_url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        # Return placeholder on error
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjUwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iI2Y5ZmFmYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2YjcyODAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5VUEkgUVIgQ29kZTwvdGV4dD48L3N2Zz4="

@router.post("/create")
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a payment request and generate UPI QR codes"""
    if not payment_data.appointment_id and not payment_data.operation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either appointment_id or operation_id is required"
        )
    
    # Get hospital
    hospital_id = None
    if payment_data.appointment_id:
        appointment = db.query(Appointment).filter(Appointment.id == payment_data.appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        if appointment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        hospital_id = appointment.hospital_id or current_user.hospital_id
    elif payment_data.operation_id:
        operation = db.query(Operation).filter(Operation.id == payment_data.operation_id).first()
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")
        if operation.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        hospital_id = operation.hospital_id or current_user.hospital_id
    
    if not hospital_id:
        raise HTTPException(status_code=400, detail="Hospital not found")
    
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Get UPI IDs for each payment app (use app-specific or fallback to default)
    gpay_upi = hospital.gpay_upi_id or hospital.upi_id or "hospital@upi"
    phonepay_upi = hospital.phonepay_upi_id or hospital.upi_id or "hospital@upi"
    paytm_upi = hospital.paytm_upi_id or hospital.upi_id or "hospital@upi"
    bhim_upi = hospital.bhim_upi_id or hospital.upi_id or "hospital@upi"
    default_upi = hospital.upi_id or "hospital@upi"
    
    # Generate transaction ID
    transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
    
    # Create payment record
    payment = Payment(
        appointment_id=payment_data.appointment_id,
        operation_id=payment_data.operation_id,
        user_id=current_user.id,
        hospital_id=hospital_id,
        amount=payment_data.amount,
        status=PaymentStatus.PENDING,
        transaction_id=transaction_id
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Generate QR codes for each UPI app using their specific UPI IDs
    qr_codes = {
        "gpay": generate_upi_qr_code(gpay_upi, payment_data.amount, transaction_id),
        "phonepay": generate_upi_qr_code(phonepay_upi, payment_data.amount, transaction_id),
        "paytm": generate_upi_qr_code(paytm_upi, payment_data.amount, transaction_id),
        "bhimupi": generate_upi_qr_code(bhim_upi, payment_data.amount, transaction_id)
    }
    
    # Generate UPI payment URLs for each app
    upi_url = f"upi://pay?pa={default_upi}&am={payment_data.amount}&tn=Appointment%20Payment&tr={transaction_id}"
    
    # Generate payment links for each UPI app using their specific UPI IDs
    payment_links = {
        "gpay": f"tez://pay?pa={gpay_upi}&am={payment_data.amount}&tn=Appointment%20Payment&tr={transaction_id}",
        "phonepay": f"phonepe://pay?pa={phonepay_upi}&am={payment_data.amount}&tn=Appointment%20Payment&tr={transaction_id}",
        "paytm": f"paytmmp://pay?pa={paytm_upi}&am={payment_data.amount}&tn=Appointment%20Payment&tr={transaction_id}",
        "bhimupi": f"upi://pay?pa={bhim_upi}&am={payment_data.amount}&tn=Appointment%20Payment&tr={transaction_id}",
        "universal": upi_url
    }
    
    return {
        "payment_id": payment.id,
        "transaction_id": transaction_id,
        "amount": payment_data.amount,
        "upi_id": upi_id,
        "upi_url": upi_url,
        "qr_codes": qr_codes,
        "payment_links": payment_links,
        "status": payment.status
    }

@router.post("/verify/{payment_id}")
def verify_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Verify payment status (manual verification)"""
    payment = db.query(Payment).filter(
        and_(Payment.id == payment_id, Payment.user_id == current_user.id)
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # In production, integrate with payment gateway webhook
    # For now, return current status
    return {
        "payment_id": payment.id,
        "status": payment.status,
        "transaction_id": payment.transaction_id,
        "amount": payment.amount
    }

@router.put("/complete/{payment_id}")
def complete_payment(
    payment_id: int,
    upi_transaction_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark payment as completed (admin/doctor function)"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment.status = PaymentStatus.COMPLETED
    payment.payment_date = datetime.utcnow()
    if upi_transaction_id:
        payment.upi_transaction_id = upi_transaction_id
    
    # Update appointment/operation status if payment completed
    if payment.appointment_id:
        appointment = db.query(Appointment).filter(Appointment.id == payment.appointment_id).first()
        if appointment:
            appointment.status = "confirmed"
    elif payment.operation_id:
        operation = db.query(Operation).filter(Operation.id == payment.operation_id).first()
        if operation:
            operation.status = "confirmed"
    
    db.commit()
    
    return {"message": "Payment marked as completed", "payment": payment}

@router.get("/my-payments")
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all payments for current user"""
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    return [{
        "id": p.id,
        "appointment_id": p.appointment_id,
        "operation_id": p.operation_id,
        "amount": p.amount,
        "status": p.status,
        "transaction_id": p.transaction_id,
        "payment_date": p.payment_date,
        "created_at": p.created_at
    } for p in payments]

class QRGenerateRequest(BaseModel):
    upi_id: str
    amount: str = "500"
    transaction_id: Optional[str] = None

@router.post("/generate-qr")
def generate_qr_code(request: QRGenerateRequest):
    """Generate QR code for homepage (public endpoint)"""
    from datetime import datetime
    if not request.transaction_id:
        request.transaction_id = f"HOME{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    qr_code = generate_upi_qr_code(request.upi_id, request.amount, request.transaction_id)
    return {
        "qr_code": qr_code,
        "upi_id": request.upi_id,
        "amount": request.amount
    }
