#!/bin/bash

# Azure App Service Startup Script für Argo Aviation Referral Portal
echo "=== Starting Argo Aviation Referral Portal ==="

# Setze Environment-Variablen für Azure
export FLASK_APP=run.py
export FLASK_ENV=production
export DATABASE_URL=sqlite:///instance/app.db
export SECRET_KEY=your-secret-key-here-change-in-production

# Erstelle notwendige Verzeichnisse
mkdir -p logs
mkdir -p instance

# Initialisiere Datenbank falls nicht vorhanden
echo "Checking database..."
if [ ! -f "instance/app.db" ]; then
    echo "Initializing database..."
    python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
else
    echo "Database already exists"
fi

# Starte die Anwendung
echo "Starting Flask application with Gunicorn..."
exec gunicorn --bind=0.0.0.0:8000 --workers=2 --timeout=120 --preload --access-logfile=logs/access.log --error-logfile=logs/error.log run:app
