/**
 * API service for interacting with the meal planner backend.
 */

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * API client for the meal planner backend.
 */
const api = {
    /**
     * Fetch recipes with optional pagination.
     * 
     * @param {number} limit - Maximum number of recipes to return
     * @param {number} offset - Offset for pagination
     * @returns {Promise<Array>} - Promise resolving to an array of recipes
     */
    async getRecipes(limit = 20, offset = 0) {
        try {
            const response = await fetch(`${API_BASE_URL}/recipes?limit=${limit}&offset=${offset}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch recipes: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching recipes:', error);
            throw error;
        }
    },
    
    /**
     * Fetch a recipe by ID.
     * 
     * @param {string} recipeId - Recipe ID
     * @returns {Promise<Object>} - Promise resolving to a recipe object
     */
    async getRecipe(recipeId) {
        try {
            const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch recipe: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error fetching recipe ${recipeId}:`, error);
            throw error;
        }
    },
    
    /**
     * Create a new recipe.
     * 
     * @param {Object} recipe - Recipe object
     * @returns {Promise<Object>} - Promise resolving to the created recipe
     */
    async createRecipe(recipe) {
        try {
            const response = await fetch(`${API_BASE_URL}/recipes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(recipe)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create recipe: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating recipe:', error);
            throw error;
        }
    },
    
    /**
     * Update a recipe.
     * 
     * @param {string} recipeId - Recipe ID
     * @param {Object} recipe - Updated recipe object
     * @returns {Promise<Object>} - Promise resolving to the updated recipe
     */
    async updateRecipe(recipeId, recipe) {
        try {
            const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(recipe)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to update recipe: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error updating recipe ${recipeId}:`, error);
            throw error;
        }
    },
    
    /**
     * Delete a recipe.
     * 
     * @param {string} recipeId - Recipe ID
     * @returns {Promise<Object>} - Promise resolving to the deletion status
     */
    async deleteRecipe(recipeId) {
        try {
            const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to delete recipe: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error deleting recipe ${recipeId}:`, error);
            throw error;
        }
    },
    
    /**
     * Search recipes.
     * 
     * @param {string} query - Search query
     * @param {number} limit - Maximum number of recipes to return
     * @returns {Promise<Array>} - Promise resolving to an array of matching recipes
     */
    async searchRecipes(query, limit = 20) {
        try {
            const response = await fetch(`${API_BASE_URL}/recipes/search?query=${encodeURIComponent(query)}&limit=${limit}`);
            
            if (!response.ok) {
                throw new Error(`Failed to search recipes: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error searching recipes with query "${query}":`, error);
            throw error;
        }
    },
    
    /**
     * Analyze nutrition information for a recipe.
     * 
     * @param {string} recipeId - Recipe ID
     * @returns {Promise<Object>} - Promise resolving to nutrition information
     */
    async analyzeRecipeNutrition(recipeId) {
        try {
            const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}/analyze-nutrition`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to analyze recipe nutrition: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error analyzing nutrition for recipe ${recipeId}:`, error);
            throw error;
        }
    },
    
    /**
     * Generate a meal plan.
     * 
     * @param {Object} mealPlanRequest - Meal plan request object
     * @returns {Promise<Object>} - Promise resolving to a meal plan response
     */
    async generateMealPlan(mealPlanRequest) {
        try {
            const response = await fetch(`${API_BASE_URL}/meal-plans`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(mealPlanRequest)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to generate meal plan: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error generating meal plan:', error);
            throw error;
        }
    },
    
    /**
     * Fetch meal plans with optional user filtering.
     * 
     * @param {string} userId - Optional user ID to filter by
     * @returns {Promise<Array>} - Promise resolving to an array of meal plans
     */
    async getMealPlans(userId = null) {
        try {
            let url = `${API_BASE_URL}/meal-plans`;
            
            if (userId) {
                url += `?user_id=${userId}`;
            }
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch meal plans: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching meal plans:', error);
            throw error;
        }
    },
    
    /**
     * Fetch a meal plan by ID.
     * 
     * @param {string} mealPlanId - Meal plan ID
     * @returns {Promise<Object>} - Promise resolving to a meal plan object
     */
    async getMealPlan(mealPlanId) {
        try {
            const response = await fetch(`${API_BASE_URL}/meal-plans/${mealPlanId}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch meal plan: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error fetching meal plan ${mealPlanId}:`, error);
            throw error;
        }
    },
    
    /**
     * Delete a meal plan.
     * 
     * @param {string} mealPlanId - Meal plan ID
     * @returns {Promise<Object>} - Promise resolving to the deletion status
     */
    async deleteMealPlan(mealPlanId) {
        try {
            const response = await fetch(`${API_BASE_URL}/meal-plans/${mealPlanId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to delete meal plan: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error deleting meal plan ${mealPlanId}:`, error);
            throw error;
        }
    },
    
    /**
     * Fetch the grocery list for a meal plan.
     * 
     * @param {string} mealPlanId - Meal plan ID
     * @returns {Promise<Object>} - Promise resolving to a grocery list object
     */
    async getMealPlanGroceryList(mealPlanId) {
        try {
            const response = await fetch(`${API_BASE_URL}/meal-plans/${mealPlanId}/grocery-list`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch grocery list: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error fetching grocery list for meal plan ${mealPlanId}:`, error);
            throw error;
        }
    }
};
