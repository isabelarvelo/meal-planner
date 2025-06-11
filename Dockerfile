# Use Python 3.11 slim as the base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Create necessary directories
RUN mkdir -p data/uploads data/recipes

# Expose port
EXPOSE 8000

# Set up entrypoint
CMD ["uv", "run", "uvicorn", "meal_planner.api.main:app", "--host", "0.0.0.0", "--port", "8000"]