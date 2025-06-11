"""Tests for database services."""

import pytest
import uuid
from datetime import datetime, timedelta

from meal_planner.db.services import UserService, RecipeService, MealPlanService


class TestUserService:
    """Test user service operations."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_service):
        """Test creating a new user."""
        user = await user_service.create_user(
            email="newuser@example.com",
            full_name="New User"
        )
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert user.is_active is True
        assert user.created_at is not None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_service, test_user):
        """Test getting user by ID."""
        found_user = await user_service.get_user_by_id(test_user.id)
        
        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.email == test_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_service, test_user):
        """Test getting user by email."""
        found_user = await user_service.get_user_by_email(test_user.email)
        
        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.email == test_user.email
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, user_service):
        """Test getting non-existent user returns None."""
        fake_id = uuid.uuid4()
        user = await user_service.get_user_by_id(fake_id)
        assert user is None
        
        user = await user_service.get_user_by_email("nonexistent@example.com")
        assert user is None
    
    @pytest.mark.asyncio
    async def test_update_user(self, user_service, test_user):
        """Test updating user information."""
        updated_user = await user_service.update_user(
            test_user.id,
            full_name="Updated Name",
            is_active=False
        )
        
        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.is_active is False
        assert updated_user.email == test_user.email  # Unchanged
    
    @pytest.mark.asyncio
    async def test_delete_user(self, user_service, test_user):
        """Test deleting a user."""
        success = await user_service.delete_user(test_user.id)
        assert success is True
        
        # Verify user is deleted
        deleted_user = await user_service.get_user_by_id(test_user.id)
        assert deleted_user is None


class TestRecipeService:
    """Test recipe service operations."""
    
    @pytest.mark.asyncio
    async def test_create_recipe(self, recipe_service, test_user, test_recipe_data):
        """Test creating a new recipe."""
        recipe = await recipe_service.create_recipe(
            user_id=test_user.id,
            recipe_data=test_recipe_data
        )
        
        assert recipe.id is not None
        assert recipe.user_id == test_user.id
        assert recipe.title == test_recipe_data["title"]
        assert recipe.total_time_minutes == 25  # prep + cook time
        assert recipe.ingredients == test_recipe_data["ingredients"]
        assert recipe.instructions == test_recipe_data["instructions"]
    
    @pytest.mark.asyncio
    async def test_create_recipe_without_times(self, recipe_service, test_user):
        """Test creating recipe without prep/cook times."""
        recipe_data = {
            "title": "No Time Recipe",
            "ingredients": ["ingredient1"],
            "instructions": ["step1"],
            "meal_types": ["lunch"]
        }
        
        recipe = await recipe_service.create_recipe(
            user_id=test_user.id,
            recipe_data=recipe_data
        )
        
        assert recipe.total_time_minutes is None
        assert recipe.prep_time_minutes is None
        assert recipe.cook_time_minutes is None
    
    @pytest.mark.asyncio
    async def test_get_recipe_by_id(self, recipe_service, test_recipe):
        """Test getting recipe by ID."""
        found_recipe = await recipe_service.get_recipe_by_id(test_recipe.id)
        
        assert found_recipe is not None
        assert found_recipe.id == test_recipe.id
        assert found_recipe.title == test_recipe.title
        assert found_recipe.user is not None  # Should load user relationship
    
    @pytest.mark.asyncio
    async def test_list_recipes(self, recipe_service, test_recipe):
        """Test listing recipes with pagination."""
        recipes = await recipe_service.list_recipes(limit=10, offset=0)
        
        assert len(recipes) >= 1
        assert any(r.id == test_recipe.id for r in recipes)
    
    @pytest.mark.asyncio
    async def test_list_recipes_by_user(self, recipe_service, test_user, test_recipe):
        """Test listing recipes for specific user."""
        recipes = await recipe_service.list_recipes(user_id=test_user.id)
        
        assert len(recipes) >= 1
        assert all(r.user_id == test_user.id for r in recipes)
    
    @pytest.mark.asyncio
    async def test_search_recipes(self, recipe_service, test_recipe):
        """Test searching recipes by title."""
        recipes = await recipe_service.search_recipes("Test Pasta")
        
        assert len(recipes) >= 1
        assert any(r.id == test_recipe.id for r in recipes)
    
    @pytest.mark.asyncio
    async def test_search_recipes_no_results(self, recipe_service):
        """Test searching with no matching results."""
        recipes = await recipe_service.search_recipes("NonexistentRecipe123")
        assert len(recipes) == 0
    
    @pytest.mark.asyncio
    async def test_update_recipe(self, recipe_service, test_recipe):
        """Test updating recipe."""
        update_data = {
            "title": "Updated Pasta",
            "prep_time_minutes": 20,
            "cook_time_minutes": 25
        }
        
        updated_recipe = await recipe_service.update_recipe(
            test_recipe.id,
            update_data
        )
        
        assert updated_recipe is not None
        assert updated_recipe.title == "Updated Pasta"
        assert updated_recipe.total_time_minutes == 45  # Updated total
    
    @pytest.mark.asyncio
    async def test_delete_recipe(self, recipe_service, test_recipe):
        """Test deleting recipe."""
        success = await recipe_service.delete_recipe(test_recipe.id)
        assert success is True
        
        # Verify recipe is deleted
        deleted_recipe = await recipe_service.get_recipe_by_id(test_recipe.id)
        assert deleted_recipe is None
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_filters(self, recipe_service, test_recipe):
        """Test filtering recipes by various criteria."""
        # Filter by meal type
        recipes = await recipe_service.get_recipes_by_filters(
            meal_types=["dinner"]
        )
        assert len(recipes) >= 1
        
        # Filter by dietary restriction
        recipes = await recipe_service.get_recipes_by_filters(
            dietary_restrictions=["vegetarian"]
        )
        assert len(recipes) >= 1
        
        # Filter by max prep time
        recipes = await recipe_service.get_recipes_by_filters(
            max_prep_time=15
        )
        assert len(recipes) >= 1


class TestMealPlanService:
    """Test meal plan service operations."""
    
    @pytest.mark.asyncio
    async def test_create_meal_plan(self, meal_plan_service, test_user, test_meal_plan_data):
        """Test creating a new meal plan."""
        meal_plan = await meal_plan_service.create_meal_plan(
            user_id=test_user.id,
            meal_plan_data=test_meal_plan_data
        )
        
        assert meal_plan.id is not None
        assert meal_plan.user_id == test_user.id
        assert meal_plan.name == test_meal_plan_data["name"]
        assert meal_plan.nutrition_goal == test_meal_plan_data["nutrition_goal"]
    
    @pytest.mark.asyncio
    async def test_get_meal_plan_by_id(self, meal_plan_service, test_user, test_meal_plan_data):
        """Test getting meal plan by ID."""
        # Create meal plan
        meal_plan = await meal_plan_service.create_meal_plan(
            user_id=test_user.id,
            meal_plan_data=test_meal_plan_data
        )
        
        # Get meal plan
        found_plan = await meal_plan_service.get_meal_plan_by_id(meal_plan.id)
        
        assert found_plan is not None
        assert found_plan.id == meal_plan.id
        assert found_plan.user is not None  # Should load user relationship
    
    @pytest.mark.asyncio
    async def test_list_meal_plans(self, meal_plan_service, test_user, test_meal_plan_data):
        """Test listing meal plans."""
        # Create meal plan
        meal_plan = await meal_plan_service.create_meal_plan(
            user_id=test_user.id,
            meal_plan_data=test_meal_plan_data
        )
        
        # List meal plans
        meal_plans = await meal_plan_service.list_meal_plans(user_id=test_user.id)
        
        assert len(meal_plans) >= 1
        assert any(mp.id == meal_plan.id for mp in meal_plans)
    
    @pytest.mark.asyncio
    async def test_add_recipe_to_meal_plan(self, meal_plan_service, test_user, test_recipe, test_meal_plan_data):
        """Test adding recipe to meal plan."""
        # Create meal plan
        meal_plan = await meal_plan_service.create_meal_plan(
            user_id=test_user.id,
            meal_plan_data=test_meal_plan_data
        )
        
        # Add recipe to meal plan
        scheduled_date = datetime.now()
        meal_plan_recipe = await meal_plan_service.add_recipe_to_meal_plan(
            meal_plan_id=meal_plan.id,
            recipe_id=test_recipe.id,
            scheduled_date=scheduled_date,
            meal_type="dinner",
            servings_multiplier=1.5,
            notes="Extra servings for leftovers"
        )
        
        assert meal_plan_recipe.id is not None
        assert meal_plan_recipe.meal_plan_id == meal_plan.id
        assert meal_plan_recipe.recipe_id == test_recipe.id
        assert meal_plan_recipe.meal_type == "dinner"
        assert meal_plan_recipe.servings_multiplier == 1.5
    
    @pytest.mark.asyncio
    async def test_create_grocery_list(self, meal_plan_service, test_user, test_meal_plan_data):
        """Test creating grocery list for meal plan."""
        # Create meal plan
        meal_plan = await meal_plan_service.create_meal_plan(
            user_id=test_user.id,
            meal_plan_data=test_meal_plan_data
        )
        
        # Create grocery list
        items = [
            {"name": "Pasta", "quantity": "1 lb"},
            {"name": "Tomato Sauce", "quantity": "2 cans"},
            {"name": "Cheese", "quantity": "1 cup"}
        ]
        
        grocery_list = await meal_plan_service.create_grocery_list(
            meal_plan_id=meal_plan.id,
            user_id=test_user.id,
            items=items,
            name="Weekly Groceries",
            total_estimated_cost=45.50
        )
        
        assert grocery_list.id is not None
        assert grocery_list.meal_plan_id == meal_plan.id
        assert grocery_list.items == items
        assert grocery_list.total_estimated_cost == 45.50
    
    @pytest.mark.asyncio
    async def test_delete_meal_plan(self, meal_plan_service, test_user, test_meal_plan_data):
        """Test deleting meal plan."""
        # Create meal plan
        meal_plan = await meal_plan_service.create_meal_plan(
            user_id=test_user.id,
            meal_plan_data=test_meal_plan_data
        )
        
        # Delete meal plan
        success = await meal_plan_service.delete_meal_plan(meal_plan.id)
        assert success is True
        
        # Verify meal plan is deleted
        deleted_plan = await meal_plan_service.get_meal_plan_by_id(meal_plan.id)
        assert deleted_plan is None