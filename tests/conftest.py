"""Test configuration and fixtures."""

import asyncio
import os
import pytest
import pytest_asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from meal_planner.api.main import app
from meal_planner.core.config import Settings
from meal_planner.db.database import get_db_session
from meal_planner.db.models import Base
from meal_planner.db.services import UserService, RecipeService, MealPlanService


# Test settings
@pytest.fixture(scope="session")
def test_settings():
    """Test configuration settings."""
    return Settings(
        environment="testing",
        debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        data_dir=Path("test_data"),
        upload_dir=Path("test_data/uploads"),
        recipes_dir=Path("test_data/recipes"),
    )


# Database fixtures
@pytest_asyncio.fixture(scope="function")
async def test_engine(test_settings):
    """Create test database engine."""
    engine = create_async_engine(
        test_settings.database_url,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session_factory(test_engine):
    """Create test session factory."""
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="function")
async def test_db_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with test_session_factory() as session:
        yield session


# API client fixtures
@pytest.fixture(scope="function")
def test_client(test_db_session):
    """Create test API client."""
    # Override the database dependency
    def get_test_db():
        return test_db_session
    
    app.dependency_overrides[get_db_session] = get_test_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


# Service fixtures
@pytest_asyncio.fixture(scope="function")
async def user_service(test_db_session):
    """Create user service with test database."""
    return UserService(test_db_session)


@pytest_asyncio.fixture(scope="function")
async def recipe_service(test_db_session):
    """Create recipe service with test database."""
    return RecipeService(test_db_session)


@pytest_asyncio.fixture(scope="function")
async def meal_plan_service(test_db_session):
    """Create meal plan service with test database."""
    return MealPlanService(test_db_session)


# Test data fixtures
@pytest_asyncio.fixture
async def test_user(user_service):
    """Create a test user."""
    return await user_service.create_user(
        email="test@example.com",
        full_name="Test User"
    )


@pytest_asyncio.fixture
async def test_recipe_data():
    """Sample recipe data for testing."""
    return {
        "title": "Test Pasta",
        "description": "A simple test pasta recipe",
        "ingredients": ["1 lb pasta", "2 cups tomato sauce", "1 cup cheese"],
        "instructions": ["Boil pasta", "Heat sauce", "Combine and serve"],
        "meal_types": ["dinner"],
        "tags": ["quick", "easy"],
        "dietary_restrictions": ["vegetarian"],
        "appliances": ["stovetop"],
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "notes": "Great for weeknight dinners"
    }


@pytest_asyncio.fixture
async def test_recipe(recipe_service, test_user, test_recipe_data):
    """Create a test recipe."""
    return await recipe_service.create_recipe(
        user_id=test_user.id,
        recipe_data=test_recipe_data
    )


@pytest_asyncio.fixture
async def test_meal_plan_data():
    """Sample meal plan data for testing."""
    from datetime import datetime, timedelta
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=6)
    
    return {
        "name": "Test Meal Plan",
        "start_date": start_date,
        "end_date": end_date,
        "nutrition_goal": "balanced",
        "budget_limit": 100.0,
        "meal_types": ["breakfast", "lunch", "dinner"]
    }


# Mock fixtures for external dependencies
@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""
    mock = MagicMock()
    mock.structure_recipe.return_value = {
        "title": "Mocked Recipe",
        "ingredients": ["Mock ingredient 1", "Mock ingredient 2"],
        "instructions": ["Mock step 1", "Mock step 2"],
        "meal_types": ["dinner"],
        "tags": ["mock"]
    }
    mock.generate_meal_plan.return_value = {
        "days": [
            {
                "date": "2025-06-11",
                "breakfast": "Mock Breakfast",
                "lunch": "Mock Lunch", 
                "dinner": "Mock Dinner"
            }
        ],
        "grocery_items": [
            {"name": "Mock Item", "quantity": "1 unit"}
        ],
        "total_cost": 25.50
    }
    return mock


@pytest.fixture
def mock_ocr_engine():
    """Mock OCR engine for testing."""
    mock = MagicMock()
    mock.extract_text.return_value = {
        "text": "Mock extracted text from recipe image",
        "confidence": 0.95
    }
    mock.get_name.return_value = "MockOCR"
    mock.get_version.return_value = "1.0.0"
    mock.get_supported_formats.return_value = [".pdf", ".jpg", ".png"]
    return mock


# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after each test."""
    yield
    
    # Clean up test data directory
    test_data_path = Path("test_data")
    if test_data_path.exists():
        import shutil
        shutil.rmtree(test_data_path, ignore_errors=True)

@pytest.fixture(autouse=True)
def cleanup_recipes_between_tests():
    """Clean up recipe storage between tests."""
    yield
    
    # Clean up JSON recipe files
    recipes_dir = Path("test_data/recipes")
    if recipes_dir.exists():
        import shutil
        shutil.rmtree(recipes_dir, ignore_errors=True)
        recipes_dir.mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="function")
def isolated_test_client(test_client):
    """Test client with isolated storage for each test."""
    # This ensures each test gets a clean storage state
    yield test_client

@pytest.fixture(autouse=True)
def cleanup_recipe_files():
    """Clean up recipe JSON files between tests."""
    yield
    recipes_dir = Path("data/recipes")
    if recipes_dir.exists():
        import shutil
        shutil.rmtree(recipes_dir, ignore_errors=True)
        recipes_dir.mkdir(parents=True, exist_ok=True)