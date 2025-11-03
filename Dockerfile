FROM python:3.11-slim

# Install system dependencies for CairoSVG
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libpango1.0-dev \
    shared-mime-info \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./

# Copy application code
COPY src/ ./src/

# Install Python dependencies using uv
RUN uv sync

# Create non-root user for security
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser

# Run the bot
CMD ["uv", "run", "-m", "apisbot"]
