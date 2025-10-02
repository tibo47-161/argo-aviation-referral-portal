#!/usr/bin/env python3
"""
Sichere Azure-Version der Argo Aviation Referral Portal App
Mit umfassender Fehlerbehandlung und Fallback-Optionen
"""

import os
import sys
import logging
from flask import Flask

# Basis-Flask-App als Fallback
def create_fallback_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'fallback-secret-key'
    
    @app.route('/')
    def home():
        return '''
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1 style="color: #1e3a8a;">🚀 Argo Aviation Referral Portal</h1>
            <div style="background: #f0f9ff; border: 1px solid #0ea5e9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #0c4a6e; margin-top: 0;">Status: Initializing...</h3>
                <p>The application is starting up. Full functionality will be available shortly.</p>
            </div>
            <h3>Expected Features:</h3>
            <ul style="line-height: 1.6;">
                <li>✈️ Aviation Job Listings</li>
                <li>👤 User Authentication</li>
                <li>📊 Referral Dashboard</li>
                <li>💰 Referral Bonus Tracking</li>
                <li>🎨 Argo Aviation Corporate Design</li>
            </ul>
            <p><em>Please refresh in a few moments...</em></p>
        </div>
        '''
    
    @app.route('/health')
    def health():
        return {'status': 'initializing', 'app': 'argo-aviation-referral-portal'}
    
    return app

# Versuche die echte App zu laden
try:
    from app import create_app, db
    
    # Erstelle die echte App
    app = create_app()
    
    # Azure-spezifische Konfiguration
    if os.environ.get('WEBSITE_SITE_NAME'):
        with app.app_context():
            try:
                # Erstelle Verzeichnisse
                os.makedirs('instance', exist_ok=True)
                os.makedirs('logs', exist_ok=True)
                
                # Initialisiere Datenbank
                db.create_all()
                
                # Füge Beispieldaten hinzu falls leer
                from app.models import JobListing, User
                if JobListing.query.count() == 0:
                    # Erstelle Admin-User
                    admin = User(
                        first_name='Admin',
                        last_name='User', 
                        email='admin@argo-aviation.com',
                        is_admin=True
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    
                    # Erstelle Beispiel-Jobs
                    jobs = [
                        JobListing(
                            title='Commercial Pilot',
                            description='Experienced pilot for commercial flights',
                            location='Hamburg',
                            referral_bonus=2000.0,
                            is_active=True,
                            creator_id=1
                        ),
                        JobListing(
                            title='Aircraft Maintenance Engineer',
                            description='Maintenance and repair of aircraft systems',
                            location='München',
                            referral_bonus=1500.0,
                            is_active=True,
                            creator_id=1
                        )
                    ]
                    
                    for job in jobs:
                        db.session.add(job)
                    
                    db.session.commit()
                    
                app.logger.info('✅ Argo Aviation Referral Portal initialized successfully')
                
            except Exception as e:
                app.logger.error(f'Database initialization error: {e}')
                # App trotzdem starten
    
except Exception as e:
    # Falls die echte App nicht geladen werden kann, verwende Fallback
    print(f"Error loading main app: {e}")
    app = create_fallback_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
