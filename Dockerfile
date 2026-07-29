# Step 1: Get the scraper binary
FROM gosom/google-maps-scraper:latest AS binary-source

# Step 2: Use the Python environment
FROM python:3.11-slim

WORKDIR /app

# Install basic tools needed to fetch browser drivers
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install FastAPI and Playwright python modules
RUN pip install --no-cache-dir fastapi uvicorn playwright

# FIX: Let Playwright automatically discover and install all correct system dependencies
RUN playwright install chromium
RUN playwright install-deps chromium

# Bring in the compiled scraper binary
COPY --from=binary-source /usr/bin/google-maps-scraper /app/google-maps-scraper
RUN chmod +x /app/google-maps-scraper

# Copy application script
COPY app.py /app/app.py

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
