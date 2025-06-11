# Meal Planner Frontend

A simple web interface for the Meal Planner application.

## Overview

This frontend provides a user-friendly interface for managing recipes and meal plans. It communicates with the Meal Planner API to perform operations such as:

- Viewing, creating, editing, and deleting recipes
- Searching for recipes
- Analyzing nutrition information for recipes
- Creating meal plans
- Viewing meal plans and associated grocery lists

## Structure

- `index.html`: Main HTML file
- `css/styles.css`: Stylesheet
- `js/api.js`: API client for communicating with the backend
- `js/recipes.js`: Recipe-related functionality
- `js/meal-plans.js`: Meal plan-related functionality
- `js/app.js`: Main application entry point

## Setup

1. Make sure the backend API is running (default: http://localhost:8000/api)
2. Open `index.html` in a web browser

## Usage

### Recipes

- View all recipes on the Recipes page
- Search for recipes using the search bar
- Click "Add Recipe" to create a new recipe
- Click "View Recipe" on a recipe card to see details
- Click the edit icon to modify a recipe
- Click the delete icon to remove a recipe
- Click "Analyze Nutrition" on a recipe detail page to get nutrition information

### Meal Plans

- View all meal plans on the Meal Plans page
- Click "Create Meal Plan" to generate a new meal plan
- Select date range, meal types, nutrition goals, and budget constraints
- Click "View Full Plan" on a meal plan card to see details
- View the grocery list associated with a meal plan

## Development

To modify the frontend:

1. Edit the HTML, CSS, or JavaScript files as needed
2. Refresh the browser to see changes

## API Integration

The frontend communicates with the Meal Planner API using the fetch API. The base URL is configured in `js/api.js` and defaults to `http://localhost:8000/api`.

## MCP Integration

This frontend works with the Model Context Protocol (MCP) server for enhanced functionality:

- Recipe search using natural language queries
- Nutrition analysis for recipes
- Intelligent meal plan generation based on preferences

## Browser Compatibility

The frontend is compatible with modern browsers that support ES6+ features:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
