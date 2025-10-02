#!/bin/bash

# Azure App Service Startup Script für Argo Aviation Referral Portal
# Erstellt: 02.10.2025

echo "Starting Argo Aviation Referral Portal..."

# Erstelle notwendige Verzeichnisse
mkdir -p logs
mkdir -p instance

# Setze Environment-Variablen
export FLASK_APP=run.py
export FLASK_ENV=production

# Initialisiere Datenbank (falls noch nicht vorhanden)
if [ ! -f "instance/app.db" ]; then
    echo "Initializing database..."
    flask db upgrade
fi

# Starte die Anwendung mit Gunicorn
echo "Starting application with Gunicorn..."
exec gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 --access-logfile=logs/access.log --error-logfile=logs/error.log run:app
