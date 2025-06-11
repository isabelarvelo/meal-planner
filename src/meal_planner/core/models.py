"""Core models for the meal planner application."""

import json
import time
import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, field_validator


class OCREngine(str, Enum):
    """OCR engine types."""
    
    PYMUPDF = "pymupdf"
    MARKER = "marker"


class MealType(str, Enum):
    """Meal types."""
    
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    DESSERT = "dessert"


class DietaryRestriction(str, Enum):
    """Dietary restrictions."""
    
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    LOW_CARB = "low_carb"
    KETO = "keto"
    PALEO = "paleo"
    PESCATARIAN = "pescatarian"


class Appliance(str, Enum):
    """Kitchen appliances."""
    
    OVEN = "oven"
    STOVETOP = "stovetop"
    MICROWAVE = "microwave"
    BLENDER = "blender"
    FOOD_PROCESSOR = "food_processor"
    SLOW_COOKER = "slow_cooker"
    PRESSURE_COOKER = "pressure_cooker"
    AIR_FRYER = "air_fryer"
    GRILL = "grill"
    TOASTER = "toaster"
    TOASTER_OVEN = "toaster_oven"
    MIXER = "mixer"
    RICE_COOKER = "rice_cooker"
    INSTANT_POT = "instant_pot"
    SOUS_VIDE = "sous_vide"


class NutritionGoal(str, Enum):
    """Nutrition goals."""
    
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    HORMONE_BALANCE = "hormone_balance"
    GUT_HEALTH = "gut_health"
    HEART_HEALTH = "heart_health"
    ENERGY_BOOST = "energy_boost"


class OCRResult(BaseModel):
    """OCR result."""
    
    text: str
    confidence: float
    engine_used: OCREngine
    processing_time: float
    page_count: Optional[int] = None
    warnings: List[str] = Field(default_factory=list)


class NutritionInfo(BaseModel):
    """Nutrition information."""
    
    calories: Optional[int] = None
    protein_grams: Optional[float] = None
    carbs_grams: Optional[float] = None
    fat_grams: Optional[float] = None
    fiber_grams: Optional[float] = None
    sugar_grams: Optional[float] = None
    sodium_mg: Optional[int] = None
    cholesterol_mg: Optional[int] = None


class Ingredient(BaseModel):
    """Recipe ingredient."""
    
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None
    estimated_cost: Optional[Decimal] = None


class Recipe(BaseModel):
    """Recipe model."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    ingredients: List[Union[str, "Ingredient"]]
    instructions: List[str]
    meal_types: List[Union[str, "MealType"]] = Field(default_factory=list)
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    source_url: Optional[str] = None
    source_file: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    dietary_restrictions: List[Union[str, "DietaryRestriction"]] = Field(default_factory=list)
    appliances: List[Union[str, "Appliance"]] = Field(default_factory=list)
    nutrition: Optional["NutritionInfo"] = None
    notes: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    
    def save_to_file(self, directory: Path) -> Path:
        """Save recipe to a JSON file.
        
        Args:
            directory: Directory to save the file in
            
        Returns:
            Path to the saved file
        """
        # Create directory if it doesn't exist
        directory.mkdir(exist_ok=True, parents=True)
        
        # Create file path
        file_path = directory / f"{self.id}.json"
        
        # Convert to dict and handle UUID serialization
        recipe_dict = self.model_dump()
        
        # Convert UUID to string for JSON serialization
        if isinstance(recipe_dict.get('id'), uuid.UUID):
            recipe_dict['id'] = str(recipe_dict['id'])
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(recipe_dict, f, indent=2, default=str)
        
        return file_path
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> "Recipe":
        """Load recipe from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Recipe object
        """
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Convert string ID back to UUID if needed
        if isinstance(data.get('id'), str):
            try:
                data['id'] = uuid.UUID(data['id'])
            except ValueError:
                # If it's not a valid UUID string, generate a new one
                data['id'] = uuid.uuid4()
        
        return cls(**data)

class RecipeExtractionResponse(BaseModel):
    """Response for recipe extraction."""
    
    recipe: Recipe
    ocr_result: OCRResult
    processing_time: float
    warnings: List[str] = Field(default_factory=list)


class User(BaseModel):
    """User model."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: str
    name: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class UserPreferences(BaseModel):
    """User preferences."""
    
    favorite_cuisines: List[str] = Field(default_factory=list)
    disliked_ingredients: List[str] = Field(default_factory=list)
    dietary_restrictions: List[Union[str, DietaryRestriction]] = Field(default_factory=list)
    meal_preferences: Dict[str, List[MealType]] = Field(default_factory=dict)
    budget_per_meal: Optional[Decimal] = None
    servings_per_meal: int = 1


class NutritionGoalSettings(BaseModel):
    """Nutrition goal settings."""
    
    goal_type: str
    target_calories: Optional[int] = None
    target_protein_grams: Optional[float] = None
    target_carbs_grams: Optional[float] = None
    target_fat_grams: Optional[float] = None
    notes: Optional[str] = None


class UserFavorite(BaseModel):
    """User favorite recipe."""
    
    recipe_id: uuid.UUID
    notes: Optional[str] = None
    added_at: float = Field(default_factory=time.time)


class MealPlanDay(BaseModel):
    """Meal plan day."""
    
    date: date
    breakfast: Optional[uuid.UUID] = None
    lunch: Optional[uuid.UUID] = None
    dinner: Optional[uuid.UUID] = None
    snacks: List[uuid.UUID] = Field(default_factory=list)


class MealPlan(BaseModel):
    """Meal plan."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    start_date: date
    end_date: date
    days: List[MealPlanDay] = Field(default_factory=list)
    nutrition_goal: Optional[NutritionGoal] = None
    total_estimated_cost: Optional[Decimal] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class GroceryItem(BaseModel):
    """Grocery item."""
    
    name: str
    quantity: float
    unit: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    recipe_ids: List[uuid.UUID] = Field(default_factory=list)
    category: Optional[str] = None
    purchased: bool = False


class GroceryList(BaseModel):
    """Grocery list."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    meal_plan_id: uuid.UUID
    user_id: uuid.UUID
    items: List[GroceryItem] = Field(default_factory=list)
    total_estimated_cost: Optional[Decimal] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class MealPlanRequest(BaseModel):
    """Request for meal plan generation."""
    
    user_id: uuid.UUID
    start_date: date
    end_date: date
    meal_types: List[MealType] = Field(default_factory=list)
    nutrition_goal: Optional[NutritionGoal] = None
    budget_limit: Optional[Decimal] = None
    preferences: Dict = Field(default_factory=dict)


class MealPlanResponse(BaseModel):
    """Response for meal plan generation."""
    
    meal_plan: MealPlan
    grocery_list: GroceryList
    total_cost: Optional[Decimal] = None
    nutrition_summary: Dict = Field(default_factory=dict)
    processing_time: float
