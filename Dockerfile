# Step 1: Pull from the high-speed backend image
FROM gosom/google-maps-scraper:latest AS binary-source

# Step 2: Build a ultra-lightweight python layer
FROM python:3.11-slim

WORKDIR /app

# Pull only the compiled high-speed scraper binary
COPY --from=binary-source /app/google-maps-scraper /app/google-maps-scraper
RUN chmod +x /app/google-maps-scraper

# Install API layer
RUN pip install --no-cache-dir fastapi uvicorn

COPY app.py /app/app.py

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
