"""Recipe-related API endpoints."""

import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import (
    APIRouter, Depends, File, Form, HTTPException, Path as PathParam, Query, UploadFile
)
from fastapi.responses import Response
from loguru import logger
from pydantic import BaseModel, Field

from meal_planner.api.dependencies import get_storage_service
from meal_planner.core.config import settings
from meal_planner.core.models import (
    DietaryRestriction, MealType, NutritionInfo, Recipe, Appliance, Ingredient
)
from meal_planner.core.services import RecipeStorageService

router = APIRouter()


@router.options("/recipes")
async def recipes_options():
    """Handle OPTIONS request for recipes endpoint."""
    return Response(status_code=200)


class RecipeCreateRequest(BaseModel):
    """Request model for creating a recipe."""
    
    title: str
    ingredients: List[Union[str, Ingredient]]
    instructions: List[str]
    meal_types: List[Union[str, MealType]] = Field(default_factory=list)
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    dietary_restrictions: List[Union[str, DietaryRestriction]] = Field(default_factory=list)
    appliances: List[Union[str, Appliance]] = Field(default_factory=list)
    notes: Optional[str] = None


class RecipeUpdateRequest(BaseModel):
    """Request model for updating a recipe."""
    
    title: Optional[str] = None
    ingredients: Optional[List[Union[str, Ingredient]]] = None
    instructions: Optional[List[str]] = None
    meal_types: Optional[List[Union[str, MealType]]] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    dietary_restrictions: Optional[List[Union[str, DietaryRestriction]]] = None
    appliances: Optional[List[Union[str, Appliance]]] = None
    notes: Optional[str] = None


@router.post("/recipes", response_model=Recipe)
async def create_recipe(
    recipe_request: RecipeCreateRequest,
    storage_service: RecipeStorageService = Depends(get_storage_service)
):
    """Create a new recipe.
    
    Args:
        recipe_request: Recipe creation request
        storage_service: Recipe storage service
        
    Returns:
        Created recipe
    """
    # Create Recipe object with generated ID and timestamps
    recipe = Recipe(
        id=uuid.uuid4(),
        title=recipe_request.title,
        ingredients=recipe_request.ingredients,
        instructions=recipe_request.instructions,
        meal_types=recipe_request.meal_types,
        prep_time_minutes=recipe_request.prep_time_minutes,
        cook_time_minutes=recipe_request.cook_time_minutes,
        servings=recipe_request.servings,
        source_url=recipe_request.source_url,
        image_url=recipe_request.image_url,
        tags=recipe_request.tags,
        dietary_restrictions=recipe_request.dietary_restrictions,
        appliances=recipe_request.appliances,
        notes=recipe_request.notes,
        created_at=time.time(),
        updated_at=time.time()
    )
    
    # Save recipe
    storage_service.save_recipe(recipe)
    
    return recipe


# IMPORTANT: Put specific routes BEFORE parameterized routes
@router.get("/recipes/search", response_model=List[Recipe])
async def search_recipes(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    storage_service: RecipeStorageService = Depends(get_storage_service)
):
    """Search recipes.
    
    Args:
        query: Search query
        limit: Maximum number of recipes to return
        storage_service: Recipe storage service
        
    Returns:
        List of matching recipes
    """
    return storage_service.search_recipes(query=query, limit=limit)


@router.post("/recipes/extract")
async def extract_recipe():
    """Extract a recipe from an image or document - not implemented yet."""
    raise HTTPException(status_code=501, detail="Recipe extraction not implemented yet")


@router.post("/recipes/{recipe_id}/analyze-nutrition")
async def analyze_recipe_nutrition():
    """Analyze nutrition information for a recipe - not implemented yet."""
    raise HTTPException(status_code=501, detail="Nutrition analysis not implemented yet")


@router.get("/recipes", response_model=List[Recipe])
async def list_recipes(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    storage_service: RecipeStorageService = Depends(get_storage_service)
):
    """List recipes.
    
    Args:
        limit: Maximum number of recipes to return
        offset: Offset for pagination
        storage_service: Recipe storage service
        
    Returns:
        List of recipes
    """
    return storage_service.list_recipes(limit=limit, offset=offset)


@router.get("/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(
    recipe_id: UUID = PathParam(..., description="Recipe ID"),
    storage_service: RecipeStorageService = Depends(get_storage_service)
):
    """Get a recipe by ID.
    
    Args:
        recipe_id: Recipe ID
        storage_service: Recipe storage service
        
    Returns:
        Recipe
    """
    recipe = storage_service.load_recipe(recipe_id)
    
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return recipe


@router.put("/recipes/{recipe_id}", response_model=Recipe)
async def update_recipe(
    recipe_request: RecipeUpdateRequest,
    recipe_id: UUID = PathParam(..., description="Recipe ID"),
    storage_service: RecipeStorageService = Depends(get_storage_service)
):
    """Update a recipe.
    
    Args:
        recipe_request: Recipe update request
        recipe_id: Recipe ID
        storage_service: Recipe storage service
        
    Returns:
        Updated recipe
    """
    # Check if recipe exists
    existing_recipe = storage_service.load_recipe(recipe_id)
    
    if existing_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Update only provided fields
    update_data = recipe_request.model_dump(exclude_unset=True)
    update_data['updated_at'] = time.time()
    
    # Create updated recipe
    updated_recipe = existing_recipe.model_copy(update=update_data)
    
    # Save updated recipe
    storage_service.save_recipe(updated_recipe)
    
    return updated_recipe


@router.delete("/recipes/{recipe_id}")
async def delete_recipe(
    recipe_id: UUID = PathParam(..., description="Recipe ID"),
    storage_service: RecipeStorageService = Depends(get_storage_service)
):
    """Delete a recipe.
    
    Args:
        recipe_id: Recipe ID
        storage_service: Recipe storage service
        
    Returns:
        Deletion status
    """
    success = storage_service.delete_recipe(recipe_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return {"message": "Recipe deleted successfully"}