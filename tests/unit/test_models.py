"""Tests for core models."""

import json
import tempfile
import time
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from meal_planner.core.models import (
    DietaryRestriction, GroceryItem, GroceryList, Ingredient, MealPlan, MealPlanDay,
    MealType, NutritionGoal, NutritionInfo, OCREngine, OCRResult, Recipe,
    RecipeExtractionResponse, User, UserFavorite, UserPreferences
)


class TestRecipe:
    """Tests for Recipe model."""
    
    def test_recipe_creation(self):
        """Test creating a recipe."""
        recipe = Recipe(
            title="Test Recipe",
            ingredients=["Ingredient 1", "Ingredient 2"],
            instructions=["Step 1", "Step 2"],
            meal_types=[MealType.DINNER]
        )
        
        assert recipe.title == "Test Recipe"
        assert recipe.ingredients == ["Ingredient 1", "Ingredient 2"]
        assert recipe.instructions == ["Step 1", "Step 2"]
        assert recipe.meal_types == [MealType.DINNER]
        assert recipe.id is not None
        assert recipe.created_at is not None
        assert recipe.updated_at is not None
    
    def test_recipe_with_structured_ingredients(self):
        """Test creating a recipe with structured ingredients."""
        recipe = Recipe(
            title="Test Recipe",
            ingredients=[
                Ingredient(name="Flour", quantity=2.0, unit="cups"),
                Ingredient(name="Sugar", quantity=1.0, unit="cup")
            ],
            instructions=["Step 1", "Step 2"],
            meal_types=[MealType.DESSERT]
        )
        
        assert recipe.title == "Test Recipe"
        assert len(recipe.ingredients) == 2
        assert recipe.ingredients[0].name == "Flour"
        assert recipe.ingredients[0].quantity == 2.0
        assert recipe.ingredients[0].unit == "cups"
        assert recipe.ingredients[1].name == "Sugar"
        assert recipe.ingredients[1].quantity == 1.0
        assert recipe.ingredients[1].unit == "cup"
    
    def test_recipe_save_and_load(self, tmp_path):
        """Test saving and loading a recipe."""
        recipe = Recipe(
            title="Test Recipe",
            ingredients=["Ingredient 1", "Ingredient 2"],
            instructions=["Step 1", "Step 2"],
            meal_types=[MealType.DINNER]
        )
        
        # Save recipe
        file_path = recipe.save_to_file(tmp_path)
        
        # Check file exists
        assert file_path.exists()
        
        # Load recipe
        loaded_recipe = Recipe.load_from_file(file_path)
        
        # Check loaded recipe
        assert loaded_recipe.id == recipe.id
        assert loaded_recipe.title == recipe.title
        assert loaded_recipe.ingredients == recipe.ingredients
        assert loaded_recipe.instructions == recipe.instructions
        assert loaded_recipe.meal_types == recipe.meal_types
        assert loaded_recipe.created_at == recipe.created_at
        assert loaded_recipe.updated_at == recipe.updated_at


class TestOCRResult:
    """Tests for OCRResult model."""
    
    def test_ocr_result_creation(self):
        """Test creating an OCR result."""
        result = OCRResult(
            text="Test OCR text",
            confidence=0.9,
            engine_used=OCREngine.PYMUPDF,
            processing_time=0.5
        )
        
        assert result.text == "Test OCR text"
        assert result.confidence == 0.9
        assert result.engine_used == OCREngine.PYMUPDF
        assert result.processing_time == 0.5
        assert result.warnings == []
    
    def test_ocr_result_with_warnings(self):
        """Test creating an OCR result with warnings."""
        result = OCRResult(
            text="Test OCR text",
            confidence=0.7,
            engine_used=OCREngine.MARKER,
            processing_time=0.8,
            warnings=["Low quality image", "Text may be incomplete"]
        )
        
        assert result.text == "Test OCR text"
        assert result.confidence == 0.7
        assert result.engine_used == OCREngine.MARKER
        assert result.processing_time == 0.8
        assert result.warnings == ["Low quality image", "Text may be incomplete"]


class TestRecipeExtractionResponse:
    """Tests for RecipeExtractionResponse model."""
    
    def test_extraction_response_creation(self):
        """Test creating a recipe extraction response."""
        recipe = Recipe(
            title="Test Recipe",
            ingredients=["Ingredient 1", "Ingredient 2"],
            instructions=["Step 1", "Step 2"],
            meal_types=[MealType.DINNER]
        )
        
        ocr_result = OCRResult(
            text="Test OCR text",
            confidence=0.9,
            engine_used=OCREngine.PYMUPDF,
            processing_time=0.5
        )
        
        response = RecipeExtractionResponse(
            recipe=recipe,
            ocr_result=ocr_result,
            processing_time=1.2,
            warnings=["Warning 1", "Warning 2"]
        )
        
        assert response.recipe == recipe
        assert response.ocr_result == ocr_result
        assert response.processing_time == 1.2
        assert response.warnings == ["Warning 1", "Warning 2"]


class TestUser:
    """Tests for User model."""
    
    def test_user_creation(self):
        """Test creating a user."""
        user = User(
            email="user@example.com",
            name="Test User"
        )
        
        assert user.email == "user@example.com"
        assert user.name == "Test User"
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None


class TestUserPreferences:
    """Tests for UserPreferences model."""
    
    def test_user_preferences_creation(self):
        """Test creating user preferences."""
        preferences = UserPreferences(
            favorite_cuisines=["Italian", "Mexican"],
            disliked_ingredients=["cilantro", "olives"],
            dietary_restrictions=[DietaryRestriction.VEGETARIAN],
            meal_preferences={"weekdays": [MealType.DINNER], "weekends": [MealType.BREAKFAST, MealType.LUNCH]},
            budget_per_meal=Decimal("10.00"),
            servings_per_meal=2
        )
        
        assert preferences.favorite_cuisines == ["Italian", "Mexican"]
        assert preferences.disliked_ingredients == ["cilantro", "olives"]
        assert preferences.dietary_restrictions == [DietaryRestriction.VEGETARIAN]
        assert preferences.meal_preferences == {"weekdays": [MealType.DINNER], "weekends": [MealType.BREAKFAST, MealType.LUNCH]}
        assert preferences.budget_per_meal == Decimal("10.00")
        assert preferences.servings_per_meal == 2


class TestMealPlan:
    """Tests for MealPlan model."""
    
    def test_meal_plan_creation(self):
        """Test creating a meal plan."""
        user_id = uuid.uuid4()
        
        meal_plan = MealPlan(
            user_id=user_id,
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 7),
            days=[
                MealPlanDay(
                    date=date(2025, 6, 1),
                    breakfast=uuid.uuid4(),
                    lunch=uuid.uuid4(),
                    dinner=uuid.uuid4()
                ),
                MealPlanDay(
                    date=date(2025, 6, 2),
                    breakfast=uuid.uuid4(),
                    lunch=uuid.uuid4(),
                    dinner=uuid.uuid4()
                )
            ],
            nutrition_goal=NutritionGoal.WEIGHT_LOSS,
            total_estimated_cost=Decimal("50.00")
        )
        
        assert meal_plan.user_id == user_id
        assert meal_plan.start_date == date(2025, 6, 1)
        assert meal_plan.end_date == date(2025, 6, 7)
        assert len(meal_plan.days) == 2
        assert meal_plan.days[0].date == date(2025, 6, 1)
        assert meal_plan.days[1].date == date(2025, 6, 2)
        assert meal_plan.nutrition_goal == NutritionGoal.WEIGHT_LOSS
        assert meal_plan.total_estimated_cost == Decimal("50.00")
        assert meal_plan.id is not None
        assert meal_plan.created_at is not None
        assert meal_plan.updated_at is not None


class TestGroceryList:
    """Tests for GroceryList model."""
    
    def test_grocery_list_creation(self):
        """Test creating a grocery list."""
        meal_plan_id = uuid.uuid4()
        user_id = uuid.uuid4()
        recipe_id = uuid.uuid4()
        
        grocery_list = GroceryList(
            meal_plan_id=meal_plan_id,
            user_id=user_id,
            items=[
                GroceryItem(
                    name="Flour",
                    quantity=2.0,
                    unit="cups",
                    estimated_cost=Decimal("2.50"),
                    recipe_ids=[recipe_id],
                    category="Baking"
                ),
                GroceryItem(
                    name="Eggs",
                    quantity=12.0,
                    unit="",
                    estimated_cost=Decimal("3.00"),
                    recipe_ids=[recipe_id],
                    category="Dairy"
                )
            ],
            total_estimated_cost=Decimal("5.50")
        )
        
        assert grocery_list.meal_plan_id == meal_plan_id
        assert grocery_list.user_id == user_id
        assert len(grocery_list.items) == 2
        assert grocery_list.items[0].name == "Flour"
        assert grocery_list.items[0].quantity == 2.0
        assert grocery_list.items[0].unit == "cups"
        assert grocery_list.items[0].estimated_cost == Decimal("2.50")
        assert grocery_list.items[0].recipe_ids == [recipe_id]
        assert grocery_list.items[0].category == "Baking"
        assert grocery_list.items[1].name == "Eggs"
        assert grocery_list.items[1].quantity == 12.0
        assert grocery_list.items[1].unit == ""
        assert grocery_list.items[1].estimated_cost == Decimal("3.00")
        assert grocery_list.items[1].recipe_ids == [recipe_id]
        assert grocery_list.items[1].category == "Dairy"
        assert grocery_list.total_estimated_cost == Decimal("5.50")
        assert grocery_list.id is not None
        assert grocery_list.created_at is not None
        assert grocery_list.updated_at is not None
