"""Database-enabled recipe router (optional alternative to current recipes.py)."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from meal_planner.api.dependencies import get_recipe_service, get_user_service
from meal_planner.db.services import RecipeService, UserService
from meal_planner.db.models import Recipe as DBRecipe

router = APIRouter()


class RecipeCreate(BaseModel):
    """Request model for creating a recipe."""
    title: str
    description: Optional[str] = None
    ingredients: List[str]
    instructions: List[str]
    meal_types: List[str] = []
    tags: List[str] = []
    dietary_restrictions: List[str] = []
    appliances: List[str] = []
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None


class RecipeResponse(BaseModel):
    """Response model for recipes."""
    id: str
    title: str
    description: Optional[str]
    ingredients: List
    instructions: List[str]
    meal_types: List[str]
    tags: List[str]
    dietary_restrictions: List[str]
    appliances: List[str]
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    total_time_minutes: Optional[int]
    servings: Optional[int]
    source_url: Optional[str]
    image_url: Optional[str]
    notes: Optional[str]
    created_at: str
    updated_at: str
    
    @classmethod
    def from_db_recipe(cls, recipe: DBRecipe) -> "RecipeResponse":
        """Convert database recipe to response model."""
        return cls(
            id=str(recipe.id),
            title=recipe.title,
            description=recipe.description,
            ingredients=recipe.ingredients,
            instructions=recipe.instructions,
            meal_types=recipe.meal_types,
            tags=recipe.tags,
            dietary_restrictions=recipe.dietary_restrictions,
            appliances=recipe.appliances,
            prep_time_minutes=recipe.prep_time_minutes,
            cook_time_minutes=recipe.cook_time_minutes,
            total_time_minutes=recipe.total_time_minutes,
            servings=recipe.servings,
            source_url=recipe.source_url,
            image_url=recipe.image_url,
            notes=recipe.notes,
            created_at=recipe.created_at.isoformat(),
            updated_at=recipe.updated_at.isoformat()
        )


@router.post("/recipes-db", response_model=RecipeResponse)
async def create_recipe_db(
    recipe_data: RecipeCreate,
    recipe_service: RecipeService = Depends(get_recipe_service),
    user_service: UserService = Depends(get_user_service)
):
    """Create a new recipe in the database."""
    # For now, create a default user if none exists
    # In a real app, you'd get this from authentication
    default_user_email = "demo@example.com"
    user = await user_service.get_user_by_email(default_user_email)
    
    if not user:
        user = await user_service.create_user(
            email=default_user_email,
            full_name="Demo User"
        )
    
    # Create recipe
    recipe = await recipe_service.create_recipe(
        user_id=user.id,
        recipe_data=recipe_data.model_dump()
    )
    
    return RecipeResponse.from_db_recipe(recipe)


@router.get("/recipes-db", response_model=List[RecipeResponse])
async def list_recipes_db(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """List recipes from database."""
    recipes = await recipe_service.list_recipes(
        limit=limit,
        offset=offset,
        include_public=True
    )
    
    return [RecipeResponse.from_db_recipe(recipe) for recipe in recipes]


@router.get("/recipes-db/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_db(
    recipe_id: str,
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Get a recipe by ID from database."""
    try:
        recipe_uuid = uuid.UUID(recipe_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid recipe ID format")
    
    recipe = await recipe_service.get_recipe_by_id(recipe_uuid)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return RecipeResponse.from_db_recipe(recipe)


@router.get("/recipes-db/search", response_model=List[RecipeResponse])
async def search_recipes_db(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Search recipes in database."""
    recipes = await recipe_service.search_recipes(
        query=q,
        limit=limit
    )
    
    return [RecipeResponse.from_db_recipe(recipe) for recipe in recipes]


@router.delete("/recipes-db/{recipe_id}")
async def delete_recipe_db(
    recipe_id: str,
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Delete a recipe from database."""
    try:
        recipe_uuid = uuid.UUID(recipe_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid recipe ID format")
    
    success = await recipe_service.delete_recipe(recipe_uuid)
    
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return {"message": "Recipe deleted successfully"}