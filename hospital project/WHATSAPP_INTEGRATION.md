# WhatsApp Integration Guide

## Overview
This system integrates WhatsApp Web automation for sending appointment confirmations, follow-ups, and reminders to patients.

## Features

### ✅ Implemented Features

1. **CSV Export with +91 Prefix**
   - All appointments are automatically saved to CSV files
   - Mobile numbers are normalized with +91 prefix
   - One CSV file per hospital: `hospital_{id}_appointments.csv`

2. **WhatsApp Web Automation**
   - Persistent sessions per hospital
   - One-time QR code scan per hospital
   - Automatic message sending

3. **Automatic Confirmation Messages**
   - Sent immediately after appointment booking
   - Customizable message templates per hospital

4. **Doctor Visit Marking**
   - Doctors can mark appointments as "Visited"
   - Optional follow-up date setting

5. **Automated Follow-up Reminders**
   - Daily scheduler sends follow-up reminders
   - Runs at 9:00 AM daily

6. **Appointment Reminders**
   - Sends reminders 1 day before appointment
   - Runs at 10:00 AM daily

7. **Hospital-Level Controls**
   - Enable/disable WhatsApp per hospital
   - Custom message templates
   - Session health monitoring

## Setup Instructions

### 1. Install Dependencies

```bash
pip install selenium webdriver-manager apscheduler
```

### 2. Initialize WhatsApp Session for Hospital

1. Call the API endpoint:
   ```
   POST /api/hospitals/{hospital_id}/whatsapp-init
   ```

2. A Chrome browser window will open with WhatsApp Web
3. Scan the QR code with your hospital's WhatsApp mobile
4. Session will be saved and persist across restarts

### 3. Enable WhatsApp for Hospital

```bash
PUT /api/hospitals/{hospital_id}/whatsapp-settings
{
  "whatsapp_enabled": "true"
}
```

### 4. Customize Message Templates (Optional)

```bash
PUT /api/hospitals/{hospital_id}/whatsapp-settings
{
  "whatsapp_confirmation_template": "Hello {patient_name}, Your appointment with Dr {doctor_name} is confirmed for {date} at {time}. - {hospital_name}",
  "whatsapp_followup_template": "Hello {patient_name}, Reminder: Follow-up with Dr {doctor_name} on {followup_date}. - {hospital_name}",
  "whatsapp_reminder_template": "Hello {patient_name}, Reminder: Appointment with Dr {doctor_name} tomorrow at {time}. - {hospital_name}"
}
```

**Available placeholders:**
- `{patient_name}` - Patient's name
- `{doctor_name}` - Doctor's name
- `{date}` - Appointment date
- `{time}` - Appointment time
- `{followup_date}` - Follow-up date
- `{hospital_name}` - Hospital name
- `{specialty}` - Doctor's specialty (if available)

## API Endpoints

### WhatsApp Management

- `POST /api/hospitals/{hospital_id}/whatsapp-init` - Initialize WhatsApp session
- `GET /api/hospitals/{hospital_id}/whatsapp-status` - Check session status
- `PUT /api/hospitals/{hospital_id}/whatsapp-settings` - Update settings
- `POST /api/hospitals/{hospital_id}/whatsapp-close` - Close session

### Appointment Management

- `POST /api/appointments/book` - Book appointment (auto-saves CSV and sends WhatsApp)
- `PUT /api/appointments/{id}/mark-visited` - Mark as visited (with optional follow-up date)

## CSV File Format

Location: `./appointment_exports/hospital_{id}_appointments.csv`

```csv
name,mobile,date,time_slot,doctor,specialty,followup_date
Rahul Sharma,+919876543210,2025-02-10,10:30,Dr Mehta,Ortho,2025-02-17
```

## Message Flow

### 1. Appointment Booking
1. Patient books appointment
2. Data saved to database
3. Data appended to CSV file
4. WhatsApp confirmation sent (if enabled)

### 2. Doctor Visit
1. Doctor marks appointment as "Visited"
2. Optional: Set follow-up date
3. System schedules follow-up reminder

### 3. Automated Reminders
- **Follow-up Reminders**: Sent on follow-up date at 9:00 AM
- **Appointment Reminders**: Sent 1 day before appointment at 10:00 AM

## Rate Limiting & Safety

- **One-to-one messages only** (no bulk blasting)
- **Rate limit**: 10-15 messages per minute (built into Selenium delays)
- **Error handling**: Failed messages are logged
- **Session monitoring**: Automatic health checks

## Troubleshooting

### Session Expired
If WhatsApp session expires:
1. Check status: `GET /api/hospitals/{id}/whatsapp-status`
2. Re-initialize: `POST /api/hospitals/{id}/whatsapp-init`
3. Scan QR code again

### Messages Not Sending
1. Verify WhatsApp is enabled: `whatsapp_enabled = "true"`
2. Check session health
3. Review logs for errors
4. Ensure mobile numbers are in correct format

### CSV Not Saving
1. Check `appointment_exports/` directory exists
2. Verify write permissions
3. Check application logs

## File Structure

```
services/
├── whatsapp_service.py      # WhatsApp Web automation
├── csv_service.py           # CSV export functionality
├── message_templates.py     # Message template system
└── scheduler_service.py     # Background job scheduler

appointment_exports/         # CSV files directory
whatsapp_sessions/           # Browser session data
  └── {hospital_id}/         # Per-hospital sessions
```

## Next Steps (Recommended)

When ready to scale:
1. **Migrate to WhatsApp Business API** (official, legal, scalable)
2. **Add message delivery tracking**
3. **Implement message template approval workflow**
4. **Add analytics dashboard**

## Notes

- WhatsApp Web sessions persist across server restarts
- Each hospital has its own isolated session
- CSV files are append-only (never overwritten)
- Scheduler runs automatically on server start
- All messages are logged for audit purposes



