FROM python:3.11-slim

# Run as non-root for security
RUN useradd --create-home --shell /bin/bash botuser

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir "python-telegram-bot==20.7"

# Copy only application source — never .env or *.db
COPY *.py ./
COPY pro_players.py ./

# Writable dirs for DB and logs
RUN mkdir -p /app/logs /app/data \
    && chown -R botuser:botuser /app

USER botuser

# DB_PATH should point to /app/data/lolnotifier.db via env
ENV DB_PATH=/app/data/lolnotifier.db

CMD ["python", "main.py"]

