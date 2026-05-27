FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies needed for some wheels (psycopg2) and builds
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app

# Ensure data/logs dirs exist
RUN mkdir -p /app/data/raw /app/data/processed /app/logs

# Default working directory and command
ENV DATA_DIR=/app/data

CMD ["python", "src/pipeline.py"]
