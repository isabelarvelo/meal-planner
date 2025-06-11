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
# Show help
help:
	@echo "Available targets:"
	@echo ""
	@echo "Setup & Dependencies:"
	@echo "  setup              - Set up development environment with uv"
	@echo "  install            - Install dependencies (alias for setup)"
	@echo "  dev-setup          - Complete dev setup with test dependencies"
	@echo "  add                - Add a package (use: make add PACKAGE=package-name)"
	@echo "  add-dev            - Add a dev package (use: make add-dev PACKAGE=package-name)"
	@echo "  update             - Update all dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test               - Run all tests"
	@echo "  test-unit          - Run only unit tests (fast)"
	@echo "  test-integration   - Run only integration tests"
	@echo "  test-performance   - Run only performance tests"
	@echo "  test-cov           - Run tests with coverage report"
	@echo "  test-parallel      - Run tests in parallel"
	@echo "  test-watch         - Watch files and rerun tests on changes"
	@echo "  test-file          - Run specific test file (use: make test-file FILE=tests/test_api.py)"
	@echo "  test-report        - Generate HTML test report"
	@echo "  test-db            - Test database services"
	@echo "  test-api           - Test API endpoints"
	@echo "  test-parser        - Test recipe parser"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint               - Run linting"
	@echo "  format             - Format code"
	@echo "  dev-test           - Quick test + lint for development"
	@echo "  check              - Full check (format + lint + test + coverage)"
	@echo ""
	@echo "Running:"
	@echo "  run                - Run the API server"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build       - Build Docker image"
	@echo "  docker-run         - Run Docker container"
	@echo "  docker-compose-up  - Start Docker Compose services"
	@echo "  docker-compose-down - Stop Docker Compose services"
	@echo "  ollama-pull        - Pull Ollama models"
	@echo "  ollama-run         - Run Ollama model"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean              - Clean up build artifacts"
	@echo "  clean-test         - Clean up test artifacts"


# Testing targets
.PHONY: test-unit test-integration test-performance test-cov test-parallel test-watch clean-test test-report test-file

# Run only unit tests (fast)
test-unit:
	uv run pytest -m "not integration and not performance" -v

# Run only integration tests
test-integration:
	uv run pytest -m integration -v

# Run only performance tests
test-performance:
	uv run pytest -m performance -v

# Run tests with coverage report
test-cov:
	uv run pytest --cov=src/meal_planner --cov-report=html --cov-report=term-missing --cov-fail-under=80

# Run tests in parallel (requires pytest-xdist)
test-parallel:
	uv run pytest -n auto

# Watch for changes and rerun tests (requires pytest-watch)
test-watch:
	uv run ptw --runner "pytest --tb=short"

# Run specific test file (use: make test-file FILE=tests/test_api.py)
test-file:
	uv run pytest $(FILE) -v

# Generate HTML test report
test-report:
	uv run pytest --html=reports/report.html --self-contained-html --cov=src/meal_planner --cov-report=html

# Clean test artifacts
clean-test:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf test_data/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Database testing targets
.PHONY: test-db test-api test-parser

# Test database services specifically
test-db:
	uv run pytest tests/test_db_services.py -v

# Test API endpoints specifically
test-api:
	uv run pytest tests/test_api.py -v

# Test recipe parser specifically
test-parser:
	uv run pytest tests/test_recipe_parser.py -v

# Development workflow targets
.PHONY: dev-test dev-setup check

# Quick development test (unit tests + linting)
dev-test:
	uv run pytest -m "not integration and not performance" --tb=short
	uv run ruff check src tests

# Complete development setup
dev-setup: setup
	uv add --dev pytest pytest-asyncio pytest-cov httpx faker pytest-xdist pytest-html pytest-watch
	@echo "Development environment ready!"
	@echo "Run 'make test' to run all tests"
	@echo "Run 'make dev-test' for quick testing during development"

# Full check before committing (tests + linting + formatting)
check: format lint test-cov
	@echo "✅ All checks passed! Ready to commit."