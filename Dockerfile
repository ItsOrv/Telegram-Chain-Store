FROM python:3.12-slim

LABEL maintainer="Telegram Chain Store <support@example.com>"

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p logs

# Set permissions
RUN chmod +x scripts/*.py

# Create startup script
RUN echo '#!/bin/bash\nset -e\npython -m alembic upgrade head\npython -m src.main' > /app/start.sh && \
    chmod +x /app/start.sh

# Run startup script
CMD ["/app/start.sh"]