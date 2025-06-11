"""Tests for core services."""

import os
import tempfile
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from meal_planner.core.models import (
    MealType, OCREngine, OCRResult, Recipe, RecipeExtractionResponse
)
from meal_planner.core.services import (
    MealPlanService, RecipeExtractionService, RecipeStorageService
)
from meal_planner.ml.llm.base import BaseLLMProvider
from meal_planner.ml.ocr.base import BaseOCREngine


class TestRecipeExtractionService:
    """Tests for RecipeExtractionService."""
    
    @pytest.fixture
    def mock_ocr_primary(self):
        """Create a mock primary OCR engine."""
        mock = Mock(spec=BaseOCREngine)
        mock.extract_text = AsyncMock(return_value=OCRResult(
            text="Test recipe text",
            confidence=0.9,
            engine_used=OCREngine.PYMUPDF,
            processing_time=0.5
        ))
        mock.get_name.return_value = "MockOCR"
        return mock
    
    @pytest.fixture
    def mock_ocr_fallback(self):
        """Create a mock fallback OCR engine."""
        mock = Mock(spec=BaseOCREngine)
        mock.extract_text = AsyncMock(return_value=OCRResult(
            text="Fallback recipe text",
            confidence=0.7,
            engine_used=OCREngine.MARKER,
            processing_time=0.8
        ))
        mock.get_name.return_value = "MockFallbackOCR"
        return mock
    
    @pytest.fixture
    def mock_llm_provider(self):
        """Create a mock LLM provider."""
        mock = Mock(spec=BaseLLMProvider)
        mock.evaluate_ocr_quality = AsyncMock(return_value={
            "quality_score": 0.9,
            "is_recipe_content": True,
            "detected_issues": [],
            "recommended_action": "use_result"
        })
        mock.structure_recipe = AsyncMock(return_value=Recipe(
            title="Test Recipe",
            ingredients=["Ingredient 1", "Ingredient 2"],
            instructions=["Step 1", "Step 2"],
            meal_types=[MealType.DINNER]
        ))
        return mock
    
    @pytest.fixture
    def extraction_service(self, mock_ocr_primary, mock_ocr_fallback, mock_llm_provider):
        """Create a recipe extraction service."""
        return RecipeExtractionService(
            ocr_primary=mock_ocr_primary,
            ocr_fallback=mock_ocr_fallback,
            llm_provider=mock_llm_provider
        )
    
    @pytest.mark.asyncio
    async def test_extract_recipe(self, extraction_service, tmp_path):
        """Test extracting a recipe."""
        # Create a test file
        test_file = tmp_path / "test_recipe.pdf"
        test_file.write_text("Test recipe content")
        
        # Extract recipe
        response = await extraction_service.extract_recipe(test_file)
        
        # Check response
        assert isinstance(response, RecipeExtractionResponse)
        assert response.recipe.title == "Test Recipe"
        assert len(response.recipe.ingredients) == 2
        assert len(response.recipe.instructions) == 2
        assert response.recipe.meal_types == [MealType.DINNER]
        assert response.recipe.source_file == str(test_file)
        assert response.ocr_result.confidence == 0.9
        assert response.ocr_result.engine_used == OCREngine.PYMUPDF
    
    @pytest.mark.asyncio
    async def test_extract_recipe_with_fallback(self, extraction_service, mock_ocr_primary, tmp_path):
        """Test extracting a recipe with fallback OCR."""
        # Create a test file
        test_file = tmp_path / "test_recipe.pdf"
        test_file.write_text("Test recipe content")
        
        # Make primary OCR return low confidence
        mock_ocr_primary.extract_text = AsyncMock(return_value=OCRResult(
            text="Low quality text",
            confidence=0.3,
            engine_used=OCREngine.PYMUPDF,
            processing_time=0.5
        ))
        
        # Extract recipe
        response = await extraction_service.extract_recipe(test_file)
        
        # Check response
        assert isinstance(response, RecipeExtractionResponse)
        assert response.ocr_result.confidence == 0.7
        assert response.ocr_result.engine_used == OCREngine.MARKER
        assert len(response.warnings) > 0


class TestRecipeStorageService:
    """Tests for RecipeStorageService."""
    
    @pytest.fixture
    def storage_service(self, tmp_path):
        """Create a recipe storage service."""
        return RecipeStorageService(recipes_dir=tmp_path)
    
    @pytest.fixture
    def sample_recipe(self):
        """Create a sample recipe."""
        return Recipe(
            title="Test Recipe",
            ingredients=["Ingredient 1", "Ingredient 2"],
            instructions=["Step 1", "Step 2"],
            meal_types=[MealType.DINNER]
        )
    
    def test_save_recipe(self, storage_service, sample_recipe):
        """Test saving a recipe."""
        # Save recipe
        file_path = storage_service.save_recipe(sample_recipe)
        
        # Check file exists
        assert file_path.exists()
        
        # Check file content
        with open(file_path, "r") as f:
            content = f.read()
            assert "Test Recipe" in content
            assert "Ingredient 1" in content
            assert "Step 1" in content
    
    def test_load_recipe(self, storage_service, sample_recipe):
        """Test loading a recipe."""
        # Save recipe
        file_path = storage_service.save_recipe(sample_recipe)
        
        # Load recipe
        loaded_recipe = storage_service.load_recipe(sample_recipe.id)
        
        # Check loaded recipe
        assert loaded_recipe is not None
        assert loaded_recipe.id == sample_recipe.id
        assert loaded_recipe.title == sample_recipe.title
        assert loaded_recipe.ingredients == sample_recipe.ingredients
        assert loaded_recipe.instructions == sample_recipe.instructions
    
    def test_delete_recipe(self, storage_service, sample_recipe):
        """Test deleting a recipe."""
        # Save recipe
        file_path = storage_service.save_recipe(sample_recipe)
        
        # Delete recipe
        success = storage_service.delete_recipe(sample_recipe.id)
        
        # Check deletion
        assert success
        assert not file_path.exists()
    
    def test_list_recipes(self, storage_service):
        """Test listing recipes."""
        # Create and save recipes
        recipes = []
        for i in range(5):
            recipe = Recipe(
                title=f"Recipe {i}",
                ingredients=[f"Ingredient {i}"],
                instructions=[f"Step {i}"],
                meal_types=[MealType.DINNER]
            )
            storage_service.save_recipe(recipe)
            recipes.append(recipe)
        
        # List recipes
        listed_recipes = storage_service.list_recipes()
        
        # Check listed recipes
        assert len(listed_recipes) == 5
        for recipe in recipes:
            assert any(r.id == recipe.id for r in listed_recipes)
    
    def test_search_recipes(self, storage_service):
        """Test searching recipes."""
        # Create and save recipes
        recipes = [
            Recipe(
                title="Pasta Carbonara",
                ingredients=["Pasta", "Eggs", "Bacon", "Parmesan"],
                instructions=["Cook pasta", "Fry bacon", "Mix eggs and cheese", "Combine all"],
                meal_types=[MealType.DINNER]
            ),
            Recipe(
                title="Avocado Toast",
                ingredients=["Bread", "Avocado", "Salt", "Pepper"],
                instructions=["Toast bread", "Mash avocado", "Spread on toast", "Season"],
                meal_types=[MealType.BREAKFAST]
            ),
            Recipe(
                title="Chicken Salad",
                ingredients=["Chicken", "Lettuce", "Tomato", "Cucumber", "Dressing"],
                instructions=["Cook chicken", "Chop vegetables", "Combine all", "Add dressing"],
                meal_types=[MealType.LUNCH]
            )
        ]
        
        for recipe in recipes:
            storage_service.save_recipe(recipe)
        
        # Search recipes
        pasta_recipes = storage_service.search_recipes("pasta")
        avocado_recipes = storage_service.search_recipes("avocado")
        chicken_recipes = storage_service.search_recipes("chicken")
        
        # Check search results
        assert len(pasta_recipes) == 1
        assert pasta_recipes[0].title == "Pasta Carbonara"
        
        assert len(avocado_recipes) == 1
        assert avocado_recipes[0].title == "Avocado Toast"
        
        assert len(chicken_recipes) == 1
        assert chicken_recipes[0].title == "Chicken Salad"


class TestMealPlanService:
    """Tests for MealPlanService."""
    
    @pytest.fixture
    def mock_recipe_storage(self):
        """Create a mock recipe storage service."""
        mock = Mock(spec=RecipeStorageService)
        mock.list_recipes.return_value = [
            Recipe(
                title="Pasta Carbonara",
                ingredients=["Pasta", "Eggs", "Bacon", "Parmesan"],
                instructions=["Cook pasta", "Fry bacon", "Mix eggs and cheese", "Combine all"],
                meal_types=[MealType.DINNER]
            ),
            Recipe(
                title="Avocado Toast",
                ingredients=["Bread", "Avocado", "Salt", "Pepper"],
                instructions=["Toast bread", "Mash avocado", "Spread on toast", "Season"],
                meal_types=[MealType.BREAKFAST]
            ),
            Recipe(
                title="Chicken Salad",
                ingredients=["Chicken", "Lettuce", "Tomato", "Cucumber", "Dressing"],
                instructions=["Cook chicken", "Chop vegetables", "Combine all", "Add dressing"],
                meal_types=[MealType.LUNCH]
            )
        ]
        return mock
    
    @pytest.fixture
    def mock_llm_provider(self):
        """Create a mock LLM provider."""
        mock = Mock(spec=BaseLLMProvider)
        mock.generate_meal_plan = AsyncMock(return_value={
            "message": "Meal plan generated"
        })
        return mock
    
    @pytest.fixture
    def meal_plan_service(self, mock_recipe_storage, mock_llm_provider):
        """Create a meal plan service."""
        return MealPlanService(
            recipe_storage=mock_recipe_storage,
            llm_provider=mock_llm_provider
        )
    
    @pytest.mark.asyncio
    async def test_generate_meal_plan(self, meal_plan_service, mock_llm_provider):
        """Test generating a meal plan."""
        # Generate meal plan
        user_id = uuid.uuid4()
        start_date = "2025-06-01"
        end_date = "2025-06-07"
        preferences = {"favorite_cuisines": ["Italian", "Mexican"]}
        nutrition_goal = "weight_loss"
        
        meal_plan = await meal_plan_service.generate_meal_plan(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            preferences=preferences,
            nutrition_goal=nutrition_goal
        )
        
        # Check meal plan
        assert meal_plan == {"message": "Meal plan generated"}
        
        # Check LLM provider was called correctly
        mock_llm_provider.generate_meal_plan.assert_called_once()
        call_args = mock_llm_provider.generate_meal_plan.call_args[1]
        assert call_args["user_preferences"] == preferences
        assert call_args["nutrition_goal"] == nutrition_goal
        assert len(call_args["available_recipes"]) == 3
