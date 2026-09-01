import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.core.database import engine
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.core.security import bootstrap_admin, validate_security_settings
from backend.app.models import Base
from backend.app.services.camera_manager import camera_manager
from backend.app.api.cameras import router as cameras_router
from backend.app.api.events import router as events_router
from backend.app.api.auth import router as auth_router
from backend.app.api.anpr import router as anpr_router
from backend.app.api.system import router as system_router
from backend.app.api.demo import router as demo_router
from backend.app.api.ws import router as ws_router
from backend.app.services.geo_service import geo_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    validate_security_settings()
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"Base.metadata.create_all warning: {e}")
    db = SessionLocal()
    try:
        bootstrap_admin(db)
    finally:
        db.close()
    
    logger.info("Starting video ingestion streams...")
    camera_manager.start_all()
    
    from backend.app.api.ws import start_ws_listener, stop_ws_listener
    await start_ws_listener()
    
    import asyncio
    geo_service.start(loop=asyncio.get_running_loop())
    
    yield
    # Shutdown actions
    logger.info("Stopping video ingestion streams...")
    camera_manager.stop_all()
    geo_service.stop()
    await stop_ws_listener()

app = FastAPI(
    title="IBVAP Command Center API",
    description="Intelligent Border Video Analytics Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(cameras_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(anpr_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(demo_router, prefix="/api")
app.include_router(ws_router)

@app.get("/")
def read_root():
    return {
        "status": "ONLINE",
        "app": "IBVAP (Intelligent Border Video Analytics Platform)",
        "docs": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
