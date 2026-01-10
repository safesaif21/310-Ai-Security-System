# Backend Analysis Service Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/services/analysis/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY backend/shared /app/backend/shared

# Copy service code
COPY backend/services/analysis /app/backend/services/analysis

# Copy models (Assuming they are in yolo_models at root)
COPY yolo_models /app/yolo_models

ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.services.analysis.main:app", "--host", "0.0.0.0", "--port", "8042"]
