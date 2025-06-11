"""User-related API endpoints."""

import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from loguru import logger

from meal_planner.core.models import User, UserFavorite, UserPreferences

router = APIRouter()


# In-memory storage for users and preferences (for MVP)
# In a real application, this would be replaced with a database
users_db = {}
preferences_db = {}
favorites_db = {}


@router.post("/users", response_model=User)
async def create_user(user: User):
    """Create a new user.
    
    Args:
        user: User to create
        
    Returns:
        Created user
    """
    # Check if user already exists
    if str(user.id) in users_db or any(u.email == user.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Save user
    users_db[str(user.id)] = user
    
    return user


@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: uuid.UUID = Path(..., description="User ID")
):
    """Get a user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        User
    """
    user = users_db.get(str(user_id))
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.put("/users/{user_id}", response_model=User)
async def update_user(
    updated_user: User,
    user_id: uuid.UUID = Path(..., description="User ID")
):
    """Update a user.
    
    Args:
        updated_user: Updated user
        user_id: User ID
        
    Returns:
        Updated user
    """
    # Check if user exists
    if str(user_id) not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user ID matches path parameter
    if updated_user.id != user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    
    # Save updated user
    users_db[str(user_id)] = updated_user
    
    return updated_user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: uuid.UUID = Path(..., description="User ID")
):
    """Delete a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Deletion status
    """
    # Check if user exists
    if str(user_id) not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete user
    del users_db[str(user_id)]
    
    # Delete user preferences
    if str(user_id) in preferences_db:
        del preferences_db[str(user_id)]
    
    # Delete user favorites
    if str(user_id) in favorites_db:
        del favorites_db[str(user_id)]
    
    return {"message": "User deleted successfully"}


@router.post("/users/{user_id}/preferences", response_model=UserPreferences)
async def set_user_preferences(
    preferences: UserPreferences,
    user_id: uuid.UUID = Path(..., description="User ID")
):
    """Set user preferences.
    
    Args:
        preferences: User preferences
        user_id: User ID
        
    Returns:
        User preferences
    """
    # Check if user exists
    if str(user_id) not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Save preferences
    preferences_db[str(user_id)] = preferences
    
    return preferences


@router.get("/users/{user_id}/preferences", response_model=UserPreferences)
async def get_user_preferences(
    user_id: uuid.UUID = Path(..., description="User ID")
):
    """Get user preferences.
    
    Args:
        user_id: User ID
        
    Returns:
        User preferences
    """
    # Check if user exists
    if str(user_id) not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if preferences exist
    if str(user_id) not in preferences_db:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    return preferences_db[str(user_id)]


@router.post("/users/{user_id}/favorites/{recipe_id}", response_model=UserFavorite)
async def add_favorite(
    user_id: uuid.UUID = Path(..., description="User ID"),
    recipe_id: uuid.UUID = Path(..., description="Recipe ID"),
    notes: Optional[str] = None
):
    """Add a recipe to user favorites.
    
    Args:
        user_id: User ID
        recipe_id: Recipe ID
        notes: Optional notes
        
    Returns:
        User favorite
    """
    # Check if user exists
    if str(user_id) not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create favorite
    favorite = UserFavorite(
        recipe_id=recipe_id,
        notes=notes
    )
    
    # Initialize user favorites if not exists
    if str(user_id) not in favorites_db:
        favorites_db[str(user_id)] = []
    
    # Check if recipe is already a favorite
    if any(f.recipe_id == recipe_id for f in favorites_db[str(user_id)]):
        raise HTTPException(status_code=400, detail="Recipe is already a favorite")
    
    # Add to favorites
    favorites_db[str(user_id)].append(favorite)
    
    return favorite


@router.get("/users/{user_id}/favorites", response_model=List[UserFavorite])
async def list_favorites(
    user_id: uuid.UUID = Path(..., description="User ID")
):
    """List user favorites.
    
    Args:
        user_id: User ID
        
    Returns:
        List of user favorites
    """
    # Check if user exists
    if str(user_id) not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return favorites
    return favorites_db.get(str(user_id), [])


@router.delete("/users/{user_id}/favorites/{recipe_id}")
async def remove_favorite(
    user_id: uuid.UUID = Path(..., description="User ID"),
    recipe_id: uuid.UUID = Path(..., description="Recipe ID")
):
    """Remove a recipe from user favorites.
    
    Args:
        user_id: User ID
        recipe_id: Recipe ID
        
    Returns:
        Removal status
    """
    # Check if user exists
    if str(user_id) not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has favorites
    if str(user_id) not in favorites_db:
        raise HTTPException(status_code=404, detail="User has no favorites")
    
    # Find favorite
    favorites = favorites_db[str(user_id)]
    favorite_idx = next((i for i, f in enumerate(favorites) if f.recipe_id == recipe_id), None)
    
    if favorite_idx is None:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    # Remove favorite
    favorites.pop(favorite_idx)
    
    return {"message": "Favorite removed successfully"}
