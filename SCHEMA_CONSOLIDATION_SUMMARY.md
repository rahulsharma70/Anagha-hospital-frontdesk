# Database Schema Consolidation Summary

## ✅ Consolidation Complete

All database schema files have been consolidated into a single file: `backend/complete_schema.sql`

### Files Removed (9 files):
1. ✅ `backend/supabase_schema.sql` - Deleted
2. ✅ `backend/supabase_simple.sql` - Deleted
3. ✅ `backend/supabase_tables.sql` - Deleted
4. ✅ `backend/supabase_audit_schema.sql` - Deleted
5. ✅ `backend/supabase_smtp_migration.sql` - Deleted
6. ✅ `backend/hospital_upi_schema.sql` - Deleted
7. ✅ `backend/whatsapp_schema.sql` - Deleted
8. ✅ `backend/payment_schema.sql` - Deleted
9. ✅ `backend/razorpay_schema.sql` - Deleted

### New Consolidated File:
**`backend/complete_schema.sql`** - Contains all schemas in one file

---

## Schema Structure

### 1. Core Tables
- **hospitals** - Hospital registration with UPI, WhatsApp, SMTP settings
- **users** - Patients, pharma professionals, doctors
- **appointments** - Patient appointments with doctors
- **operations** - Scheduled operations

### 2. Payment Tables
- **payments** - Payment records (Razorpay + UPI)
- **payment_webhooks** - Razorpay webhook events (idempotency)
- **payment_refunds** - Refund records
- **payment_retry_queue** - Retry queue for failed operations
- **payment_manual_review** - Manual review queue

### 3. Audit & Logging Tables
- **audit_logs** - System audit trail
- **whatsapp_logs** - WhatsApp message delivery logs

---

## Key Features

### Table Naming Convention
- All tables use **plural** names (matches codebase):
  - `hospitals` (not `hospital`)
  - `appointments` (not `appointment`)
  - `operations` (not `operation`)
  - `users` (not `user`)

### Column Consistency
- **Operations table**: Uses `operation_date` (primary field)
- **Payments table**: Uses `DECIMAL(10, 2)` for amount (with migration logic)
- **Status fields**: Proper CHECK constraints
- **Timestamps**: Consistent naming (`created_at`, `updated_at`, etc.)

### Indexes
- All foreign keys indexed
- Status fields indexed
- Date fields indexed
- Unique constraints on critical fields
- Composite indexes for common queries

### Documentation
- Table comments for all tables
- Column comments for important fields
- Clear section organization

---

## Migration Notes

### For Existing Databases:
1. The schema uses `IF NOT EXISTS` - safe to run multiple times
2. Amount conversion from TEXT to DECIMAL is handled with migration logic
3. All ALTER TABLE statements use `IF NOT EXISTS` - won't fail on existing columns

### Table Name Mapping:
- Code uses: `hospitals`, `appointments`, `operations`, `users`
- Schema matches codebase exactly

### Field Compatibility:
- Operations: Code handles both `operation_date` and `date` (schema has `operation_date`)
- Payments: Legacy fields (`transaction_id`, `upi_transaction_id`) preserved for backward compatibility

---

## Usage

**To apply schema:**
```sql
-- Copy and paste entire backend/complete_schema.sql
-- into Supabase SQL Editor
-- Execute
```

**Schema is idempotent:**
- Safe to run multiple times
- Uses `IF NOT EXISTS` for all CREATE statements
- Uses `IF NOT EXISTS` for all ALTER statements
- Won't duplicate indexes or constraints

---

## Verification Checklist

✅ All table names match codebase (plural forms)
✅ All foreign key relationships correct
✅ All indexes created
✅ All constraints defined
✅ Payment integration complete (Razorpay + UPI)
✅ WhatsApp integration fields included
✅ SMTP configuration fields included
✅ Audit logging table included
✅ Comments and documentation included
✅ Row Level Security configured for audit_logs

---

**Status:** ✅ Complete and ready for deployment

