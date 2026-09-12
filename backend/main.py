from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

import sys
from pathlib import Path

# Add backend/RESQ-AI to sys.path for module resolution
resq_ai_dir = Path(__file__).resolve().parent / "RESQ-AI"
if str(resq_ai_dir) not in sys.path:
    sys.path.insert(0, str(resq_ai_dir))

from backend.config import settings
from backend.routers import alerts, locations, ai
from backend.database import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Flood Emergency Response System")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    yield
    # Shutdown
    logger.info("Shutting down application")


app = FastAPI(
    title="Flood Emergency Response System",
    description="Transform emergency flood response from reactive data interpretation to proactive decision intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["locations"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai-legacy"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Flood Emergency Response System API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
