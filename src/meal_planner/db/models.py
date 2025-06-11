"""Database models using SQLAlchemy."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON, TypeDecorator

Base = declarative_base()


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type when available,
    otherwise uses CHAR(36) for other databases.
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class User(Base, TimestampMixin):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    recipes = relationship("Recipe", back_populates="user", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserPreferences(Base, TimestampMixin):
    """User preferences model."""
    
    __tablename__ = "user_preferences"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Preferences as JSON
    dietary_restrictions = Column(JSON, default=list)  # ["vegetarian", "gluten_free"]
    allergies = Column(JSON, default=list)  # ["nuts", "dairy"]
    favorite_cuisines = Column(JSON, default=list)  # ["italian", "mexican"]
    disliked_ingredients = Column(JSON, default=list)  # ["mushrooms", "olives"]
    cooking_skill_level = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    available_appliances = Column(JSON, default=list)  # ["oven", "stovetop", "microwave"]
    
    # Nutritional preferences
    target_calories_per_day = Column(Integer, nullable=True)
    target_protein_grams = Column(Float, nullable=True)
    target_carbs_grams = Column(Float, nullable=True)
    target_fat_grams = Column(Float, nullable=True)
    
    # Meal planning preferences
    meals_per_day = Column(Integer, default=3)  # breakfast, lunch, dinner
    prep_time_limit_minutes = Column(Integer, default=60)
    budget_per_week = Column(Float, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="preferences")


class Recipe(Base, TimestampMixin):
    """Recipe model."""
    
    __tablename__ = "recipes"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True)  # Nullable for system recipes
    
    # Basic recipe info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Recipe content (stored as JSON for flexibility)
    ingredients = Column(JSON, nullable=False)  # List of ingredients
    instructions = Column(JSON, nullable=False)  # List of instruction steps
    
    # Metadata
    meal_types = Column(JSON, default=list)  # ["breakfast", "lunch", "dinner", "snack"]
    tags = Column(JSON, default=list)  # ["quick", "healthy", "budget-friendly"]
    dietary_restrictions = Column(JSON, default=list)  # ["vegetarian", "vegan", "gluten_free"]
    appliances = Column(JSON, default=list)  # ["oven", "stovetop", "blender"]
    
    # Timing and serving
    prep_time_minutes = Column(Integer, nullable=True)
    cook_time_minutes = Column(Integer, nullable=True)
    total_time_minutes = Column(Integer, nullable=True)  # Computed field
    servings = Column(Integer, nullable=True)
    
    # External references
    source_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Nutrition (optional, can be computed)
    nutrition_info = Column(JSON, nullable=True)  # Calories, protein, carbs, fat, etc.
    
    # User notes
    notes = Column(Text, nullable=True)
    
    # Recipe status
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # For system/verified recipes
    
    # Difficulty and rating
    difficulty_level = Column(String(50), default="medium")  # easy, medium, hard
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Estimated cost
    estimated_cost_per_serving = Column(Float, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="recipes")
    meal_plan_recipes = relationship("MealPlanRecipe", back_populates="recipe")


class MealPlan(Base, TimestampMixin):
    """Meal plan model."""
    
    __tablename__ = "meal_plans"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # Plan metadata
    name = Column(String(255), nullable=True)  # Optional name for the plan
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Plan configuration
    nutrition_goal = Column(String(100), nullable=True)  # "balanced", "low_carb", "high_protein"
    budget_limit = Column(Float, nullable=True)
    meal_types = Column(JSON, default=list)  # ["breakfast", "lunch", "dinner"]
    
    # Plan results
    total_estimated_cost = Column(Float, nullable=True)
    nutrition_summary = Column(JSON, nullable=True)  # Aggregate nutrition info
    
    # Plan status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="meal_plans")
    recipes = relationship("MealPlanRecipe", back_populates="meal_plan", cascade="all, delete-orphan")
    grocery_lists = relationship("GroceryList", back_populates="meal_plan", cascade="all, delete-orphan")


class MealPlanRecipe(Base):
    """Association table for meal plans and recipes with additional data."""
    
    __tablename__ = "meal_plan_recipes"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    meal_plan_id = Column(GUID(), ForeignKey("meal_plans.id"), nullable=False)
    recipe_id = Column(GUID(), ForeignKey("recipes.id"), nullable=False)
    
    # When this recipe is scheduled
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    meal_type = Column(String(50), nullable=False)  # "breakfast", "lunch", "dinner", "snack"
    
    # Recipe modifications for this meal plan
    servings_multiplier = Column(Float, default=1.0)  # Scale recipe up/down
    notes = Column(Text, nullable=True)  # Plan-specific notes
    
    # Relationships
    meal_plan = relationship("MealPlan", back_populates="recipes")
    recipe = relationship("Recipe", back_populates="meal_plan_recipes")


class GroceryList(Base, TimestampMixin):
    """Grocery list model."""
    
    __tablename__ = "grocery_lists"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    meal_plan_id = Column(GUID(), ForeignKey("meal_plans.id"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # List metadata
    name = Column(String(255), nullable=True)
    
    # List items (stored as JSON for flexibility)
    items = Column(JSON, nullable=False)  # List of grocery items with quantities
    
    # Shopping info
    total_estimated_cost = Column(Float, nullable=True)
    store_preference = Column(String(255), nullable=True)
    
    # List status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    meal_plan = relationship("MealPlan", back_populates="grocery_lists")


class RecipeRating(Base, TimestampMixin):
    """Recipe rating model."""
    
    __tablename__ = "recipe_ratings"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    recipe_id = Column(GUID(), ForeignKey("recipes.id"), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(Text, nullable=True)
    
    # Additional feedback
    difficulty_rating = Column(Integer, nullable=True)  # 1-5 (easy to hard)
    would_make_again = Column(Boolean, nullable=True)
    
    # Prevent duplicate ratings using proper SQLAlchemy constraint
    __table_args__ = (UniqueConstraint('user_id', 'recipe_id', name='_user_recipe_rating'),)


class UploadedFile(Base, TimestampMixin):
    """Uploaded file model for recipe extraction."""
    
    __tablename__ = "uploaded_files"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    
    # File info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(255), nullable=False)
    
    # Processing status
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    extraction_result = Column(JSON, nullable=True)  # Extracted recipe data
    error_message = Column(Text, nullable=True)
    
    # Cleanup
    is_temporary = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)