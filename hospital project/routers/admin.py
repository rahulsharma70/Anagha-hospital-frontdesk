from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import UserRole
# Note: User SQLAlchemy model removed - using Supabase now
from auth import get_current_user
import json
import os

router = APIRouter(prefix="/api/admin", tags=["admin"])

def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Verify user is admin/doctor"""
    if current_user.get("role") != "doctor":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.post("/update-pricing")
def update_pricing(
    pricing_data: dict,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user)
):
    """Update pricing configuration"""
    try:
        # Validate pricing data structure
        required_fields = ["plans", "annual_discount", "currency", "currency_symbol"]
        for field in required_fields:
            if field not in pricing_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate plans
        if not isinstance(pricing_data["plans"], list) or len(pricing_data["plans"]) == 0:
            raise HTTPException(status_code=400, detail="At least one plan is required")
        
        for plan in pricing_data["plans"]:
            required_plan_fields = ["name", "price", "period", "description", "features"]
            for field in required_plan_fields:
                if field not in plan:
                    raise HTTPException(status_code=400, detail=f"Plan missing required field: {field}")
        
        # Save to file
        config_path = "pricing_config.json"
        with open(config_path, "w") as f:
            json.dump(pricing_data, f, indent=2)
        
        return {"message": "Pricing updated successfully", "pricing": pricing_data}
    
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Pricing config file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating pricing: {str(e)}")

@router.get("/pricing")
def get_pricing(admin_user: dict = Depends(get_admin_user)):
    """Get current pricing configuration"""
    try:
        config_path = "pricing_config.json"
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default if file doesn't exist
        return {
            "plans": [
                {
                    "name": "Starter",
                    "price": "999",
                    "period": "month",
                    "description": "Perfect for small clinics",
                    "features": ["Up to 5 doctors", "Unlimited appointments", "Basic scheduling", "Email support"],
                    "popular": False
                }
            ],
            "annual_discount": 20,
            "currency": "INR",
            "currency_symbol": "₹"
        }



