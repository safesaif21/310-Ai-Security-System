"""Auth Service Entry Point"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.shared.config import settings
from backend.services.auth.routes import router as auth_router
from backend.shared.database import get_database, close_mongo_connection

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Auth Service",
    version=settings.app_version,
    description="Authentication Microservice"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Auth Service...")
    # Initialize DB connection (if needed globally, otherwise dependencies handle it)
    try:
        db = get_database()
        logger.info(f"Connected to MongoDB: {db.name}")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Auth Service...")
    close_mongo_connection()

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "auth"}
