# Meal Planner

A web application that helps young professionals meal prep by organizing recipes, creating meal plans, and generating grocery lists.

## Features

- **Recipe Management**: Upload, store, and organize recipes from various sources
  - Extract recipes from images, screenshots, and handwritten notes using OCR
  - Manually enter recipes
  - Import recipes from social media (Instagram, TikTok)
- **Meal Planning**: Create weekly meal plans based on preferences and goals
  - Plan for breakfast, lunch, dinner, or any combination
  - Optimize for nutrition goals (hormone balance, gut health, muscle building)
  - Stay within budget constraints
- **Grocery Lists**: Generate shopping lists based on meal plans
  - Reduce food waste by buying only what you need
  - Optimize for budget

## Tech Stack

- **Backend**: Python with FastAPI
- **ML Components**:
  - OCR for recipe extraction from images
  - LLM for recipe structuring and meal plan generation
- **Deployment**: Docker and Docker Compose

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional, for containerized setup)
- Ollama (for local LLM support)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/meal-planner.git
   cd meal-planner
   ```

2. Set up the development environment:
   ```bash
   python scripts/setup_dev.py
   ```

   This script will:
   - Check Python version
   - Create necessary directories
   - Create a `.env` file if it doesn't exist
   - Install dependencies
   - Set up pre-commit hooks
   - Check for Ollama installation

3. Start the API server:
   ```bash
   uvicorn meal_planner.api.main:app --reload
   ```

   The API will be available at http://localhost:8000/api/docs

### Docker Setup

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Pull the required Ollama model:
   ```bash
   docker-compose exec ollama ollama pull llama3
   ```

3. Access the API at http://localhost:8000/api/docs

## Project Structure

```
meal-planner/
├── data/                  # Data storage
│   ├── recipes/           # Stored recipes
│   └── uploads/           # Uploaded files
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── src/                   # Source code
│   ├── meal_planner/      # Main application
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   └── utils/         # Utilities
│   └── ml/                # Machine learning components
│       ├── llm/           # LLM integration
│       └── ocr/           # OCR integration
└── tests/                 # Tests
    ├── integration/       # Integration tests
    └── unit/              # Unit tests
```

## Development

### Running Tests

```bash
pytest
```

### Linting and Formatting

```bash
# Lint code
make lint

# Format code
make format
```

### Available Make Commands

```bash
# Show all available commands
make help
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
