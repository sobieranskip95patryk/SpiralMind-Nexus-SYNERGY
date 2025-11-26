FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY spiral/ spiral/
COPY config/ config/
COPY pyproject.toml .
COPY README.md .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash spiral
USER spiral

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
ENTRYPOINT ["python", "-m", "spiral"]
CMD ["--help"]