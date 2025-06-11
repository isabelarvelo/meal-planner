"""Database service layer for CRUD operations."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from meal_planner.db.models import (
    GroceryList, MealPlan, MealPlanRecipe, Recipe, RecipeRating, UploadedFile, User, UserPreferences
)


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, email: str, full_name: str) -> User:
        """Create a new user."""
        user = User(email=email, full_name=full_name)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: uuid.UUID, **kwargs) -> Optional[User]:
        """Update user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            setattr(user, key, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        return True


class RecipeService:
    """Service for recipe operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_recipe(self, user_id: Optional[uuid.UUID], recipe_data: dict) -> Recipe:
        """Create a new recipe."""
        # Calculate total time
        prep_time = recipe_data.get('prep_time_minutes', 0) or 0
        cook_time = recipe_data.get('cook_time_minutes', 0) or 0
        total_time = prep_time + cook_time if prep_time or cook_time else None
        
        recipe = Recipe(
            user_id=user_id,
            total_time_minutes=total_time,
            **recipe_data
        )
        
        self.db.add(recipe)
        await self.db.commit()
        await self.db.refresh(recipe)
        return recipe
    
    async def get_recipe_by_id(self, recipe_id: uuid.UUID) -> Optional[Recipe]:
        """Get recipe by ID."""
        result = await self.db.execute(
            select(Recipe)
            .options(selectinload(Recipe.user))
            .where(Recipe.id == recipe_id)
        )
        return result.scalar_one_or_none()
    
    async def list_recipes(
        self,
        user_id: Optional[uuid.UUID] = None,
        limit: int = 20,
        offset: int = 0,
        include_public: bool = True
    ) -> List[Recipe]:
        """List recipes with pagination."""
        query = select(Recipe).options(selectinload(Recipe.user))
        
        # Filter conditions
        conditions = []
        if user_id:
            conditions.append(Recipe.user_id == user_id)
        if include_public:
            conditions.append(Recipe.is_public == True)
        
        if conditions:
            query = query.where(or_(*conditions))
        
        query = query.order_by(desc(Recipe.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_recipes(
        self,
        query: str,
        user_id: Optional[uuid.UUID] = None,
        limit: int = 20
    ) -> List[Recipe]:
        """Search recipes by title, tags, or ingredients."""
        search_query = select(Recipe).options(selectinload(Recipe.user))
        
        # Text search conditions
        search_conditions = [
            Recipe.title.ilike(f"%{query}%"),
            Recipe.description.ilike(f"%{query}%"),
            # For JSON fields, we'll use a simple string search for SQLite compatibility
            func.json_extract(Recipe.tags, '$').like(f"%{query}%"),
            func.json_extract(Recipe.ingredients, '$').like(f"%{query}%")
        ]
        
        search_query = search_query.where(or_(*search_conditions))
        
        # User filter
        if user_id:
            search_query = search_query.where(
                or_(Recipe.user_id == user_id, Recipe.is_public == True)
            )
        else:
            search_query = search_query.where(Recipe.is_public == True)
        
        search_query = search_query.order_by(desc(Recipe.created_at)).limit(limit)
        
        result = await self.db.execute(search_query)
        return result.scalars().all()
    
    async def update_recipe(self, recipe_id: uuid.UUID, recipe_data: dict) -> Optional[Recipe]:
        """Update recipe."""
        recipe = await self.get_recipe_by_id(recipe_id)
        if not recipe:
            return None
        
        # Calculate total time if prep/cook time changed
        if 'prep_time_minutes' in recipe_data or 'cook_time_minutes' in recipe_data:
            prep_time = recipe_data.get('prep_time_minutes', recipe.prep_time_minutes) or 0
            cook_time = recipe_data.get('cook_time_minutes', recipe.cook_time_minutes) or 0
            recipe_data['total_time_minutes'] = prep_time + cook_time if prep_time or cook_time else None
        
        for key, value in recipe_data.items():
            setattr(recipe, key, value)
        
        await self.db.commit()
        await self.db.refresh(recipe)
        return recipe
    
    async def delete_recipe(self, recipe_id: uuid.UUID) -> bool:
        """Delete recipe."""
        recipe = await self.get_recipe_by_id(recipe_id)
        if not recipe:
            return False
        
        await self.db.delete(recipe)
        await self.db.commit()
        return True
    
    async def get_recipes_by_filters(
        self,
        meal_types: Optional[List[str]] = None,
        dietary_restrictions: Optional[List[str]] = None,
        max_prep_time: Optional[int] = None,
        max_total_time: Optional[int] = None,
        appliances: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Recipe]:
        """Get recipes by various filters."""
        query = select(Recipe).where(Recipe.is_public == True)
        
        if meal_types:
            # For SQLite, we'll use a simple text search in JSON
            meal_type_conditions = [
                func.json_extract(Recipe.meal_types, '$').like(f"%{mt}%") 
                for mt in meal_types
            ]
            query = query.where(or_(*meal_type_conditions))
        
        if dietary_restrictions:
            dr_conditions = [
                func.json_extract(Recipe.dietary_restrictions, '$').like(f"%{dr}%")
                for dr in dietary_restrictions
            ]
            query = query.where(or_(*dr_conditions))
        
        if max_prep_time:
            query = query.where(Recipe.prep_time_minutes <= max_prep_time)
        
        if max_total_time:
            query = query.where(Recipe.total_time_minutes <= max_total_time)
        
        if appliances:
            app_conditions = [
                func.json_extract(Recipe.appliances, '$').like(f"%{app}%")
                for app in appliances
            ]
            query = query.where(or_(*app_conditions))
        
        query = query.order_by(desc(Recipe.average_rating), desc(Recipe.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()


class MealPlanService:
    """Service for meal plan operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_meal_plan(self, user_id: uuid.UUID, meal_plan_data: dict) -> MealPlan:
        """Create a new meal plan."""
        meal_plan = MealPlan(user_id=user_id, **meal_plan_data)
        self.db.add(meal_plan)
        await self.db.commit()
        await self.db.refresh(meal_plan)
        return meal_plan
    
    async def get_meal_plan_by_id(self, meal_plan_id: uuid.UUID) -> Optional[MealPlan]:
        """Get meal plan by ID."""
        result = await self.db.execute(
            select(MealPlan)
            .options(
                selectinload(MealPlan.user),
                selectinload(MealPlan.recipes).selectinload(MealPlanRecipe.recipe),
                selectinload(MealPlan.grocery_lists)
            )
            .where(MealPlan.id == meal_plan_id)
        )
        return result.scalar_one_or_none()
    
    async def list_meal_plans(
        self,
        user_id: Optional[uuid.UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[MealPlan]:
        """List meal plans with pagination."""
        query = select(MealPlan).options(
            selectinload(MealPlan.user),
            selectinload(MealPlan.recipes).selectinload(MealPlanRecipe.recipe)
        )
        
        if user_id:
            query = query.where(MealPlan.user_id == user_id)
        
        query = query.order_by(desc(MealPlan.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_meal_plan(self, meal_plan_id: uuid.UUID, meal_plan_data: dict) -> Optional[MealPlan]:
        """Update meal plan."""
        meal_plan = await self.get_meal_plan_by_id(meal_plan_id)
        if not meal_plan:
            return None
        
        for key, value in meal_plan_data.items():
            setattr(meal_plan, key, value)
        
        await self.db.commit()
        await self.db.refresh(meal_plan)
        return meal_plan
    
    async def delete_meal_plan(self, meal_plan_id: uuid.UUID) -> bool:
        """Delete meal plan."""
        meal_plan = await self.get_meal_plan_by_id(meal_plan_id)
        if not meal_plan:
            return False
        
        await self.db.delete(meal_plan)
        await self.db.commit()
        return True
    
    async def add_recipe_to_meal_plan(
        self,
        meal_plan_id: uuid.UUID,
        recipe_id: uuid.UUID,
        scheduled_date: datetime,
        meal_type: str,
        servings_multiplier: float = 1.0,
        notes: Optional[str] = None
    ) -> MealPlanRecipe:
        """Add a recipe to a meal plan."""
        meal_plan_recipe = MealPlanRecipe(
            meal_plan_id=meal_plan_id,
            recipe_id=recipe_id,
            scheduled_date=scheduled_date,
            meal_type=meal_type,
            servings_multiplier=servings_multiplier,
            notes=notes
        )
        
        self.db.add(meal_plan_recipe)
        await self.db.commit()
        await self.db.refresh(meal_plan_recipe)
        return meal_plan_recipe
    
    async def remove_recipe_from_meal_plan(
        self,
        meal_plan_id: uuid.UUID,
        recipe_id: uuid.UUID,
        scheduled_date: datetime,
        meal_type: str
    ) -> bool:
        """Remove a recipe from a meal plan."""
        result = await self.db.execute(
            select(MealPlanRecipe).where(
                and_(
                    MealPlanRecipe.meal_plan_id == meal_plan_id,
                    MealPlanRecipe.recipe_id == recipe_id,
                    MealPlanRecipe.scheduled_date == scheduled_date,
                    MealPlanRecipe.meal_type == meal_type
                )
            )
        )
        meal_plan_recipe = result.scalar_one_or_none()
        
        if not meal_plan_recipe:
            return False
        
        await self.db.delete(meal_plan_recipe)
        await self.db.commit()
        return True
    
    async def create_grocery_list(
        self,
        meal_plan_id: uuid.UUID,
        user_id: uuid.UUID,
        items: List[dict],
        name: Optional[str] = None,
        total_estimated_cost: Optional[float] = None
    ) -> GroceryList:
        """Create a grocery list for a meal plan."""
        grocery_list = GroceryList(
            meal_plan_id=meal_plan_id,
            user_id=user_id,
            name=name,
            items=items,
            total_estimated_cost=total_estimated_cost
        )
        
        self.db.add(grocery_list)
        await self.db.commit()
        await self.db.refresh(grocery_list)
        return grocery_list
    
    async def get_grocery_list_by_meal_plan(self, meal_plan_id: uuid.UUID) -> Optional[GroceryList]:
        """Get grocery list for a meal plan."""
        result = await self.db.execute(
            select(GroceryList).where(GroceryList.meal_plan_id == meal_plan_id)
        )
        return result.scalar_one_or_none()


class RecipeRatingService:
    """Service for recipe rating operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_rating(
        self,
        user_id: uuid.UUID,
        recipe_id: uuid.UUID,
        rating: int,
        review: Optional[str] = None,
        difficulty_rating: Optional[int] = None,
        would_make_again: Optional[bool] = None
    ) -> RecipeRating:
        """Create a recipe rating."""
        recipe_rating = RecipeRating(
            user_id=user_id,
            recipe_id=recipe_id,
            rating=rating,
            review=review,
            difficulty_rating=difficulty_rating,
            would_make_again=would_make_again
        )
        
        self.db.add(recipe_rating)
        await self.db.commit()
        await self.db.refresh(recipe_rating)
        
        # Update recipe average rating
        await self._update_recipe_average_rating(recipe_id)
        
        return recipe_rating
    
    async def get_ratings_for_recipe(self, recipe_id: uuid.UUID) -> List[RecipeRating]:
        """Get all ratings for a recipe."""
        result = await self.db.execute(
            select(RecipeRating)
            .options(selectinload(RecipeRating.user))
            .where(RecipeRating.recipe_id == recipe_id)
            .order_by(desc(RecipeRating.created_at))
        )
        return result.scalars().all()
    
    async def get_user_rating_for_recipe(
        self,
        user_id: uuid.UUID,
        recipe_id: uuid.UUID
    ) -> Optional[RecipeRating]:
        """Get a user's rating for a specific recipe."""
        result = await self.db.execute(
            select(RecipeRating).where(
                and_(
                    RecipeRating.user_id == user_id,
                    RecipeRating.recipe_id == recipe_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update_rating(
        self,
        user_id: uuid.UUID,
        recipe_id: uuid.UUID,
        **kwargs
    ) -> Optional[RecipeRating]:
        """Update a recipe rating."""
        rating = await self.get_user_rating_for_recipe(user_id, recipe_id)
        if not rating:
            return None
        
        for key, value in kwargs.items():
            setattr(rating, key, value)
        
        await self.db.commit()
        await self.db.refresh(rating)
        
        # Update recipe average rating
        await self._update_recipe_average_rating(recipe_id)
        
        return rating
    
    async def delete_rating(self, user_id: uuid.UUID, recipe_id: uuid.UUID) -> bool:
        """Delete a recipe rating."""
        rating = await self.get_user_rating_for_recipe(user_id, recipe_id)
        if not rating:
            return False
        
        await self.db.delete(rating)
        await self.db.commit()
        
        # Update recipe average rating
        await self._update_recipe_average_rating(recipe_id)
        
        return True
    
    async def _update_recipe_average_rating(self, recipe_id: uuid.UUID):
        """Update the average rating for a recipe."""
        # Get average rating and count
        result = await self.db.execute(
            select(
                func.avg(RecipeRating.rating).label('avg_rating'),
                func.count(RecipeRating.rating).label('rating_count')
            ).where(RecipeRating.recipe_id == recipe_id)
        )
        row = result.fetchone()
        
        avg_rating = row.avg_rating or 0.0
        rating_count = row.rating_count or 0
        
        # Update recipe
        recipe_result = await self.db.execute(
            select(Recipe).where(Recipe.id == recipe_id)
        )
        recipe = recipe_result.scalar_one_or_none()
        
        if recipe:
            recipe.average_rating = float(avg_rating)
            recipe.rating_count = int(rating_count)
            await self.db.commit()