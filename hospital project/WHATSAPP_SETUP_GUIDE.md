# WhatsApp Integration - Quick Setup Guide

## ✅ Implementation Complete!

All WhatsApp integration features have been successfully implemented:

### Features Implemented

1. ✅ **CSV Export** - Automatic export with +91 mobile prefix
2. ✅ **WhatsApp Web Automation** - Selenium-based message sending
3. ✅ **Auto Confirmation Messages** - Sent on appointment booking
4. ✅ **Doctor Visit Marking** - Mark appointments as visited
5. ✅ **Follow-up Reminders** - Automated daily reminders
6. ✅ **Appointment Reminders** - 1-day advance reminders
7. ✅ **Hospital-Level Controls** - Enable/disable per hospital
8. ✅ **Custom Message Templates** - Editable per hospital
9. ✅ **Session Management** - Persistent WhatsApp sessions
10. ✅ **Background Scheduler** - APScheduler for automated tasks

## Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `selenium==4.15.2`
- `webdriver-manager==4.0.1`
- `apscheduler==3.10.4`

### Step 2: Run Database Migration

Execute the SQL script in your database (Supabase SQL Editor):

```bash
# Run whatsapp_schema.sql
```

This adds:
- `visit_date` and `followup_date` to appointments
- WhatsApp settings columns to hospitals

### Step 3: Initialize WhatsApp for a Hospital

1. **Start the server:**
   ```bash
   python3 -m uvicorn main:app --reload
   ```

2. **Initialize WhatsApp session:**
   ```bash
   POST /api/hospitals/{hospital_id}/whatsapp-init
   ```

3. **A Chrome browser will open** - Scan QR code with hospital's WhatsApp

4. **Enable WhatsApp:**
   ```bash
   PUT /api/hospitals/{hospital_id}/whatsapp-settings
   {
     "whatsapp_enabled": "true"
   }
   ```

### Step 4: Test the Flow

1. **Book an appointment** - CSV is saved automatically
2. **WhatsApp confirmation** is sent automatically (if enabled)
3. **Doctor marks visit** - Use `/api/appointments/{id}/mark-visited`
4. **Reminders run automatically** - Daily at 9 AM and 10 AM

## File Structure

```
services/
├── whatsapp_service.py      # WhatsApp automation
├── csv_service.py           # CSV export
├── message_templates.py     # Message templates
└── scheduler_service.py      # Background jobs

appointment_exports/         # CSV files (auto-created)
whatsapp_sessions/           # Browser sessions (auto-created)
  └── {hospital_id}/
```

## API Endpoints

### WhatsApp Management
- `POST /api/hospitals/{id}/whatsapp-init` - Initialize session
- `GET /api/hospitals/{id}/whatsapp-status` - Check status
- `PUT /api/hospitals/{id}/whatsapp-settings` - Update settings
- `POST /api/hospitals/{id}/whatsapp-close` - Close session

### Appointments
- `POST /api/appointments/book` - Book (auto CSV + WhatsApp)
- `PUT /api/appointments/{id}/mark-visited` - Mark visited

## CSV Format

Files: `appointment_exports/hospital_{id}_appointments.csv`

```csv
name,mobile,date,time_slot,doctor,specialty,followup_date
Rahul Sharma,+919876543210,2025-02-10,10:30,Dr Mehta,,2025-02-17
```

## Message Templates

### Default Templates

**Confirmation:**
```
Hello {patient_name},
Your appointment with Dr {doctor_name} is confirmed.
🗓 Date: {date}
⏰ Time: {time}
– {hospital_name}
```

**Follow-up:**
```
Hello {patient_name},
This is a reminder for your follow-up visit with Dr {doctor_name}.
📅 Date: {followup_date}
– {hospital_name}
```

**Reminder:**
```
Hello {patient_name},
Reminder: Your appointment with Dr {doctor_name} is scheduled for:
🗓 Date: {date}
⏰ Time: {time}
Please arrive on time.
– {hospital_name}
```

### Customize Templates

```bash
PUT /api/hospitals/{id}/whatsapp-settings
{
  "whatsapp_confirmation_template": "Your custom message with {patient_name}, {doctor_name}, etc."
}
```

## Scheduler

Runs automatically on server start:
- **Follow-up reminders**: Daily at 9:00 AM
- **Appointment reminders**: Daily at 10:00 AM

## Safety Features

✅ One-to-one messages only (no bulk blasting)
✅ Rate limiting (10-15 msgs/min via delays)
✅ Error logging
✅ Session health monitoring
✅ Retry mechanism (3 attempts)

## Troubleshooting

### Session Expired
```bash
# Check status
GET /api/hospitals/{id}/whatsapp-status

# Re-initialize
POST /api/hospitals/{id}/whatsapp-init
```

### Messages Not Sending
1. Check `whatsapp_enabled = "true"`
2. Verify session is active
3. Check application logs
4. Ensure mobile format is correct

### CSV Not Saving
1. Check `appointment_exports/` directory exists
2. Verify write permissions
3. Check logs for errors

## Next Steps

When ready to scale:
1. **WhatsApp Business API** - Official, legal, scalable
2. **Message delivery tracking**
3. **Template approval workflow**
4. **Analytics dashboard**

## Support

For detailed documentation, see:
- `WHATSAPP_INTEGRATION.md` - Full feature documentation
- `whatsapp_schema.sql` - Database schema updates

---

**Status**: ✅ All features implemented and ready to use!



