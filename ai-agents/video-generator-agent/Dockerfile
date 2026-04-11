FROM python:3.11-slim

# Install system dependencies required by MoviePy
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    imagemagick \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy to allow MoviePy to use it
RUN sed -i 's/rights="none" pattern="@\*"/rights="read|write" pattern="@*"/' \
    /etc/ImageMagick-6/policy.xml 2>/dev/null || true

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create output directory for generated videos
RUN mkdir -p /app/output

EXPOSE 8004

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8004"]
