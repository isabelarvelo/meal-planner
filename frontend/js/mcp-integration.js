/**
 * MCP integration for the Meal Planner frontend.
 * 
 * This file provides integration with the Model Context Protocol (MCP) server
 * for enhanced functionality such as recipe search, nutrition analysis,
 * and meal plan generation.
 */

/**
 * MCP client for the meal planner.
 */
const mcpClient = {
    /**
     * Initialize MCP client.
     */
    init() {
        // Add MCP integration to the recipe manager
        this.enhanceRecipeManager();
        
        // Add MCP integration to the meal plan manager
        this.enhanceMealPlanManager();
        
        console.log('MCP integration initialized');
    },
    
    /**
     * Enhance recipe manager with MCP capabilities.
     */
    enhanceRecipeManager() {
        // Store original search method
        const originalSearchMethod = recipeManager.searchRecipes;
        
        // Override search method to use MCP for enhanced search
        recipeManager.searchRecipes = async function() {
            const query = this.searchInput.value.trim();
            
            if (!query) {
                this.loadRecipes();
                return;
            }
            
            try {
                this.recipesContainer.innerHTML = `<div class="loading">Searching for "${query}"...</div>`;
                
                // Try to use MCP search first
                try {
                    const mcpResults = await mcpClient.searchRecipes(query);
                    
                    if (mcpResults && mcpResults.length > 0) {
                        this.renderRecipes(mcpResults);
                        return;
                    }
                } catch (mcpError) {
                    console.warn('MCP search failed, falling back to API search:', mcpError);
                }
                
                // Fall back to original search method
                const recipes = await api.searchRecipes(query);
                
                if (recipes.length === 0) {
                    this.recipesContainer.innerHTML = `<div class="loading">No recipes found for "${query}"</div>`;
                    return;
                }
                
                this.renderRecipes(recipes);
            } catch (error) {
                console.error('Error searching recipes:', error);
                this.recipesContainer.innerHTML = `<div class="loading">Error searching recipes: ${error.message}</div>`;
            }
        };
        
        // Store original nutrition analysis method
        const originalAnalyzeMethod = api.analyzeRecipeNutrition;
        
        // Override nutrition analysis method to use MCP for enhanced analysis
        api.analyzeRecipeNutrition = async function(recipeId) {
            try {
                // Try to use MCP nutrition analysis first
                try {
                    const mcpResult = await mcpClient.analyzeNutrition(recipeId);
                    if (mcpResult) {
                        return mcpResult;
                    }
                } catch (mcpError) {
                    console.warn('MCP nutrition analysis failed, falling back to API:', mcpError);
                }
                
                // Fall back to original method
                return await originalAnalyzeMethod(recipeId);
            } catch (error) {
                console.error('Error analyzing nutrition:', error);
                throw error;
            }
        };
    },
    
    /**
     * Enhance meal plan manager with MCP capabilities.
     */
    enhanceMealPlanManager() {
        // Store original generate method
        const originalGenerateMethod = mealPlanManager.generateMealPlan;
        
        // Override generate method to use MCP for enhanced meal plan generation
        mealPlanManager.generateMealPlan = async function() {
            try {
                const formData = new FormData(this.mealPlanForm);
                
                // Get form values
                const startDate = formData.get('start_date');
                const endDate = formData.get('end_date');
                const mealTypes = formData.getAll('meal_types');
                const nutritionGoal = formData.get('nutrition_goal');
                const budgetLimit = formData.get('budget_limit') ? parseFloat(formData.get('budget_limit')) : null;
                
                // Create meal plan request
                const mealPlanRequest = {
                    user_id: DEFAULT_USER_ID,
                    start_date: startDate,
                    end_date: endDate,
                    meal_types: mealTypes,
                    nutrition_goal: nutritionGoal || null,
                    budget_limit: budgetLimit,
                    preferences: {}
                };
                
                // Show loading message
                const submitButton = this.mealPlanForm.querySelector('button[type="submit"]');
                const originalButtonText = submitButton.textContent;
                submitButton.textContent = 'Generating...';
                submitButton.disabled = true;
                
                // Try to use MCP meal plan generation first
                let response;
                try {
                    response = await mcpClient.generateMealPlan(mealPlanRequest);
                } catch (mcpError) {
                    console.warn('MCP meal plan generation failed, falling back to API:', mcpError);
                    // Fall back to original method
                    response = await api.generateMealPlan(mealPlanRequest);
                }
                
                // Reset button
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
                
                // Close modal and reload meal plans
                this.mealPlanModal.classList.remove('active');
                
                // Show the newly created meal plan
                this.showMealPlanDetail(response.meal_plan.id);
                
                // Reload meal plans in the background
                this.loadMealPlans();
            } catch (error) {
                console.error('Error generating meal plan:', error);
                alert(`Error generating meal plan: ${error.message}`);
                
                // Reset button
                const submitButton = this.mealPlanForm.querySelector('button[type="submit"]');
                submitButton.textContent = 'Generate Meal Plan';
                submitButton.disabled = false;
            }
        };
    },
    
    /**
     * Search recipes using MCP.
     * 
     * @param {string} query - Search query
     * @returns {Promise<Array>} - Promise resolving to an array of recipes
     */
    async searchRecipes(query) {
        try {
            const response = await fetch('/mcp/search-recipes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });
            
            if (!response.ok) {
                throw new Error(`MCP search failed: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('MCP search error:', error);
            throw error;
        }
    },
    
    /**
     * Analyze nutrition information for a recipe using MCP.
     * 
     * @param {string} recipeId - Recipe ID
     * @returns {Promise<Object>} - Promise resolving to nutrition information
     */
    async analyzeNutrition(recipeId) {
        try {
            const response = await fetch('/mcp/analyze-nutrition', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ recipe_id: recipeId })
            });
            
            if (!response.ok) {
                throw new Error(`MCP nutrition analysis failed: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('MCP nutrition analysis error:', error);
            throw error;
        }
    },
    
    /**
     * Generate a meal plan using MCP.
     * 
     * @param {Object} mealPlanRequest - Meal plan request object
     * @returns {Promise<Object>} - Promise resolving to a meal plan response
     */
    async generateMealPlan(mealPlanRequest) {
        try {
            const response = await fetch('/mcp/generate-meal-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(mealPlanRequest)
            });
            
            if (!response.ok) {
                throw new Error(`MCP meal plan generation failed: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('MCP meal plan generation error:', error);
            throw error;
        }
    }
};

// Initialize MCP client when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Initialize MCP client after a short delay to ensure other components are loaded
    setTimeout(() => {
        mcpClient.init();
    }, 500);
});
