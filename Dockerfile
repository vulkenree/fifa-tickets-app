# Multi-stage build for production deployment
# Stage 1: Build stage with uv
FROM python:3.11-slim AS builder

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install production dependencies including PostgreSQL support
RUN uv pip install --system --no-cache \
    "flask>=3.1.2" \
    "flask-sqlalchemy>=3.1.1" \
    "werkzeug>=3.1.3" \
    "python-dotenv>=1.1.1" \
    "gunicorn>=21.2.0" \
    "psycopg2-binary>=2.9.9" \
    "flask-cors>=6.0.1"

# Stage 2: Production runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=8000

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Make startup script executable
RUN chmod +x start.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start the application
CMD ["./start.sh"]
