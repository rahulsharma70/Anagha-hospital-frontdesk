from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hospital SaaS Backend",
    description="Hospital booking system backend API",
    version="1.0.0"
)

# CORS middleware for Flutter/Web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "Backend running",
        "message": "Hospital SaaS API is live",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/config")
def get_config():
    """Check configuration status"""
    from config import get_config
    return {
        "status": "ok",
        "configuration": get_config()
    }

# Test database connection endpoint
@app.get("/test-db")
def test_db():
    from database import test_connection, SUPABASE_API_KEY
    result = test_connection()
    response = {
        "status": "Database connected" if result else "Database connection failed",
        "database_connected": result
    }
    if SUPABASE_API_KEY:
        response["supabase_api_key"] = "configured"
    return response

