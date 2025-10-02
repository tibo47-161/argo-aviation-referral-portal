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

# Copy application files - FIXED: Copy main.py instead of app_working.py
COPY main.py .

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

# Start command - FIXED: Start main.py
CMD ["python", "main.py"]
