"""Core services for the meal planner application."""

import glob
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import UUID

from loguru import logger

from meal_planner.core.config import settings
from meal_planner.core.models import (
    MealPlan, OCRResult, Recipe, RecipeExtractionResponse
)
from meal_planner.ml.llm.base import BaseLLMProvider
from meal_planner.ml.ocr.base import BaseOCREngine


class RecipeExtractionService:
    """Service for extracting recipes from images and documents."""
    
    def __init__(
        self,
        ocr_primary: BaseOCREngine,
        ocr_fallback: Optional[BaseOCREngine],
        llm_provider: BaseLLMProvider
    ):
        """Initialize the recipe extraction service.
        
        Args:
            ocr_primary: Primary OCR engine
            ocr_fallback: Fallback OCR engine (optional)
            llm_provider: LLM provider
        """
        self.ocr_primary = ocr_primary
        self.ocr_fallback = ocr_fallback
        self.llm_provider = llm_provider
        
        logger.info(
            f"Initialized RecipeExtractionService with {ocr_primary.get_name()} "
            f"and {ocr_fallback.get_name() if ocr_fallback else 'no fallback'}"
        )
    
    async def extract_recipe(
        self,
        file_path: Path,
        user_notes: Optional[str] = None
    ) -> RecipeExtractionResponse:
        """Extract a recipe from a file.
        
        Args:
            file_path: Path to the file
            user_notes: Optional notes from the user
            
        Returns:
            Extraction response with recipe and metadata
        """
        start_time = time.time()
        warnings = []
        
        logger.info(f"Extracting recipe from {file_path}")
        
        # Extract text using primary OCR engine
        ocr_result = await self.ocr_primary.extract_text(file_path)
        
        # Check if OCR was successful
        if ocr_result.confidence < 0.5 and self.ocr_fallback is not None:
            warnings.append(
                f"Primary OCR engine ({self.ocr_primary.get_name()}) produced low confidence "
                f"result ({ocr_result.confidence:.2f}). Trying fallback engine."
            )
            
            # Try fallback OCR engine
            fallback_result = await self.ocr_fallback.extract_text(file_path)
            
            # Use fallback result if it has higher confidence
            if fallback_result.confidence > ocr_result.confidence:
                warnings.append(
                    f"Using fallback OCR engine ({self.ocr_fallback.get_name()}) "
                    f"with confidence {fallback_result.confidence:.2f}"
                )
                ocr_result = fallback_result
            else:
                warnings.append(
                    f"Fallback OCR engine ({self.ocr_fallback.get_name()}) "
                    f"produced lower confidence result ({fallback_result.confidence:.2f}). "
                    f"Using primary OCR result."
                )
        
        # Evaluate OCR quality
        quality_assessment = await self.llm_provider.evaluate_ocr_quality(
            ocr_result.text, ocr_result.confidence
        )
        
        # Add warnings from quality assessment
        if "detected_issues" in quality_assessment:
            warnings.extend(quality_assessment["detected_issues"])
        
        # Structure recipe using LLM
        recipe = await self.llm_provider.structure_recipe(
            ocr_result.text, user_notes
        )
        
        # Set source file
        recipe.source_file = str(file_path)
        
        # Create response
        response = RecipeExtractionResponse(
            recipe=recipe,
            ocr_result=ocr_result,
            processing_time=time.time() - start_time,
            warnings=warnings
        )
        
        return response


class RecipeStorageService:
    """Service for storing and retrieving recipes."""
    
    def __init__(self, recipes_dir: Optional[Path] = None):
        """Initialize the recipe storage service.
        
        Args:
            recipes_dir: Directory to store recipes in
        """
        self.recipes_dir = recipes_dir or settings.recipes_dir
        
        # Create directory if it doesn't exist
        self.recipes_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Initialized RecipeStorageService with directory {self.recipes_dir}")
    
    def save_recipe(self, recipe: Recipe) -> Path:
        """Save a recipe.
        
        Args:
            recipe: Recipe to save
            
        Returns:
            Path to the saved file
        """
        # Update timestamp
        recipe.updated_at = time.time()
        
        # Save recipe
        file_path = recipe.save_to_file(self.recipes_dir)
        
        logger.info(f"Saved recipe {recipe.id} to {file_path}")
        
        return file_path
    
    def load_recipe(self, recipe_id: UUID) -> Optional[Recipe]:
        """Load a recipe.
        
        Args:
            recipe_id: Recipe ID
            
        Returns:
            Recipe if found, None otherwise
        """
        file_path = self.recipes_dir / f"{recipe_id}.json"
        
        if not file_path.exists():
            logger.warning(f"Recipe {recipe_id} not found at {file_path}")
            return None
        
        try:
            recipe = Recipe.load_from_file(file_path)
            logger.info(f"Loaded recipe {recipe_id} from {file_path}")
            return recipe
        except Exception as e:
            logger.error(f"Error loading recipe {recipe_id}: {e}")
            return None
    
    def delete_recipe(self, recipe_id: UUID) -> bool:
        """Delete a recipe.
        
        Args:
            recipe_id: Recipe ID
            
        Returns:
            True if the recipe was deleted, False otherwise
        """
        file_path = self.recipes_dir / f"{recipe_id}.json"
        
        if not file_path.exists():
            logger.warning(f"Recipe {recipe_id} not found at {file_path}")
            return False
        
        try:
            os.remove(file_path)
            logger.info(f"Deleted recipe {recipe_id} from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting recipe {recipe_id}: {e}")
            return False
    
    def list_recipes(self, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """List recipes.
        
        Args:
            limit: Maximum number of recipes to return
            offset: Offset for pagination
            
        Returns:
            List of recipes
        """
        # Get all recipe files
        recipe_files = sorted(glob.glob(str(self.recipes_dir / "*.json")))
        
        # Apply pagination
        recipe_files = recipe_files[offset:offset + limit]
        
        # Load recipes
        recipes = []
        for file_path in recipe_files:
            try:
                recipe = Recipe.load_from_file(Path(file_path))
                recipes.append(recipe)
            except Exception as e:
                logger.error(f"Error loading recipe from {file_path}: {e}")
        
        logger.info(f"Listed {len(recipes)} recipes")
        
        return recipes
    
    def search_recipes(self, query: str, limit: int = 100) -> List[Recipe]:
        """Search recipes.
        
        Args:
            query: Search query
            limit: Maximum number of recipes to return
            
        Returns:
            List of matching recipes
        """
        # Get all recipes
        all_recipes = self.list_recipes(limit=1000)
        
        # Filter recipes by query
        matching_recipes = []
        query = query.lower()
        
        for recipe in all_recipes:
            # Check title
            if query in recipe.title.lower():
                matching_recipes.append(recipe)
                continue
            
            # Check ingredients
            for ingredient in recipe.ingredients:
                if isinstance(ingredient, str) and query in ingredient.lower():
                    matching_recipes.append(recipe)
                    break
                elif hasattr(ingredient, "name") and query in ingredient.name.lower():
                    matching_recipes.append(recipe)
                    break
            
            # Check tags
            for tag in recipe.tags:
                if query in tag.lower():
                    matching_recipes.append(recipe)
                    break
        
        # Apply limit
        matching_recipes = matching_recipes[:limit]
        
        logger.info(f"Found {len(matching_recipes)} recipes matching '{query}'")
        
        return matching_recipes


class MealPlanService:
    """Service for generating meal plans."""
    
    def __init__(
        self,
        recipe_storage: RecipeStorageService,
        llm_provider: BaseLLMProvider
    ):
        """Initialize the meal plan service.
        
        Args:
            recipe_storage: Recipe storage service
            llm_provider: LLM provider
        """
        self.recipe_storage = recipe_storage
        self.llm_provider = llm_provider
        
        logger.info("Initialized MealPlanService")
    
    async def generate_meal_plan(
        self,
        user_id: UUID,
        start_date: str,
        end_date: str,
        preferences: Dict,
        nutrition_goal: Optional[str] = None,
        budget_limit: Optional[float] = None
    ) -> Dict:
        """Generate a meal plan.
        
        Args:
            user_id: User ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            preferences: User preferences
            nutrition_goal: Optional nutrition goal
            budget_limit: Optional budget limit
            
        Returns:
            Dictionary with meal plan and grocery list
        """
        logger.info(f"Generating meal plan for user {user_id}")
        
        # Get available recipes
        available_recipes = self.recipe_storage.list_recipes(limit=1000)
        
        if not available_recipes:
            logger.warning("No recipes available for meal planning")
            return {
                "error": "No recipes available for meal planning",
                "message": "Please add some recipes before generating a meal plan"
            }
        
        # Generate meal plan using LLM
        meal_plan_data = await self.llm_provider.generate_meal_plan(
            user_preferences=preferences,
            available_recipes=available_recipes,
            nutrition_goal=nutrition_goal,
            days=(end_date - start_date).days + 1
        )
        
        logger.info(f"Generated meal plan for user {user_id}")
        
        return meal_plan_data
