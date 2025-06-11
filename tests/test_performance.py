"""Performance and integration tests - Fixed version."""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch


class TestDatabasePerformance:
    """Test database performance under load."""
    
    @pytest.mark.asyncio
    async def test_create_many_recipes_performance(self, recipe_service, test_user):
        """Test creating many recipes quickly."""
        start_time = time.time()
        
        # Create 50 recipes
        recipes = []
        for i in range(50):
            recipe_data = {
                "title": f"Performance Test Recipe {i}",
                "ingredients": [f"ingredient_{i}_1", f"ingredient_{i}_2"],
                "instructions": [f"step_{i}_1", f"step_{i}_2"],
                "meal_types": ["dinner"],
                "tags": [f"test_{i}"]
            }
            
            recipe = await recipe_service.create_recipe(
                user_id=test_user.id,
                recipe_data=recipe_data
            )
            recipes.append(recipe)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 50 recipes in reasonable time (less than 10 seconds)
        assert duration < 10.0
        assert len(recipes) == 50
        
        # Verify all recipes were created properly
        for i, recipe in enumerate(recipes):
            assert recipe.title == f"Performance Test Recipe {i}"
    
    @pytest.mark.asyncio
    async def test_search_performance_with_many_recipes(self, recipe_service, test_user):
        """Test search performance with many recipes."""
        # First create many recipes with searchable content
        for i in range(20):
            recipe_data = {
                "title": f"Searchable Recipe {i}" + (" chicken" if i % 3 == 0 else " pasta"),
                "ingredients": ["ingredient1", "ingredient2"],
                "instructions": ["step1", "step2"],
                "meal_types": ["dinner"],
                "tags": ["searchable"]
            }
            await recipe_service.create_recipe(test_user.id, recipe_data)
        
        # Test search performance
        start_time = time.time()
        
        results = await recipe_service.search_recipes("chicken")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Search should be fast (less than 1 second)
        assert duration < 1.0
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_recipe_creation(self, test_session_factory, test_user):
        """Test concurrent recipe creation."""
        async def create_recipe(session_factory, user_id, index):
            async with session_factory() as session:
                from meal_planner.db.services import RecipeService
                service = RecipeService(session)
                
                recipe_data = {
                    "title": f"Concurrent Recipe {index}",
                    "ingredients": [f"ingredient_{index}"],
                    "instructions": [f"step_{index}"],
                    "meal_types": ["lunch"]
                }
                
                return await service.create_recipe(user_id, recipe_data)
        
        # Create 10 recipes concurrently
        tasks = [
            create_recipe(test_session_factory, test_user.id, i)
            for i in range(10)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Concurrent creation should be faster than sequential
        assert duration < 5.0
        assert len(results) == 10
        assert all(recipe.id is not None for recipe in results)


class TestAPIPerformance:
    """Test API endpoint performance."""
    
    def test_api_response_times(self, test_client):
        """Test that API responses are fast enough."""
        endpoints_to_test = [
            ("/api", "GET"),
            ("/api/health", "GET"), 
            ("/api/health/system", "GET"),
            ("/api/recipes", "GET"),
            ("/api/meal-plans", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            start_time = time.time()
            
            if method == "GET":
                response = test_client.get(endpoint)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # All endpoints should respond within 2 seconds
            assert duration < 2.0
            assert response.status_code in [200, 404, 422]  # Valid response codes
    
    def test_api_concurrent_requests(self, test_client):
        """Test API handling concurrent requests."""
        def make_request():
            return test_client.get("/api/health")
        
        # Make 20 concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        duration = end_time - start_time
        
        # Should handle 20 concurrent requests quickly
        assert duration < 5.0
        assert all(result.status_code == 200 for result in results)
    
    def test_large_recipe_creation(self, test_client):
        """Test creating recipe with large amount of data."""
        # Create a recipe with many ingredients and instructions
        large_recipe = {
            "title": "Large Recipe Test",
            "ingredients": [f"Ingredient {i}" for i in range(100)],
            "instructions": [f"Step {i}: Do something." for i in range(50)],
            "meal_types": ["dinner"],
            "tags": [f"tag{i}" for i in range(20)],
            "notes": "This is a very long note. " * 100  # Long text
        }
        
        start_time = time.time()
        response = test_client.post("/api/recipes", json=large_recipe)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should handle large recipe data efficiently
        assert duration < 3.0
        if response.status_code == 200:
            data = response.json()
            assert len(data["ingredients"]) == 100
            assert len(data["instructions"]) == 50



class TestIntegrationScenarios:
    """Test complete user scenarios."""
    
    def test_complete_recipe_workflow(self, test_client):
        """Test complete recipe management workflow."""
        # 1. Create a recipe
        recipe_data = {
            "title": "Integration Test Recipe",
            "ingredients": ["flour", "eggs", "milk"],
            "instructions": ["Mix ingredients", "Cook", "Serve"],
            "meal_types": ["breakfast"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 15
        }
        
        create_response = test_client.post("/api/recipes", json=recipe_data)
        assert create_response.status_code == 200
        recipe = create_response.json()
        recipe_id = recipe["id"]
        
        # 2. Get the recipe
        get_response = test_client.get(f"/api/recipes/{recipe_id}")
        assert get_response.status_code == 200
        retrieved_recipe = get_response.json()
        assert retrieved_recipe["title"] == recipe_data["title"]
        
        # 3. Update the recipe
        update_data = {
            "title": "Updated Integration Recipe",
            "prep_time_minutes": 20
        }
        update_response = test_client.put(f"/api/recipes/{recipe_id}", json=update_data)
        assert update_response.status_code == 200
        updated_recipe = update_response.json()
        assert updated_recipe["title"] == "Updated Integration Recipe"
        assert updated_recipe["prep_time_minutes"] == 20
        
        # 4. Search for the recipe
        search_response = test_client.get("/api/recipes/search?query=Integration")
        assert search_response.status_code == 200
        search_results = search_response.json()
        found_recipe = next((r for r in search_results if r["id"] == recipe_id), None)
        assert found_recipe is not None
        
        # 5. List all recipes (use larger limit to ensure we find it)
        list_response = test_client.get("/api/recipes?limit=100")
        assert list_response.status_code == 200
        all_recipes = list_response.json()
        recipe_ids = [r["id"] for r in all_recipes]
        assert recipe_id in recipe_ids
        
        # 6. Delete the recipe
        delete_response = test_client.delete(f"/api/recipes/{recipe_id}")
        assert delete_response.status_code == 200
        
        # 7. Verify deletion
        final_get_response = test_client.get(f"/api/recipes/{recipe_id}")
        assert final_get_response.status_code == 404


    def test_multiple_user_simulation(self, test_session_factory):
        """Simulate multiple users using the system."""
        async def user_workflow(session_factory, user_index):
            async with session_factory() as session:
                from meal_planner.db.services import UserService, RecipeService
                
                # Create user
                user_service = UserService(session)
                user = await user_service.create_user(
                    email=f"user{user_index}@test.com",
                    full_name=f"Test User {user_index}"
                )
                
                # Create recipes for this user
                recipe_service = RecipeService(session)
                recipes = []
                for i in range(3):
                    recipe_data = {
                        "title": f"User {user_index} Recipe {i}",
                        "ingredients": [f"ingredient_{user_index}_{i}"],
                        "instructions": [f"step_{user_index}_{i}"],
                        "meal_types": ["dinner"]
                    }
                    recipe = await recipe_service.create_recipe(user.id, recipe_data)
                    recipes.append(recipe)
                
                return user, recipes
        
        async def run_simulation():
            # Simulate 5 users
            tasks = [
                user_workflow(test_session_factory, i)
                for i in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Verify all users and recipes were created
            assert len(results) == 5
            for user, recipes in results:
                assert user.id is not None
                assert len(recipes) == 3
                assert all(r.user_id == user.id for r in recipes)
        
        # Run the simulation
        asyncio.run(run_simulation())
    
    @pytest.mark.asyncio
    async def test_data_consistency_under_load(self, test_session_factory, test_user):
        """Test data consistency when multiple operations happen simultaneously."""
        async def update_recipe_rating(session_factory, recipe_id, rating_value):
            async with session_factory() as session:
                from meal_planner.db.services import RecipeService
                service = RecipeService(session)
                
                # Simulate updating recipe rating
                recipe = await service.get_recipe_by_id(recipe_id)
                if recipe:
                    # Update average rating (simplified)
                    new_rating = (recipe.average_rating + rating_value) / 2
                    await service.update_recipe(recipe_id, {"average_rating": new_rating})
                    return new_rating
                return None
        
        # First create a recipe
        async with test_session_factory() as session:
            from meal_planner.db.services import RecipeService
            service = RecipeService(session)
            
            recipe = await service.create_recipe(
                user_id=test_user.id,
                recipe_data={
                    "title": "Consistency Test Recipe",
                    "ingredients": ["ingredient1"],
                    "instructions": ["step1"],
                    "meal_types": ["dinner"]
                }
            )
            recipe_id = recipe.id
        
        # Simulate concurrent rating updates
        tasks = [
            update_recipe_rating(test_session_factory, recipe_id, rating)
            for rating in [5.0, 4.0, 3.0, 5.0, 4.0]
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should handle concurrent updates without errors
        successful_updates = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_updates) > 0
        
        # Verify final state is consistent
        async with test_session_factory() as session:
            from meal_planner.db.services import RecipeService
            service = RecipeService(session)
            final_recipe = await service.get_recipe_by_id(recipe_id)
            
            assert final_recipe is not None
            assert isinstance(final_recipe.average_rating, (int, float))
            assert 0 <= final_recipe.average_rating <= 5


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_api_invalid_json(self, test_client):
        """Test API handling of invalid JSON."""
        response = test_client.post(
            "/api/recipes",
            data="invalid json data",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_api_missing_required_fields(self, test_client):
        """Test API validation of required fields."""
        incomplete_recipe = {
            "title": "Incomplete Recipe"
            # Missing required ingredients and instructions
        }
        
        response = test_client.post("/api/recipes", json=incomplete_recipe)
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_database_constraint_violations(self, user_service):
        """Test database constraint handling."""
        # Create a user
        user1 = await user_service.create_user(
            email="duplicate@test.com",
            full_name="First User"
        )
        assert user1.id is not None
        
        # Try to create another user with same email
        with pytest.raises(Exception):  # Should raise integrity error
            await user_service.create_user(
                email="duplicate@test.com",  # Duplicate email
                full_name="Second User"
            )
    
    def test_api_rate_limiting_simulation(self, test_client):
        """Simulate high request rate to test stability."""
        # Make many requests quickly
        responses = []
        for i in range(100):
            response = test_client.get("/api/health")
            responses.append(response)
        
        # Should handle all requests without crashing
        success_count = sum(1 for r in responses if r.status_code == 200)
        
        # At least 90% should succeed
        assert success_count >= 90