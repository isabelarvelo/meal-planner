#!/usr/bin/env python3
"""Setup script for development environment."""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Define colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_step(message):
    """Print a step message."""
    print(f"\n{BOLD}{GREEN}==> {message}{RESET}")


def print_warning(message):
    """Print a warning message."""
    print(f"{YELLOW}WARNING: {message}{RESET}")


def print_error(message):
    """Print an error message."""
    print(f"{RED}ERROR: {message}{RESET}")


def check_python_version():
    """Check Python version."""
    print_step("Checking Python version")
    
    required_version = (3, 9)
    current_version = sys.version_info
    
    if current_version < required_version:
        print_error(
            f"Python {required_version[0]}.{required_version[1]} or higher is required. "
            f"You have {current_version[0]}.{current_version[1]}.{current_version[2]}"
        )
        sys.exit(1)
    
    print(f"Python version: {current_version[0]}.{current_version[1]}.{current_version[2]}")


def create_directories():
    """Create necessary directories."""
    print_step("Creating necessary directories")
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # Create data directories
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    uploads_dir = data_dir / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    
    recipes_dir = data_dir / "recipes"
    recipes_dir.mkdir(exist_ok=True)
    
    print(f"Created directories: {data_dir}, {uploads_dir}, {recipes_dir}")


def create_env_file():
    """Create .env file if it doesn't exist."""
    print_step("Creating .env file")
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # Check if .env file exists
    env_file = project_root / ".env"
    
    if env_file.exists():
        print(f".env file already exists at {env_file}")
        return
    
    # Create .env file
    env_content = """# Environment variables for Meal Planner
MEAL_PLANNER_ENVIRONMENT=development
MEAL_PLANNER_DEBUG=true
MEAL_PLANNER_DATA_DIR=data
MEAL_PLANNER_API_PORT=8000
MEAL_PLANNER_LOG_LEVEL=INFO

# OCR settings
MEAL_PLANNER_OCR_PRIMARY_ENGINE=pymupdf
MEAL_PLANNER_OCR_FALLBACK_ENGINE=marker

# LLM settings
MEAL_PLANNER_LLM_PROVIDER=ollama
MEAL_PLANNER_LLM_MODEL=llama3
MEAL_PLANNER_LLM_API_BASE=http://localhost:11434/api

# CORS settings
MEAL_PLANNER_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"Created .env file at {env_file}")


def install_dependencies():
    """Install dependencies."""
    print_step("Installing dependencies")
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # Install dependencies
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=project_root,
            check=True
        )
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        sys.exit(1)


def setup_pre_commit():
    """Set up pre-commit hooks."""
    print_step("Setting up pre-commit hooks")
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # Check if pre-commit is installed
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pre-commit"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install pre-commit: {e}")
        return
    
    # Install pre-commit hooks
    try:
        subprocess.run(
            ["pre-commit", "install"],
            cwd=project_root,
            check=True
        )
        print("Pre-commit hooks installed successfully")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install pre-commit hooks: {e}")
        return
    
    # Run pre-commit hooks
    try:
        subprocess.run(
            ["pre-commit", "run", "--all-files"],
            cwd=project_root,
            check=True
        )
        print("Pre-commit hooks run successfully")
    except subprocess.CalledProcessError as e:
        print_warning(f"Pre-commit hooks failed: {e}")


def check_ollama():
    """Check if Ollama is installed."""
    print_step("Checking for Ollama")
    
    # Check if Ollama is installed
    ollama_path = shutil.which("ollama")
    
    if ollama_path:
        print(f"Ollama found at {ollama_path}")
        
        # Check if Ollama is running
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/version"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0 and "version" in result.stdout:
                print("Ollama is running")
            else:
                print_warning("Ollama is installed but not running")
                print("Start Ollama with: ollama serve")
        except Exception as e:
            print_warning(f"Failed to check if Ollama is running: {e}")
    else:
        print_warning("Ollama not found")
        print("Install Ollama from: https://ollama.ai/download")
        print("After installing, pull the required model: ollama pull llama3")


def main():
    """Main function."""
    print_step("Setting up development environment")
    
    check_python_version()
    create_directories()
    create_env_file()
    install_dependencies()
    setup_pre_commit()
    check_ollama()
    
    print_step("Setup complete!")
    print("\nYou can now start the API server with:")
    print("  uvicorn meal_planner.api.main:app --reload")
    print("\nThe API will be available at http://localhost:8000/api/docs")


if __name__ == "__main__":
    main()
