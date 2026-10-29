# RevOps AI: Production Multi-Stage Container
FROM python:3.11-slim as base

# Security & environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY pyproject.toml /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlalchemy \
    pydantic \
    pyyaml \
    beautifulsoup4 \
    httpx

# Copy source code and assets
COPY RevOpsAI /app/RevOpsAI

# Expose FastAPI Control & Kanban port
EXPOSE 8000

# Run Uvicorn ASGI server
CMD ["uvicorn", "RevOpsAI.src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
