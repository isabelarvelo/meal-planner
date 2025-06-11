/**
 * Recipe-related functionality.
 */

// Default user ID for demo purposes
const DEFAULT_USER_ID = '00000000-0000-0000-0000-000000000001';

/**
 * Recipe manager.
 */
const recipeManager = {
    /**
     * Initialize recipe functionality.
     */
    init() {
        this.recipesContainer = document.getElementById('recipes-container');
        this.recipeModal = document.getElementById('recipe-modal');
        this.recipeDetailContent = document.getElementById('recipe-detail-content');
        this.addRecipeModal = document.getElementById('add-recipe-modal');
        this.recipeForm = document.getElementById('recipe-form');
        this.recipeFormTitle = document.getElementById('recipe-form-title');
        this.searchInput = document.getElementById('recipe-search');
        this.searchButton = document.getElementById('search-button');
        this.addRecipeButton = document.getElementById('add-recipe-button');
        
        // Attach event listeners
        this.searchButton.addEventListener('click', () => this.searchRecipes());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchRecipes();
            }
        });
        
        this.addRecipeButton.addEventListener('click', () => this.showAddRecipeModal());
        
        this.recipeForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveRecipe();
        });
        
        // Close buttons for modals
        document.querySelectorAll('.close-button, .cancel-button').forEach(button => {
            button.addEventListener('click', () => {
                this.recipeModal.classList.remove('active');
                this.addRecipeModal.classList.remove('active');
            });
        });
        
        // Load recipes
        this.loadRecipes();
    },
    
    /**
     * Load recipes from the API.
     */
    async loadRecipes() {
        try {
            this.recipesContainer.innerHTML = '<div class="loading">Loading recipes...</div>';
            
            const recipes = await api.getRecipes();
            
            if (recipes.length === 0) {
                this.recipesContainer.innerHTML = '<div class="loading">No recipes found. Add your first recipe!</div>';
                return;
            }
            
            this.renderRecipes(recipes);
        } catch (error) {
            console.error('Error loading recipes:', error);
            this.recipesContainer.innerHTML = `<div class="loading">Error loading recipes: ${error.message}</div>`;
        }
    },
    
    /**
     * Search recipes.
     */
    async searchRecipes() {
        const query = this.searchInput.value.trim();
        
        if (!query) {
            this.loadRecipes();
            return;
        }
        
        try {
            this.recipesContainer.innerHTML = `<div class="loading">Searching for "${query}"...</div>`;
            
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
    },
    
    /**
     * Render recipes in the container.
     * 
     * @param {Array} recipes - Array of recipe objects
     */
    renderRecipes(recipes) {
        this.recipesContainer.innerHTML = '';
        
        recipes.forEach(recipe => {
            const card = document.createElement('div');
            card.className = 'card';
            card.dataset.id = recipe.id;
            
            // Generate a placeholder image based on the recipe title
            const placeholderImage = `https://via.placeholder.com/300x180/c8e6c9/388e3c?text=${encodeURIComponent(recipe.title.substring(0, 20))}`;
            
            // Format meal types
            const mealTypes = recipe.meal_types.map(type => {
                return type.charAt(0).toUpperCase() + type.slice(1);
            }).join(', ');
            
            // Format time
            const prepTime = recipe.prep_time_minutes ? `${recipe.prep_time_minutes} min` : 'N/A';
            const cookTime = recipe.cook_time_minutes ? `${recipe.cook_time_minutes} min` : 'N/A';
            
            // Format tags
            const tags = recipe.tags.map(tag => {
                return `<span class="tag">${tag}</span>`;
            }).join('');
            
            card.innerHTML = `
                <div class="card-image" style="background-image: url('${placeholderImage}')"></div>
                <div class="card-content">
                    <h3 class="card-title">${recipe.title}</h3>
                    <div class="card-meta">
                        <span><i class="fas fa-utensils"></i> ${mealTypes}</span>
                        <span><i class="fas fa-clock"></i> Prep: ${prepTime}</span>
                        <span><i class="fas fa-fire"></i> Cook: ${cookTime}</span>
                    </div>
                    <div class="card-tags">
                        ${tags}
                    </div>
                    <div class="card-actions">
                        <button class="icon-button edit-recipe-button" title="Edit Recipe">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="icon-button delete-recipe-button" title="Delete Recipe">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button class="primary-button view-recipe-button">View Recipe</button>
                    </div>
                </div>
            `;
            
            // Attach event listeners
            card.querySelector('.view-recipe-button').addEventListener('click', () => {
                this.showRecipeDetail(recipe.id);
            });
            
            card.querySelector('.edit-recipe-button').addEventListener('click', () => {
                this.showEditRecipeModal(recipe.id);
            });
            
            card.querySelector('.delete-recipe-button').addEventListener('click', () => {
                this.deleteRecipe(recipe.id);
            });
            
            this.recipesContainer.appendChild(card);
        });
    },
    
    /**
     * Show recipe detail modal.
     * 
     * @param {string} recipeId - Recipe ID
     */
    async showRecipeDetail(recipeId) {
        try {
            this.recipeDetailContent.innerHTML = '<div class="loading">Loading recipe...</div>';
            this.recipeModal.classList.add('active');
            
            const recipe = await api.getRecipe(recipeId);
            
            // Format meal types
            const mealTypes = recipe.meal_types.map(type => {
                return type.charAt(0).toUpperCase() + type.slice(1);
            }).join(', ');
            
            // Format time
            const prepTime = recipe.prep_time_minutes ? `${recipe.prep_time_minutes} min` : 'N/A';
            const cookTime = recipe.cook_time_minutes ? `${recipe.cook_time_minutes} min` : 'N/A';
            const totalTime = recipe.prep_time_minutes && recipe.cook_time_minutes
                ? `${recipe.prep_time_minutes + recipe.cook_time_minutes} min`
                : 'N/A';
            
            // Format ingredients
            let ingredientsList = '';
            if (Array.isArray(recipe.ingredients)) {
                ingredientsList = recipe.ingredients.map(ingredient => {
                    if (typeof ingredient === 'string') {
                        return `<li>${ingredient}</li>`;
                    } else if (typeof ingredient === 'object') {
                        const quantity = ingredient.quantity ? `${ingredient.quantity} ` : '';
                        const unit = ingredient.unit ? `${ingredient.unit} ` : '';
                        return `<li>${quantity}${unit}${ingredient.name}</li>`;
                    }
                    return '';
                }).join('');
            }
            
            // Format instructions
            const instructionsList = recipe.instructions.map((instruction, index) => {
                return `<li>${instruction}</li>`;
            }).join('');
            
            // Format tags
            const tags = recipe.tags.map(tag => {
                return `<span class="tag">${tag}</span>`;
            }).join('');
            
            // Format dietary restrictions
            const dietaryRestrictions = recipe.dietary_restrictions.map(restriction => {
                return `<span class="tag">${restriction.replace('_', ' ')}</span>`;
            }).join('');
            
            this.recipeDetailContent.innerHTML = `
                <div class="recipe-detail">
                    <div class="recipe-detail-header">
                        <h2 class="recipe-detail-title">${recipe.title}</h2>
                        <div class="recipe-detail-meta">
                            <span><i class="fas fa-utensils"></i> ${mealTypes}</span>
                            <span><i class="fas fa-clock"></i> Prep: ${prepTime}</span>
                            <span><i class="fas fa-fire"></i> Cook: ${cookTime}</span>
                            <span><i class="fas fa-hourglass-half"></i> Total: ${totalTime}</span>
                            <span><i class="fas fa-users"></i> Servings: ${recipe.servings || 'N/A'}</span>
                        </div>
                        <div class="recipe-detail-tags">
                            ${tags}
                        </div>
                    </div>
                    
                    <div class="recipe-detail-section">
                        <h3>Ingredients</h3>
                        <ul class="recipe-ingredients">
                            ${ingredientsList}
                        </ul>
                    </div>
                    
                    <div class="recipe-detail-section">
                        <h3>Instructions</h3>
                        <ol class="recipe-instructions">
                            ${instructionsList}
                        </ol>
                    </div>
                    
                    ${dietaryRestrictions ? `
                    <div class="recipe-detail-section">
                        <h3>Dietary Restrictions</h3>
                        <div class="recipe-detail-tags">
                            ${dietaryRestrictions}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${recipe.nutrition ? `
                    <div class="recipe-detail-section">
                        <h3>Nutrition Information</h3>
                        <div class="recipe-nutrition">
                            <p>Calories: ${recipe.nutrition.calories || 'N/A'}</p>
                            <p>Protein: ${recipe.nutrition.protein_grams ? `${recipe.nutrition.protein_grams}g` : 'N/A'}</p>
                            <p>Carbs: ${recipe.nutrition.carbs_grams ? `${recipe.nutrition.carbs_grams}g` : 'N/A'}</p>
                            <p>Fat: ${recipe.nutrition.fat_grams ? `${recipe.nutrition.fat_grams}g` : 'N/A'}</p>
                        </div>
                    </div>
                    ` : `
                    <div class="recipe-detail-section">
                        <button id="analyze-nutrition-button" class="primary-button">Analyze Nutrition</button>
                    </div>
                    `}
                </div>
            `;
            
            // Attach event listener for nutrition analysis
            const analyzeButton = document.getElementById('analyze-nutrition-button');
            if (analyzeButton) {
                analyzeButton.addEventListener('click', async () => {
                    try {
                        analyzeButton.textContent = 'Analyzing...';
                        analyzeButton.disabled = true;
                        
                        await api.analyzeRecipeNutrition(recipeId);
                        
                        // Refresh recipe detail
                        this.showRecipeDetail(recipeId);
                    } catch (error) {
                        console.error('Error analyzing nutrition:', error);
                        analyzeButton.textContent = 'Analyze Nutrition';
                        analyzeButton.disabled = false;
                        alert(`Error analyzing nutrition: ${error.message}`);
                    }
                });
            }
        } catch (error) {
            console.error('Error showing recipe detail:', error);
            this.recipeDetailContent.innerHTML = `<div class="loading">Error loading recipe: ${error.message}</div>`;
        }
    },
    
    /**
     * Show add recipe modal.
     */
    showAddRecipeModal() {
        this.recipeFormTitle.textContent = 'Add Recipe';
        this.recipeForm.reset();
        this.recipeForm.dataset.mode = 'add';
        this.addRecipeModal.classList.add('active');
    },
    
    /**
     * Show edit recipe modal.
     * 
     * @param {string} recipeId - Recipe ID
     */
    async showEditRecipeModal(recipeId) {
        try {
            this.recipeFormTitle.textContent = 'Edit Recipe';
            this.recipeForm.reset();
            this.recipeForm.dataset.mode = 'edit';
            this.recipeForm.dataset.recipeId = recipeId;
            
            const recipe = await api.getRecipe(recipeId);
            
            // Fill form fields
            document.getElementById('recipe-title').value = recipe.title;
            
            // Check meal types
            recipe.meal_types.forEach(type => {
                const checkbox = document.querySelector(`input[name="meal_types"][value="${type}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
            
            // Format ingredients
            let ingredientsText = '';
            if (Array.isArray(recipe.ingredients)) {
                ingredientsText = recipe.ingredients.map(ingredient => {
                    if (typeof ingredient === 'string') {
                        return ingredient;
                    } else if (typeof ingredient === 'object') {
                        const quantity = ingredient.quantity ? `${ingredient.quantity} ` : '';
                        const unit = ingredient.unit ? `${ingredient.unit} ` : '';
                        return `${quantity}${unit}${ingredient.name}`;
                    }
                    return '';
                }).join('\n');
            }
            document.getElementById('recipe-ingredients').value = ingredientsText;
            
            // Format instructions
            document.getElementById('recipe-instructions').value = recipe.instructions.join('\n');
            
            // Set other fields
            document.getElementById('recipe-prep-time').value = recipe.prep_time_minutes || '';
            document.getElementById('recipe-cook-time').value = recipe.cook_time_minutes || '';
            document.getElementById('recipe-servings').value = recipe.servings || '';
            document.getElementById('recipe-tags').value = recipe.tags.join(', ');
            
            // Check dietary restrictions
            recipe.dietary_restrictions.forEach(restriction => {
                const checkbox = document.querySelector(`input[name="dietary_restrictions"][value="${restriction}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
            
            this.addRecipeModal.classList.add('active');
        } catch (error) {
            console.error('Error loading recipe for editing:', error);
            alert(`Error loading recipe: ${error.message}`);
        }
    },
    
    /**
     * Save recipe (create or update).
     */
    async saveRecipe() {
        try {
            const formData = new FormData(this.recipeForm);
            
            // Get form values
            const title = formData.get('title');
            const mealTypes = formData.getAll('meal_types');
            const ingredientsText = formData.get('ingredients');
            const instructionsText = formData.get('instructions');
            const prepTimeMinutes = formData.get('prep_time_minutes') ? parseInt(formData.get('prep_time_minutes')) : null;
            const cookTimeMinutes = formData.get('cook_time_minutes') ? parseInt(formData.get('cook_time_minutes')) : null;
            const servings = formData.get('servings') ? parseInt(formData.get('servings')) : null;
            const tagsText = formData.get('tags');
            const dietaryRestrictions = formData.getAll('dietary_restrictions');
            const appliances = formData.getAll('appliances');
            
            // Use smart parser for ingredients and instructions
            const ingredients = smartRecipeParser.parseIngredients(ingredientsText);
            const instructions = smartRecipeParser.parseInstructions(instructionsText);
            
            // Validate parsed results
            if (ingredients.length === 0) {
                alert('Please enter at least one ingredient.');
                return;
            }
            
            if (instructions.length === 0) {
                alert('Please enter at least one instruction.');
                return;
            }
            
            // Parse tags
            const tags = tagsText.split(',')
                .map(tag => tag.trim())
                .filter(tag => tag.length > 0);
            
            // Create recipe object
            const recipe = {
                title,
                meal_types: mealTypes,
                ingredients,
                instructions,
                prep_time_minutes: prepTimeMinutes,
                cook_time_minutes: cookTimeMinutes,
                servings,
                tags,
                dietary_restrictions: dietaryRestrictions,
                appliances: appliances || []
            };
            
            // Add or update recipe
            if (this.recipeForm.dataset.mode === 'add') {
                await api.createRecipe(recipe);
                alert(`Recipe created successfully!\n\nParsed ${ingredients.length} ingredients and ${instructions.length} instructions.`);
            } else {
                // Get recipe ID from form
                const recipeId = this.recipeForm.dataset.recipeId;
                
                await api.updateRecipe(recipeId, recipe);
                alert(`Recipe updated successfully!\n\nParsed ${ingredients.length} ingredients and ${instructions.length} instructions.`);
            }
            
            // Close modal and reload recipes
            this.addRecipeModal.classList.remove('active');
            this.loadRecipes();
            
        } catch (error) {
            console.error('Error saving recipe:', error);
            
            // Show more detailed error information
            let errorMessage = 'Error saving recipe: ' + error.message;
            
            // Check if it's a parsing error
            if (error.message.includes('parse') || error.message.includes('format')) {
                errorMessage += '\n\nTip: Try using a simpler format like one ingredient per line.';
            }
            
            alert(errorMessage);
        }
    },
    
    /**
     * Delete a recipe.
     * 
     * @param {string} recipeId - Recipe ID
     */
    async deleteRecipe(recipeId) {
        if (!confirm('Are you sure you want to delete this recipe?')) {
            return;
        }
        
        try {
            await api.deleteRecipe(recipeId);
            alert('Recipe deleted successfully!');
            this.loadRecipes();
        } catch (error) {
            console.error('Error deleting recipe:', error);
            alert(`Error deleting recipe: ${error.message}`);
        }
    }
};
