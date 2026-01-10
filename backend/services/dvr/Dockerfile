FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libx264-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY backend/services/dvr/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/shared /app/backend/shared
COPY backend/services/dvr /app/backend/services/dvr

ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.services.dvr.main:app", "--host", "0.0.0.0", "--port", "8043"]
