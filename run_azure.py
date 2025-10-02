#!/usr/bin/env python3
"""
Azure-optimierte Version der Flask-App
Argo Aviation Referral Portal
"""

import os
import logging
from app import create_app, db

# Konfiguration für Azure App Service
app = create_app()

# Logging für Azure
if not app.debug:
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Argo Aviation Referral Portal startup')

# Datenbank-Initialisierung für Azure
with app.app_context():
    try:
        # Erstelle Tabellen falls sie nicht existieren
        db.create_all()
        app.logger.info('Database tables created/verified')
    except Exception as e:
        app.logger.error(f'Database initialization error: {e}')

if __name__ == '__main__':
    # Für lokale Entwicklung
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=False)
else:
    # Für Azure App Service mit Gunicorn
    application = app
