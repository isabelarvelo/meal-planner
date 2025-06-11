"""API dependencies with database support."""

from functools import lru_cache
from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.core.config import settings
from meal_planner.core.services import RecipeStorageService  # Keep the file-based service for now
from meal_planner.db import get_db_session, UserService, RecipeService, MealPlanService


# Database dependencies
async def get_user_service(db: AsyncSession = Depends(get_db_session)) -> UserService:
    """Get user service with database session."""
    return UserService(db)


async def get_recipe_service(db: AsyncSession = Depends(get_db_session)) -> RecipeService:
    """Get recipe service with database session."""
    return RecipeService(db)


async def get_meal_plan_service_db(db: AsyncSession = Depends(get_db_session)) -> MealPlanService:
    """Get meal plan service with database session."""
    return MealPlanService(db)

@lru_cache
def get_storage_service() -> RecipeStorageService:
    """Get the recipe storage service.
    
    Returns:
        Recipe storage service
    """
    return RecipeStorageService(recipes_dir=settings.recipes_dir)


# Placeholder functions for other dependencies (will implement later)
def get_ocr_primary():
    """Placeholder for OCR engine."""
    raise NotImplementedError("OCR functionality not implemented yet")


def get_ocr_fallback():
    """Placeholder for fallback OCR engine."""
    raise NotImplementedError("OCR functionality not implemented yet")


def get_llm_provider():
    """Placeholder for LLM provider."""
    raise NotImplementedError("LLM functionality not implemented yet")


def get_extraction_service():
    """Placeholder for extraction service."""
    raise NotImplementedError("Recipe extraction not implemented yet")


def get_meal_plan_service():
    """Placeholder for meal plan service."""
    raise NotImplementedError("Meal planning not implemented yet")


# Remove the duplicate functions at the bottom that have missing imports
# These will be implemented later when we add the actual LLM and OCR functionality