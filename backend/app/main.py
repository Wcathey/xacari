from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health import router as health_router
from app.routes.version import router as version_router
from app.routes.websocket import router as websocket_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.error_handlers import register_exception_handlers

# Initialize logging
setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Register exception handlers
register_exception_handlers(app)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
)

# Include routers
from app.routes.workout import router as workout_router
from app.routes.pose import router as pose_router
from app.routes.exercises import router as exercises_router

app.include_router(health_router)
app.include_router(version_router)
app.include_router(websocket_router)
app.include_router(workout_router)
app.include_router(pose_router)
app.include_router(exercises_router)


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    """
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    return {
        "message": "Xacari Backend Running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
