"""Main API application."""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from meal_planner.api.routers import health, meal_plans, recipes, users
from meal_planner.core.config import settings
from meal_planner.db import init_database, close_database


# Create data directories
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.recipes_dir, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for meal planning and recipe management",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",  # Common frontend dev server port
    "http://127.0.0.1:8080"
]


# Add the configured origins from settings
allowed_origins.extend(settings.allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Database event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting up Meal Planner API...")
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    logger.info("Shutting down Meal Planner API...")
    try:
        await close_database()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# Add routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(recipes.router, prefix="/api", tags=["recipes"])
app.include_router(meal_plans.router, prefix="/api", tags=["meal_plans"])
app.include_router(users.router, prefix="/api", tags=["users"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler.
    
    Args:
        request: Request
        exc: Exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/api")
async def root():
    """Root endpoint.
    
    Returns:
        API information
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs_url": "/api/docs"
    }
