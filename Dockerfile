FROM gosom/google-maps-scraper:latest AS binary-source

FROM python:3.11-slim

WORKDIR /app

# Install system libraries needed to launch a headless browser
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfix6 \
    librandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install python and playwright automation tools
RUN pip install --no-cache-dir fastapi uvicorn playwright

# CRITICAL: Tell Playwright to download the required webkit/chromium engines
RUN playwright install chromium

# Bring in the scraper binary from the official image
COPY --from=binary-source /usr/bin/google-maps-scraper /app/google-maps-scraper
RUN chmod +x /app/google-maps-scraper

COPY app.py /app/app.py

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
