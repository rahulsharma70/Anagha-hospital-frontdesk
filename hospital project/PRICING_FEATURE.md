# Pricing Feature Documentation

## Overview
A comprehensive pricing section has been added to the homepage with Indian Rupee (₹) pricing and an admin interface for easy price management.

## Features
- ✅ **Pricing Section on Homepage**: Beautiful, responsive pricing cards with ₹ (Indian Rupee) currency
- ✅ **Three Pricing Plans**: Starter, Professional, and Enterprise plans
- ✅ **Annual Discount Display**: Shows savings when billed annually (20% default)
- ✅ **Admin Pricing Management**: Easy-to-use interface for updating prices
- ✅ **JSON Configuration**: Simple JSON file for price management
- ✅ **Dynamic Loading**: Prices load dynamically from configuration

## Pricing Plans

### Starter Plan - ₹999/month
- Perfect for small clinics
- Up to 5 doctors
- Unlimited appointments
- Basic scheduling
- Email support
- Mobile app access

### Professional Plan - ₹2,499/month (Most Popular)
- Ideal for growing practices
- Up to 20 doctors
- Unlimited appointments
- Advanced scheduling
- Operation management
- Priority support
- Custom branding
- Analytics dashboard

### Enterprise Plan - ₹4,999/month
- For large hospitals
- Unlimited doctors
- Unlimited appointments
- Full operation management
- Multi-location support
- 24/7 priority support
- Custom integrations
- Advanced analytics
- Dedicated account manager

## Configuration File

Pricing is managed through `pricing_config.json`:

```json
{
  "plans": [
    {
      "name": "Starter",
      "price": "999",
      "period": "month",
      "description": "Perfect for small clinics",
      "features": ["Feature 1", "Feature 2"],
      "popular": false
    }
  ],
  "annual_discount": 20,
  "currency": "INR",
  "currency_symbol": "₹"
}
```

## How to Update Prices

### Method 1: Admin Interface (Recommended)
1. Login as a doctor/admin
2. Navigate to "Manage Pricing" in the navigation menu
3. Edit prices, features, and plan details
4. Click "Save Changes"
5. Changes are reflected immediately on the homepage

### Method 2: Direct File Edit
1. Open `pricing_config.json` in the project root
2. Edit prices, features, or add/remove plans
3. Save the file
4. Refresh the homepage to see changes

## Admin Interface

### Access
- URL: `/admin/pricing`
- Access: Doctors/Admins only
- Navigation: "Manage Pricing" link in header (visible to doctors)

### Features
- Edit plan names, prices, and descriptions
- Add/remove features for each plan
- Mark plans as "Popular"
- Adjust annual discount percentage
- Add new plans
- Remove existing plans

## API Endpoints

### GET `/static/pricing_config.json`
Returns the current pricing configuration.

### POST `/api/admin/update-pricing`
Updates pricing configuration (admin only).

**Request Body:**
```json
{
  "plans": [...],
  "annual_discount": 20,
  "currency": "INR",
  "currency_symbol": "₹"
}
```

### GET `/api/admin/pricing`
Get current pricing (admin only).

## Homepage Integration

The pricing section appears:
- After the "Designed for Every Healthcare Professional" section
- Before the final CTA section
- Responsive design for mobile and desktop
- Dynamic loading from configuration

## Customization

### Change Currency
Edit `pricing_config.json`:
```json
{
  "currency": "INR",
  "currency_symbol": "₹"
}
```

### Change Annual Discount
Edit `annual_discount` in `pricing_config.json` (0-100).

### Add/Remove Plans
Add or remove plan objects in the `plans` array.

### Change Plan Features
Edit the `features` array for each plan.

## Styling

The pricing cards use:
- Primary color for popular plan border
- Hover effects for interactivity
- Responsive grid layout
- Professional card design

## Notes

- Prices are displayed in Indian Rupees (₹)
- Annual billing shows monthly equivalent with discount
- All plans include a 14-day free trial (mentioned in UI)
- Changes take effect immediately after saving
- Configuration file is stored in project root

## Future Enhancements

- [ ] Payment integration with pricing plans
- [ ] Plan comparison table
- [ ] Custom pricing for enterprise clients
- [ ] Trial period management
- [ ] Usage-based pricing options



