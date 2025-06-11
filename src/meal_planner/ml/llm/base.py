"""Base LLM provider interface."""

import abc
from typing import Any, Dict, List, Optional

from meal_planner.core.models import Recipe


class BaseLLMProvider(abc.ABC):
    """Base class for LLM providers."""
    
    @abc.abstractmethod
    async def _generate(self, prompt: str) -> str:
        """Generate text using the LLM.
        
        Args:
            prompt: Prompt to generate from
            
        Returns:
            Generated text
        """
        pass
    
    @abc.abstractmethod
    async def evaluate_ocr_quality(self, text: str, confidence: float) -> Dict[str, Any]:
        """Evaluate the quality of OCR text.
        
        Args:
            text: OCR text to evaluate
            confidence: OCR confidence score
            
        Returns:
            Dictionary with quality assessment
        """
        pass
    
    @abc.abstractmethod
    async def structure_recipe(
        self, 
        text: str, 
        user_notes: Optional[str] = None
    ) -> Recipe:
        """Structure a recipe from OCR text.
        
        Args:
            text: OCR text to structure
            user_notes: Optional notes from the user
            
        Returns:
            Structured recipe
        """
        pass
    
    @abc.abstractmethod
    async def generate_meal_plan(
        self,
        user_preferences: Dict[str, Any],
        available_recipes: List[Recipe],
        nutrition_goal: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Generate a meal plan.
        
        Args:
            user_preferences: User preferences
            available_recipes: Available recipes
            nutrition_goal: Optional nutrition goal
            days: Number of days to plan for
            
        Returns:
            Dictionary with meal plan
        """
        pass
    
    @abc.abstractmethod
    async def analyze_nutrition(self, recipe: Recipe) -> Dict[str, Any]:
        """Analyze nutrition information for a recipe.
        
        Args:
            recipe: Recipe to analyze
            
        Returns:
            Dictionary with nutrition information
        """
        pass
    
    @abc.abstractmethod
    def get_name(self) -> str:
        """Get the name of the LLM provider.
        
        Returns:
            Name of the LLM provider
        """
        pass
    
    @abc.abstractmethod
    def get_model(self) -> str:
        """Get the model name.
        
        Returns:
            Model name
        """
        pass
