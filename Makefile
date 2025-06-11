.PHONY: setup install test lint format clean run docker-build docker-run docker-compose-up docker-compose-down

# Default target
all: setup

# Setup development environment
setup:
	uv sync --extra dev

# Install dependencies (same as setup with uv)
install:
	uv sync --extra dev

# Run tests
test:
	uv run pytest

# Run linting
lint:
	uv run ruff check src tests
	uv run mypy src tests

# Format code
format:
	uv run black src tests
	uv run isort src tests

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Run the API server
run:
	uv run uvicorn meal_planner.api.main:app --reload --host 0.0.0.0 --port 8000

# Build Docker image
docker-build:
	docker build -t meal-planner:latest .

# Run Docker container
docker-run:
	docker run -p 8000:8000 -v $(PWD)/data:/app/data meal-planner:latest

# Start Docker Compose services
docker-compose-up:
	docker-compose up -d

# Stop Docker Compose services
docker-compose-down:
	docker-compose down

# Pull Ollama models
ollama-pull:
	docker-compose exec ollama ollama pull llama3

# Run Ollama model
ollama-run:
	docker-compose exec ollama ollama run llama3

# Add dependencies
add:
	uv add $(PACKAGE)

# Add dev dependencies
add-dev:
	uv add --dev $(PACKAGE)

# Update dependencies
update:
	uv sync --upgrade

# Show help
help:
	@echo "Available targets:"
	@echo "  setup              - Set up development environment with uv"
	@echo "  install            - Install dependencies (alias for setup)"
	@echo "  test               - Run tests"
	@echo "  lint               - Run linting"
	@echo "  format             - Format code"
	@echo "  clean              - Clean up build artifacts"
	@echo "  run                - Run the API server"
	@echo "  docker-build       - Build Docker image"
	@echo "  docker-run         - Run Docker container"
	@echo "  docker-compose-up  - Start Docker Compose services"
	@echo "  docker-compose-down - Stop Docker Compose services"
	@echo "  ollama-pull        - Pull Ollama models"
	@echo "  ollama-run         - Run Ollama model"
	@echo "  add                - Add a package (use: make add PACKAGE=package-name)"
	@echo "  add-dev            - Add a dev package (use: make add-dev PACKAGE=package-name)"
	@echo "  update             - Update all dependencies"