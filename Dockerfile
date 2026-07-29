# Step 1: Pull from the correct official image
FROM gosom/google-maps-scraper:latest AS binary-source

# Step 2: Build a lightweight python layer
FROM python:3.11-slim

WORKDIR /app

# FIX: Copy from the exact location where gosom compiles the binary
COPY --from=binary-source /usr/bin/google-maps-scraper /app/google-maps-scraper
RUN chmod +x /app/google-maps-scraper

# Install API layer dependencies
RUN pip install --no-cache-dir fastapi uvicorn

COPY app.py /app/app.py

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
