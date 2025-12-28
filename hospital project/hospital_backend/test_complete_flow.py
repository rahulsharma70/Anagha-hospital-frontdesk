"""
Complete Flow Testing Script
Tests the entire hospital booking system flow
"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_health():
    """Test 1: Health Check"""
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_db_connection():
    """Test 2: Database Connection"""
    print_section("Test 2: Database Connection")
    try:
        response = requests.get(f"{BASE_URL}/test-db")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json().get("database_connected", False)
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_hospital_registration():
    """Test 3: Register Hospital"""
    print_section("Test 3: Register Hospital")
    hospital_data = {
        "name": "Test Hospital",
        "email": "test@hospital.com",
        "mobile": "9876543210",
        "address_line1": "123 Test Street",
        "city": "Test City",
        "state": "Test State",
        "pincode": "123456"
    }
    try:
        response = requests.post(f"{API_URL}/hospitals/register", json=hospital_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        if response.status_code == 200:
            return result.get("id")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def approve_hospital(hospital_id):
    """Approve Hospital (Admin function)"""
    print_section(f"Approve Hospital ID: {hospital_id}")
    try:
        response = requests.put(f"{API_URL}/hospitals/{hospital_id}/approve")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_user_registration(hospital_id, role="patient"):
    """Test 4: Register User"""
    print_section(f"Test 4: Register {role.capitalize()}")
    user_data = {
        "name": f"Test {role.capitalize()}",
        "mobile": f"9876543{role[:3]}",
        "role": role,
        "password": "test123",
        "hospital_id": hospital_id,
        "address_line1": "Test Address"
    }
    
    if role == "pharma":
        user_data.update({
            "company_name": "Test Pharma Company",
            "product1": "Product A",
            "product2": "Product B"
        })
    elif role == "doctor":
        user_data.update({
            "degree": "MBBS",
            "institute_name": "Test Medical College",
            "experience1": "5 years in general practice"
        })
    
    try:
        response = requests.post(f"{API_URL}/users/register", json=user_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        if response.status_code == 200:
            return result.get("id")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_login(mobile, password):
    """Test 5: User Login"""
    print_section("Test 5: User Login")
    login_data = {
        "mobile": mobile,
        "password": password
    }
    try:
        response = requests.post(f"{API_URL}/users/login", json=login_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        if response.status_code == 200:
            token = result.get("access_token")
            print(f"✓ Login successful!")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print(f"Response: {json.dumps(result, indent=2)}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_book_appointment(token, doctor_id, hospital_id):
    """Test 6: Book Appointment"""
    print_section("Test 6: Book Appointment")
    tomorrow = date.today() + timedelta(days=1)
    appointment_data = {
        "doctor_id": doctor_id,
        "date": str(tomorrow),
        "time_slot": "10:00"
    }
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{API_URL}/appointments/book", json=appointment_data, headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        if response.status_code == 200:
            return result.get("id")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_book_operation(token, doctor_id, hospital_id):
    """Test 7: Book Operation"""
    print_section("Test 7: Book Operation")
    next_week = date.today() + timedelta(days=7)
    operation_data = {
        "specialty": "ortho",
        "doctor_id": doctor_id,
        "date": str(next_week),
        "notes": "Test operation"
    }
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{API_URL}/operations/book", json=operation_data, headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_appointments(token):
    """Test 8: Get My Appointments"""
    print_section("Test 8: Get My Appointments")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_URL}/appointments/my-appointments", headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Found {len(result)} appointments")
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("  HOSPITAL BOOKING SYSTEM - COMPLETE FLOW TEST")
    print("=" * 70)
    print("\nMake sure the server is running: uvicorn main:app --reload")
    input("\nPress Enter to start testing...")
    
    results = {}
    
    # Test 1: Health Check
    results["health"] = test_health()
    if not results["health"]:
        print("\n✗ Server is not running. Please start it first.")
        return
    
    # Test 2: Database Connection
    results["database"] = test_db_connection()
    if not results["database"]:
        print("\n✗ Database connection failed. Check your .env file.")
        return
    
    # Test 3: Register Hospital
    hospital_id = test_hospital_registration()
    results["hospital_registration"] = hospital_id is not None
    
    if hospital_id:
        # Approve hospital
        approve_hospital(hospital_id)
        
        # Test 4: Register Users
        patient_id = test_user_registration(hospital_id, "patient")
        results["patient_registration"] = patient_id is not None
        
        pharma_id = test_user_registration(hospital_id, "pharma")
        results["pharma_registration"] = pharma_id is not None
        
        doctor_id = test_user_registration(hospital_id, "doctor")
        results["doctor_registration"] = doctor_id is not None
        
        if patient_id and doctor_id:
            # Test 5: Login
            patient_token = test_login("9876543pat", "test123")
            results["login"] = patient_token is not None
            
            if patient_token:
                # Test 6: Book Appointment
                appointment_id = test_book_appointment(patient_token, doctor_id, hospital_id)
                results["appointment_booking"] = appointment_id is not None
                
                # Test 7: Book Operation
                results["operation_booking"] = test_book_operation(patient_token, doctor_id, hospital_id)
                
                # Test 8: Get Appointments
                results["get_appointments"] = test_get_appointments(patient_token)
    
    # Summary
    print_section("TEST SUMMARY")
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()



