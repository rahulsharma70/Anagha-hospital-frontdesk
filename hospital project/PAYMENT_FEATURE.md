# Payment Feature Documentation

## Overview
The payment system has been integrated into the hospital booking system with UPI QR code support for multiple payment apps.

## Features
- ✅ UPI Payment Integration (GPay, PhonePe, Paytm, BHIM UPI)
- ✅ QR Code Generation for each UPI app
- ✅ Payment tracking and verification
- ✅ Automatic redirect to payment page after booking
- ✅ Payment status management

## Database Changes

### New Table: `payments`
- Tracks all payment transactions
- Links to appointments and operations
- Stores transaction IDs and payment status

### Updated Tables
- `hospital`: Added `upi_id` column for hospital UPI ID
- `appointment`: Added `amount` and `payment_required` columns
- `operation`: Added `amount` and `payment_required` columns

## Setup Instructions

### 1. Update Database Schema
Run the SQL script in `payment_schema.sql` in your Supabase SQL Editor:
```sql
-- This will add payment tables and columns
```

### 2. Configure Hospital UPI ID
Update the `upi_id` field in the `hospital` table with your actual UPI ID:
```sql
UPDATE hospital SET upi_id = 'your-hospital@upi' WHERE id = 1;
```

### 3. Install Dependencies
The following packages have been added to `requirements.txt`:
- `qrcode[pil]==7.4.2`
- `pillow==10.1.0`

Install them:
```bash
pip install -r requirements.txt
```

## Payment Flow

### For Appointments:
1. User books an appointment
2. System redirects to `/payment/{appointment_id}`
3. User selects UPI app (GPay, PhonePe, Paytm, or BHIM)
4. QR code is displayed
5. User scans QR code and completes payment
6. User clicks "I've Paid" to verify payment
7. Payment status is updated

### For Operations:
1. User books an operation
2. System redirects to `/payment-operation/{operation_id}`
3. Same payment flow as appointments

## API Endpoints

### POST `/api/payments/create`
Create a payment request and generate QR codes.

**Request Body:**
```json
{
  "appointment_id": 1,  // or operation_id
  "operation_id": null,
  "amount": "500"
}
```

**Response:**
```json
{
  "payment_id": 1,
  "transaction_id": "TXN20240101120000ABC123",
  "amount": "500",
  "upi_id": "hospital@upi",
  "qr_codes": {
    "gpay": "data:image/png;base64,...",
    "phonepay": "data:image/png;base64,...",
    "paytm": "data:image/png;base64,...",
    "bhimupi": "data:image/png;base64,..."
  },
  "status": "pending"
}
```

### POST `/api/payments/verify/{payment_id}`
Verify payment status.

### PUT `/api/payments/complete/{payment_id}`
Mark payment as completed (admin/doctor function).

### GET `/api/payments/my-payments`
Get all payments for current user.

## Frontend Pages

### Payment Page (`/payment/{appointment_id}`)
- Displays amount and transaction ID
- Shows 4 UPI app options
- Generates QR code when app is selected
- "I've Paid" button for verification
- "Pay Later" option to skip payment

## UPI QR Code Format
The QR codes use the standard UPI payment URL format:
```
upi://pay?pa={upi_id}&am={amount}&tn=Appointment%20Payment&tr={transaction_id}
```

## Configuration

### Default Amount
Currently set to ₹500. To change:
1. Update the default in `routers/payments.py` (PaymentCreate model)
2. Or make it configurable per hospital/appointment type

### Hospital UPI ID
Each hospital can have its own UPI ID. Set it in the `hospital` table:
```sql
UPDATE hospital SET upi_id = 'hospital-name@paytm' WHERE id = 1;
```

## Testing

1. Book an appointment or operation
2. You'll be redirected to the payment page
3. Select a UPI app
4. QR code will be displayed
5. Test payment verification

## Notes

- Payment verification is currently manual. In production, integrate with payment gateway webhooks.
- QR codes are generated dynamically for each transaction.
- All UPI apps use the same QR code (UPI standard), but displayed with different branding.
- Payment status can be updated by doctors/admins via the `/api/payments/complete/{payment_id}` endpoint.

## Future Enhancements

- [ ] Integrate with payment gateway (Razorpay, PayU, etc.) for automatic verification
- [ ] Add payment history page
- [ ] Email/SMS notifications for payment status
- [ ] Refund functionality
- [ ] Multiple payment methods (cards, netbanking, etc.)



