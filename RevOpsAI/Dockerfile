# RevOps AI: Production Container
FROM python:3.11-slim

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

# Install python dependencies directly for reliable multi-context builds
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    sqlalchemy \
    psycopg2-binary \
    "psycopg[binary]" \
    python-dotenv \
    pydantic \
    pyyaml \
    beautifulsoup4 \
    httpx

# Copy source code - supports either repository root context or RevOpsAI subfolder context
COPY . /tmp/src_build
RUN if [ -d "/tmp/src_build/RevOpsAI" ]; then \
        mv /tmp/src_build/RevOpsAI /app/RevOpsAI; \
    else \
        mkdir -p /app/RevOpsAI && cp -r /tmp/src_build/* /app/RevOpsAI/; \
    fi && rm -rf /tmp/src_build

# Expose default port
EXPOSE 8000

# Run Uvicorn ASGI server with dynamic PORT binding for Render / Cloud hosting
CMD ["sh", "-c", "uvicorn RevOpsAI.src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

