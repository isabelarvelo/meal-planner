/**
 * Meal plan-related functionality.
 */

/**
 * Meal plan manager.
 */
const mealPlanManager = {
    /**
     * Initialize meal plan functionality.
     */
    init() {
        this.mealPlansContainer = document.getElementById('meal-plans-container');
        this.mealPlanModal = document.getElementById('meal-plan-modal');
        this.mealPlanForm = document.getElementById('meal-plan-form');
        this.mealPlanDetailModal = document.getElementById('meal-plan-detail-modal');
        this.mealPlanDetailContent = document.getElementById('meal-plan-detail-content');
        this.createMealPlanButton = document.getElementById('create-meal-plan-button');
        
        // Attach event listeners
        this.createMealPlanButton.addEventListener('click', () => this.showCreateMealPlanModal());
        
        this.mealPlanForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateMealPlan();
        });
        
        // Close buttons for modals
        document.querySelectorAll('.close-button, .cancel-button').forEach(button => {
            button.addEventListener('click', () => {
                this.mealPlanModal.classList.remove('active');
                this.mealPlanDetailModal.classList.remove('active');
            });
        });
        
        // Set default dates for meal plan form
        this.setDefaultDates();
        
        // Load meal plans
        this.loadMealPlans();
    },
    
    /**
     * Set default dates for meal plan form.
     */
    setDefaultDates() {
        const today = new Date();
        const startDate = today.toISOString().split('T')[0];
        
        // End date is 7 days from today
        const endDate = new Date(today);
        endDate.setDate(today.getDate() + 6);
        const endDateStr = endDate.toISOString().split('T')[0];
        
        document.getElementById('meal-plan-start-date').value = startDate;
        document.getElementById('meal-plan-end-date').value = endDateStr;
    },
    
    /**
     * Load meal plans from the API.
     */
    async loadMealPlans() {
        try {
            this.mealPlansContainer.innerHTML = '<div class="loading">Loading meal plans...</div>';
            
            const mealPlans = await api.getMealPlans(DEFAULT_USER_ID);
            
            if (mealPlans.length === 0) {
                this.mealPlansContainer.innerHTML = '<div class="loading">No meal plans found. Create your first meal plan!</div>';
                return;
            }
            
            this.renderMealPlans(mealPlans);
        } catch (error) {
            console.error('Error loading meal plans:', error);
            this.mealPlansContainer.innerHTML = `<div class="loading">Error loading meal plans: ${error.message}</div>`;
        }
    },
    
    /**
     * Render meal plans in the container.
     * 
     * @param {Array} mealPlans - Array of meal plan objects
     */
    renderMealPlans(mealPlans) {
        this.mealPlansContainer.innerHTML = '';
        
        mealPlans.forEach(mealPlan => {
            const card = document.createElement('div');
            card.className = 'card meal-plan-card';
            card.dataset.id = mealPlan.id;
            
            // Format dates
            const startDate = new Date(mealPlan.start_date).toLocaleDateString();
            const endDate = new Date(mealPlan.end_date).toLocaleDateString();
            
            // Get first 3 days for preview
            const previewDays = mealPlan.days.slice(0, 3);
            
            // Create days preview HTML
            const daysPreviewHtml = previewDays.map(day => {
                const date = new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
                
                // Get one meal for preview
                let previewMeal = '';
                if (day.dinner) {
                    previewMeal = `<div class="meal-plan-meal">
                        <span class="meal-plan-meal-type">Dinner:</span>
                        <span>${day.dinner}</span>
                    </div>`;
                } else if (day.lunch) {
                    previewMeal = `<div class="meal-plan-meal">
                        <span class="meal-plan-meal-type">Lunch:</span>
                        <span>${day.lunch}</span>
                    </div>`;
                } else if (day.breakfast) {
                    previewMeal = `<div class="meal-plan-meal">
                        <span class="meal-plan-meal-type">Breakfast:</span>
                        <span>${day.breakfast}</span>
                    </div>`;
                }
                
                return `
                    <div class="meal-plan-day">
                        <div class="meal-plan-day-header">${date}</div>
                        <div class="meal-plan-meals">
                            ${previewMeal}
                        </div>
                    </div>
                `;
            }).join('');
            
            // Format nutrition goal
            const nutritionGoal = mealPlan.nutrition_goal
                ? mealPlan.nutrition_goal.replace('_', ' ')
                : 'None';
            
            // Format cost
            const cost = mealPlan.total_estimated_cost
                ? `$${mealPlan.total_estimated_cost.toFixed(2)}`
                : 'N/A';
            
            card.innerHTML = `
                <div class="card-content">
                    <h3 class="card-title">Meal Plan (${startDate} - ${endDate})</h3>
                    <div class="card-meta">
                        <span><i class="fas fa-utensils"></i> ${mealPlan.days.length} days</span>
                        <span><i class="fas fa-leaf"></i> ${nutritionGoal}</span>
                        <span><i class="fas fa-dollar-sign"></i> ${cost}</span>
                    </div>
                    <div class="meal-plan-days">
                        ${daysPreviewHtml}
                    </div>
                    <div class="card-actions">
                        <button class="icon-button delete-meal-plan-button" title="Delete Meal Plan">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button class="primary-button view-meal-plan-button">View Full Plan</button>
                    </div>
                </div>
            `;
            
            // Attach event listeners
            card.querySelector('.view-meal-plan-button').addEventListener('click', () => {
                this.showMealPlanDetail(mealPlan.id);
            });
            
            card.querySelector('.delete-meal-plan-button').addEventListener('click', () => {
                this.deleteMealPlan(mealPlan.id);
            });
            
            this.mealPlansContainer.appendChild(card);
        });
    },
    
    /**
     * Show create meal plan modal.
     */
    showCreateMealPlanModal() {
        this.mealPlanForm.reset();
        this.setDefaultDates();
        this.mealPlanModal.classList.add('active');
    },
    
    /**
     * Generate a meal plan.
     */
    async generateMealPlan() {
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
            
            // Generate meal plan
            const response = await api.generateMealPlan(mealPlanRequest);
            
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
    },
    
    /**
     * Show meal plan detail modal.
     * 
     * @param {string} mealPlanId - Meal plan ID
     */
    async showMealPlanDetail(mealPlanId) {
        try {
            this.mealPlanDetailContent.innerHTML = '<div class="loading">Loading meal plan...</div>';
            this.mealPlanDetailModal.classList.add('active');
            
            // Get meal plan and grocery list
            const [mealPlan, groceryList] = await Promise.all([
                api.getMealPlan(mealPlanId),
                api.getMealPlanGroceryList(mealPlanId)
            ]);
            
            // Format dates
            const startDate = new Date(mealPlan.start_date).toLocaleDateString();
            const endDate = new Date(mealPlan.end_date).toLocaleDateString();
            
            // Format nutrition goal
            const nutritionGoal = mealPlan.nutrition_goal
                ? mealPlan.nutrition_goal.replace('_', ' ')
                : 'None';
            
            // Format cost
            const cost = mealPlan.total_estimated_cost
                ? `$${mealPlan.total_estimated_cost.toFixed(2)}`
                : 'N/A';
            
            // Create days HTML
            const daysHtml = mealPlan.days.map(day => {
                const date = new Date(day.date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
                
                // Create meals HTML
                let mealsHtml = '';
                
                if (day.breakfast) {
                    mealsHtml += `
                        <div class="meal-plan-detail-meal">
                            <div class="meal-plan-detail-meal-type">Breakfast:</div>
                            <div class="meal-plan-detail-meal-recipe">${day.breakfast}</div>
                        </div>
                    `;
                }
                
                if (day.lunch) {
                    mealsHtml += `
                        <div class="meal-plan-detail-meal">
                            <div class="meal-plan-detail-meal-type">Lunch:</div>
                            <div class="meal-plan-detail-meal-recipe">${day.lunch}</div>
                        </div>
                    `;
                }
                
                if (day.dinner) {
                    mealsHtml += `
                        <div class="meal-plan-detail-meal">
                            <div class="meal-plan-detail-meal-type">Dinner:</div>
                            <div class="meal-plan-detail-meal-recipe">${day.dinner}</div>
                        </div>
                    `;
                }
                
                if (day.snacks && day.snacks.length > 0) {
                    const snacksHtml = day.snacks.map(snack => {
                        return `
                            <div class="meal-plan-detail-meal">
                                <div class="meal-plan-detail-meal-type">Snack:</div>
                                <div class="meal-plan-detail-meal-recipe">${snack}</div>
                            </div>
                        `;
                    }).join('');
                    
                    mealsHtml += snacksHtml;
                }
                
                return `
                    <div class="meal-plan-detail-day">
                        <div class="meal-plan-detail-day-header">${date}</div>
                        <div class="meal-plan-detail-meals">
                            ${mealsHtml}
                        </div>
                    </div>
                `;
            }).join('');
            
            // Create grocery list HTML
            let groceryListHtml = '';
            if (groceryList && groceryList.items) {
                groceryListHtml = groceryList.items.map(item => {
                    const quantity = item.quantity ? `<span class="grocery-list-item-quantity">${item.quantity}</span>` : '';
                    return `<li>${quantity}<span class="grocery-list-item-name">${item.name}</span></li>`;
                }).join('');
            }
            
            this.mealPlanDetailContent.innerHTML = `
                <div class="meal-plan-detail">
                    <div class="meal-plan-detail-header">
                        <h2 class="meal-plan-detail-title">Meal Plan (${startDate} - ${endDate})</h2>
                        <div class="meal-plan-detail-meta">
                            <span><i class="fas fa-utensils"></i> ${mealPlan.days.length} days</span>
                            <span><i class="fas fa-leaf"></i> Nutrition Goal: ${nutritionGoal}</span>
                            <span><i class="fas fa-dollar-sign"></i> Estimated Cost: ${cost}</span>
                        </div>
                    </div>
                    
                    <div class="meal-plan-detail-section">
                        <h3>Daily Meals</h3>
                        <div class="meal-plan-detail-days">
                            ${daysHtml}
                        </div>
                    </div>
                    
                    <div class="meal-plan-detail-section">
                        <h3>Grocery List</h3>
                        <ul class="grocery-list">
                            ${groceryListHtml}
                        </ul>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error showing meal plan detail:', error);
            this.mealPlanDetailContent.innerHTML = `<div class="loading">Error loading meal plan: ${error.message}</div>`;
        }
    },
    
    /**
     * Delete a meal plan.
     * 
     * @param {string} mealPlanId - Meal plan ID
     */
    async deleteMealPlan(mealPlanId) {
        if (!confirm('Are you sure you want to delete this meal plan?')) {
            return;
        }
        
        try {
            await api.deleteMealPlan(mealPlanId);
            alert('Meal plan deleted successfully!');
            this.loadMealPlans();
        } catch (error) {
            console.error('Error deleting meal plan:', error);
            alert(`Error deleting meal plan: ${error.message}`);
        }
    }
};
