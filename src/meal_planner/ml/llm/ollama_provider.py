"""Ollama LLM provider."""

import json
import time
from typing import Any, Dict, List, Optional

import aiohttp
from loguru import logger

from meal_planner.core.models import Recipe
from meal_planner.ml.llm.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """LLM provider using Ollama."""
    
    def __init__(self, model: str, api_base: str):
        """Initialize the Ollama provider.
        
        Args:
            model: Model name
            api_base: API base URL
        """
        self.model = model
        self.api_base = api_base.rstrip("/")
        logger.info(f"Initialized OllamaProvider with model {model}")
    
    async def _generate(self, prompt: str) -> str:
        """Generate text using Ollama.
        
        Args:
            prompt: Prompt to generate from
            
        Returns:
            Generated text
        """
        url = f"{self.api_base}/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {error_text}")
                        return f"Error: {error_text}"
                    
                    result = await response.json()
                    return result.get("response", "")
        
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return f"Error: {str(e)}"
    
    async def evaluate_ocr_quality(self, text: str, confidence: float) -> Dict[str, Any]:
        """Evaluate the quality of OCR text.
        
        Args:
            text: OCR text to evaluate
            confidence: OCR confidence score
            
        Returns:
            Dictionary with quality assessment
        """
        prompt = f"""
        Evaluate the quality of the following OCR text. The OCR engine reported a confidence score of {confidence:.2f}.
        
        TEXT:
        {text}
        
        Analyze the text and provide a JSON response with the following fields:
        - quality_score: A float between 0 and 1 representing the overall quality
        - is_recipe_content: A boolean indicating if this appears to be recipe content
        - detected_issues: A list of strings describing any detected issues
        - recommended_action: One of ["use_result", "retry_with_different_engine", "manual_entry"]
        
        JSON response:
        """
        
        try:
            response = await self._generate(prompt)
            
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                return {
                    "quality_score": confidence,
                    "is_recipe_content": True,
                    "detected_issues": ["Failed to parse LLM response"],
                    "recommended_action": "use_result"
                }
        
        except Exception as e:
            logger.error(f"Error evaluating OCR quality: {e}")
            return {
                "quality_score": confidence,
                "is_recipe_content": True,
                "detected_issues": [f"Error: {str(e)}"],
                "recommended_action": "use_result"
            }
    
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
        prompt = f"""
        Extract and structure a recipe from the following text. 
        
        TEXT:
        {text}
        
        {f"USER NOTES: {user_notes}" if user_notes else ""}
        
        Analyze the text and provide a JSON response with the following fields:
        - title: The recipe title
        - ingredients: A list of ingredients (strings)
        - instructions: A list of steps (strings)
        - meal_types: A list of meal types (breakfast, lunch, dinner, snack, dessert)
        - prep_time_minutes: Preparation time in minutes (integer, optional)
        - cook_time_minutes: Cooking time in minutes (integer, optional)
        - servings: Number of servings (integer, optional)
        - tags: A list of tags (strings, optional)
        - dietary_restrictions: A list of dietary restrictions (strings, optional)
        
        JSON response:
        """
        
        try:
            response = await self._generate(prompt)
            
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                recipe_data = json.loads(json_str)
                
                # Create recipe
                recipe = Recipe(
                    title=recipe_data.get("title", "Untitled Recipe"),
                    ingredients=recipe_data.get("ingredients", []),
                    instructions=recipe_data.get("instructions", []),
                    meal_types=recipe_data.get("meal_types", []),
                    prep_time_minutes=recipe_data.get("prep_time_minutes"),
                    cook_time_minutes=recipe_data.get("cook_time_minutes"),
                    servings=recipe_data.get("servings"),
                    tags=recipe_data.get("tags", []),
                    dietary_restrictions=recipe_data.get("dietary_restrictions", []),
                    notes=user_notes
                )
                
                return recipe
            else:
                # Fallback if JSON parsing fails
                return Recipe(
                    title="Extraction Failed",
                    ingredients=["Extraction failed"],
                    instructions=["Could not extract recipe from text"],
                    notes=f"Original text: {text[:100]}..."
                )
        
        except Exception as e:
            logger.error(f"Error structuring recipe: {e}")
            return Recipe(
                title="Extraction Error",
                ingredients=["Extraction error"],
                instructions=[f"Error: {str(e)}"],
                notes=f"Original text: {text[:100]}..."
            )
    
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
        # Create a list of recipe summaries
        recipe_summaries = []
        for recipe in available_recipes:
            summary = {
                "id": str(recipe.id),
                "title": recipe.title,
                "meal_types": recipe.meal_types,
                "dietary_restrictions": recipe.dietary_restrictions,
                "prep_time_minutes": recipe.prep_time_minutes,
                "cook_time_minutes": recipe.cook_time_minutes
            }
            recipe_summaries.append(summary)
        
        prompt = f"""
        Generate a meal plan based on the following information:
        
        USER PREFERENCES:
        {json.dumps(user_preferences, indent=2)}
        
        NUTRITION GOAL: {nutrition_goal or "None"}
        
        DAYS: {days}
        
        AVAILABLE RECIPES:
        {json.dumps(recipe_summaries, indent=2)}
        
        Create a meal plan that satisfies the user's preferences and nutrition goals.
        Provide a JSON response with the following fields:
        - days: A list of day objects, each with:
          - date: Date in YYYY-MM-DD format
          - breakfast: Recipe ID for breakfast (or null)
          - lunch: Recipe ID for lunch (or null)
          - dinner: Recipe ID for dinner (or null)
          - snacks: List of recipe IDs for snacks (or empty list)
        - grocery_items: A list of grocery items, each with:
          - name: Item name
          - quantity: Quantity
          - unit: Unit of measurement
          - recipe_ids: List of recipe IDs that use this item
          - category: Category (e.g., "Produce", "Dairy", etc.)
        - total_cost: Estimated total cost (optional)
        - nutrition_summary: Summary of nutritional information (optional)
        
        JSON response:
        """
        
        try:
            response = await self._generate(prompt)
            
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                return {
                    "error": "Failed to parse LLM response",
                    "message": "Could not generate meal plan"
                }
        
        except Exception as e:
            logger.error(f"Error generating meal plan: {e}")
            return {
                "error": str(e),
                "message": "Could not generate meal plan"
            }
    
    async def analyze_nutrition(self, recipe: Recipe) -> Dict[str, Any]:
        """Analyze nutrition information for a recipe.
        
        Args:
            recipe: Recipe to analyze
            
        Returns:
            Dictionary with nutrition information
        """
        # Convert ingredients to strings if they're not already
        ingredient_strings = []
        for ingredient in recipe.ingredients:
            if isinstance(ingredient, str):
                ingredient_strings.append(ingredient)
            else:
                # Assume it's an Ingredient object
                quantity_str = f"{ingredient.quantity} " if ingredient.quantity else ""
                unit_str = f"{ingredient.unit} " if ingredient.unit else ""
                ingredient_strings.append(f"{quantity_str}{unit_str}{ingredient.name}")
        
        prompt = f"""
        Analyze the nutritional content of the following recipe:
        
        RECIPE: {recipe.title}
        
        INGREDIENTS:
        {json.dumps(ingredient_strings, indent=2)}
        
        SERVINGS: {recipe.servings or "Unknown"}
        
        Estimate the nutritional content per serving and provide a JSON response with the following fields:
        - calories: Calories per serving (integer)
        - protein_grams: Protein in grams (float)
        - carbs_grams: Carbohydrates in grams (float)
        - fat_grams: Fat in grams (float)
        - fiber_grams: Fiber in grams (float)
        - sugar_grams: Sugar in grams (float)
        - sodium_mg: Sodium in milligrams (integer)
        - cholesterol_mg: Cholesterol in milligrams (integer)
        
        JSON response:
        """
        
        try:
            response = await self._generate(prompt)
            
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                return {
                    "calories": None,
                    "protein_grams": None,
                    "carbs_grams": None,
                    "fat_grams": None,
                    "fiber_grams": None,
                    "sugar_grams": None,
                    "sodium_mg": None,
                    "cholesterol_mg": None
                }
        
        except Exception as e:
            logger.error(f"Error analyzing nutrition: {e}")
            return {
                "calories": None,
                "protein_grams": None,
                "carbs_grams": None,
                "fat_grams": None,
                "fiber_grams": None,
                "sugar_grams": None,
                "sodium_mg": None,
                "cholesterol_mg": None
            }
    
    def get_name(self) -> str:
        """Get the name of the LLM provider.
        
        Returns:
            Name of the LLM provider
        """
        return "Ollama"
    
    def get_model(self) -> str:
        """Get the model name.
        
        Returns:
            Model name
        """
        return self.model
