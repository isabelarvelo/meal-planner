"""Pytest fixtures for testing."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from meal_planner.api.main import app
from meal_planner.core.config import settings
from meal_planner.core.models import Recipe
from meal_planner.core.services import RecipeStorageService
from meal_planner.ml.llm.base import BaseLLMProvider
from meal_planner.ml.ocr.base import BaseOCREngine


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_ocr_engine() -> BaseOCREngine:
    """Create a mock OCR engine."""
    from unittest.mock import AsyncMock, Mock
    from meal_planner.core.models import OCREngine, OCRResult
    
    mock_engine = Mock(spec=BaseOCREngine)
    mock_engine.extract_text = AsyncMock(return_value=OCRResult(
        text="Test recipe text",
        confidence=0.9,
        engine_used=OCREngine.PYMUPDF,
        processing_time=0.5
    ))
    mock_engine.get_name.return_value = "MockOCR"
    mock_engine.get_version.return_value = "1.0.0"
    mock_engine.supports_format.return_value = True
    
    return mock_engine


@pytest.fixture
def mock_llm_provider() -> BaseLLMProvider:
    """Create a mock LLM provider."""
    from unittest.mock import AsyncMock, Mock
    from meal_planner.core.models import Recipe, MealType
    
    mock_provider = Mock(spec=BaseLLMProvider)
    
    # Mock evaluate_ocr_quality
    mock_provider.evaluate_ocr_quality = AsyncMock(return_value={
        "quality_score": 0.9,
        "is_recipe_content": True,
        "detected_issues": [],
        "recommended_action": "use_result"
    })
    
    # Mock structure_recipe
    mock_provider.structure_recipe = AsyncMock(return_value=Recipe(
        title="Test Recipe",
        ingredients=["Ingredient 1", "Ingredient 2"],
        instructions=["Step 1", "Step 2"],
        meal_types=[MealType.DINNER]
    ))
    
    # Mock generate_meal_plan
    mock_provider.generate_meal_plan = AsyncMock(return_value={
        "message": "Meal plan generated"
    })
    
    # Mock analyze_nutrition
    mock_provider.analyze_nutrition = AsyncMock(return_value={
        "calories": 300,
        "protein_grams": 20,
        "carbs_grams": 30,
        "fat_grams": 10
    })
    
    # Mock get_name and get_model
    mock_provider.get_name.return_value = "MockLLM"
    mock_provider.get_model.return_value = "mock-model"
    
    return mock_provider


@pytest.fixture
def recipe_storage(temp_data_dir: Path) -> RecipeStorageService:
    """Create a recipe storage service with a temporary directory."""
    return RecipeStorageService(recipes_dir=temp_data_dir)


@pytest.fixture
def sample_recipe() -> Recipe:
    """Create a sample recipe for testing."""
    return Recipe(
        title="Test Recipe",
        ingredients=["Ingredient 1", "Ingredient 2"],
        instructions=["Step 1", "Step 2"],
        meal_types=[],
        prep_time_minutes=15,
        cook_time_minutes=30
    )


@pytest.fixture
def sample_recipes(recipe_storage: RecipeStorageService) -> list[Recipe]:
    """Create and save sample recipes for testing."""
    recipes = [
        Recipe(
            title="Pasta Carbonara",
            ingredients=["Pasta", "Eggs", "Bacon", "Parmesan"],
            instructions=["Cook pasta", "Fry bacon", "Mix eggs and cheese", "Combine all"],
            meal_types=["dinner"],
            prep_time_minutes=10,
            cook_time_minutes=20
        ),
        Recipe(
            title="Avocado Toast",
            ingredients=["Bread", "Avocado", "Salt", "Pepper"],
            instructions=["Toast bread", "Mash avocado", "Spread on toast", "Season"],
            meal_types=["breakfast"],
            prep_time_minutes=5,
            cook_time_minutes=5
        ),
        Recipe(
            title="Chicken Salad",
            ingredients=["Chicken", "Lettuce", "Tomato", "Cucumber", "Dressing"],
            instructions=["Cook chicken", "Chop vegetables", "Combine all", "Add dressing"],
            meal_types=["lunch"],
            prep_time_minutes=15,
            cook_time_minutes=15
        )
    ]
    
    # Save recipes
    for recipe in recipes:
        recipe_storage.save_recipe(recipe)
    
    return recipes
