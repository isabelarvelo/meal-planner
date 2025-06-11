"""Meal plan-related API endpoints."""

import uuid
from datetime import date, datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from loguru import logger

from meal_planner.api.dependencies import get_meal_plan_service
from meal_planner.core.models import (
    GroceryList, MealPlan, MealPlanRequest, MealPlanResponse, MealType, NutritionGoal
)
from meal_planner.core.services import MealPlanService

router = APIRouter()


# In-memory storage for meal plans and grocery lists (for MVP)
# In a real application, this would be replaced with a database
meal_plans_db = {}
grocery_lists_db = {}


@router.post("/meal-plans", response_model=MealPlanResponse)
async def generate_meal_plan(
    request: MealPlanRequest,
    meal_plan_service: MealPlanService = Depends(get_meal_plan_service)
):
    """Generate a meal plan.
    
    Args:
        request: Meal plan request
        meal_plan_service: Meal plan service
        
    Returns:
        Meal plan response
    """
    # Generate meal plan
    start_time = datetime.now()
    
    meal_plan_data = await meal_plan_service.generate_meal_plan(
        user_id=request.user_id,
        start_date=request.start_date,
        end_date=request.end_date,
        preferences=request.preferences,
        nutrition_goal=request.nutrition_goal,
        budget_limit=request.budget_limit
    )
    
    # Check for errors
    if "error" in meal_plan_data:
        raise HTTPException(
            status_code=400,
            detail=meal_plan_data["message"]
        )
    
    # Create meal plan
    meal_plan = MealPlan(
        user_id=request.user_id,
        start_date=request.start_date,
        end_date=request.end_date,
        days=meal_plan_data["days"],
        nutrition_goal=request.nutrition_goal,
        total_estimated_cost=meal_plan_data.get("total_cost")
    )
    
    # Create grocery list
    grocery_list = GroceryList(
        meal_plan_id=meal_plan.id,
        user_id=request.user_id,
        items=meal_plan_data["grocery_items"],
        total_estimated_cost=meal_plan_data.get("total_cost")
    )
    
    # Save meal plan and grocery list
    meal_plans_db[str(meal_plan.id)] = meal_plan
    grocery_lists_db[str(grocery_list.id)] = grocery_list
    
    # Create response
    response = MealPlanResponse(
        meal_plan=meal_plan,
        grocery_list=grocery_list,
        total_cost=meal_plan_data.get("total_cost"),
        nutrition_summary=meal_plan_data.get("nutrition_summary", {}),
        processing_time=(datetime.now() - start_time).total_seconds()
    )
    
    return response


@router.get("/meal-plans/{meal_plan_id}", response_model=MealPlan)
async def get_meal_plan(
    meal_plan_id: uuid.UUID = Path(..., description="Meal plan ID")
):
    """Get a meal plan by ID.
    
    Args:
        meal_plan_id: Meal plan ID
        
    Returns:
        Meal plan
    """
    meal_plan = meal_plans_db.get(str(meal_plan_id))
    
    if meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    
    return meal_plan


@router.get("/meal-plans", response_model=List[MealPlan])
async def list_meal_plans(
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID")
):
    """List meal plans.
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        List of meal plans
    """
    if user_id:
        # Filter by user ID
        return [mp for mp in meal_plans_db.values() if mp.user_id == user_id]
    else:
        # Return all meal plans
        return list(meal_plans_db.values())


@router.delete("/meal-plans/{meal_plan_id}")
async def delete_meal_plan(
    meal_plan_id: uuid.UUID = Path(..., description="Meal plan ID")
):
    """Delete a meal plan.
    
    Args:
        meal_plan_id: Meal plan ID
        
    Returns:
        Deletion status
    """
    # Check if meal plan exists
    if str(meal_plan_id) not in meal_plans_db:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    
    # Delete meal plan
    del meal_plans_db[str(meal_plan_id)]
    
    # Delete associated grocery lists
    for gl_id, gl in list(grocery_lists_db.items()):
        if gl.meal_plan_id == meal_plan_id:
            del grocery_lists_db[gl_id]
    
    return {"message": "Meal plan deleted successfully"}


@router.get("/grocery-lists/{grocery_list_id}", response_model=GroceryList)
async def get_grocery_list(
    grocery_list_id: uuid.UUID = Path(..., description="Grocery list ID")
):
    """Get a grocery list by ID.
    
    Args:
        grocery_list_id: Grocery list ID
        
    Returns:
        Grocery list
    """
    grocery_list = grocery_lists_db.get(str(grocery_list_id))
    
    if grocery_list is None:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    
    return grocery_list


@router.get("/meal-plans/{meal_plan_id}/grocery-list", response_model=GroceryList)
async def get_meal_plan_grocery_list(
    meal_plan_id: uuid.UUID = Path(..., description="Meal plan ID")
):
    """Get the grocery list for a meal plan.
    
    Args:
        meal_plan_id: Meal plan ID
        
    Returns:
        Grocery list
    """
    # Check if meal plan exists
    if str(meal_plan_id) not in meal_plans_db:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    
    # Find associated grocery list
    for gl in grocery_lists_db.values():
        if gl.meal_plan_id == meal_plan_id:
            return gl
    
    raise HTTPException(status_code=404, detail="Grocery list not found for this meal plan")
