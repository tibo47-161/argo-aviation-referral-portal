# Argo Aviation Referral Portal - Docker Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=8000

# Copy requirements first for better caching
COPY requirements_azure.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app_working.py .

# Create necessary directories
RUN mkdir -p instance logs uploads

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Health check using Python instead of curl
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "app_working.py"]
