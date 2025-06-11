"""Health check API endpoints."""

import platform
import time
from typing import Dict

from fastapi import APIRouter
from loguru import logger

from meal_planner.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict:
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": time.time()
    }


@router.get("/health/system")
async def system_info() -> Dict:
    """System information endpoint.
    
    Returns:
        System information
    """
    return {
        "status": "ok",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "memory": {
            "total": "N/A",  # Would require psutil
            "available": "N/A"  # Would require psutil
        }
    }


@router.get("/health/ocr")
async def ocr_health() -> Dict:
    """OCR health check endpoint.
    
    Returns:
        OCR health status
    """
    return {
        "status": "not_implemented",
        "message": "OCR functionality not implemented yet"
    }


@router.get("/health/llm")
async def llm_health() -> Dict:
    """LLM health check endpoint.
    
    Returns:
        LLM health status
    """
    return {
        "status": "not_implemented", 
        "message": "LLM functionality not implemented yet"
    }