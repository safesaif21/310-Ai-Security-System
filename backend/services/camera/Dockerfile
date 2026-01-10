# Backend Camera Service Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/services/camera/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/shared /app/backend/shared
COPY backend/services/camera /app/backend/services/camera

ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.services.camera.main:app", "--host", "0.0.0.0", "--port", "8041"]
