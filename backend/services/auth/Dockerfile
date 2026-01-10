# Backend Auth Service Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/services/auth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules (Must be built from root context)
COPY backend/shared /app/backend/shared

# Copy service code
COPY backend/services/auth /app/backend/services/auth

# Set python path to include app root
ENV PYTHONPATH=/app

# Run the service
CMD ["uvicorn", "backend.services.auth.main:app", "--host", "0.0.0.0", "--port", "8040"]
