#!/usr/bin/env python3
"""
Einfache Azure-kompatible Version der Flask-App
Argo Aviation Referral Portal
"""

import os
import sys
from flask import Flask

# Einfache Flask-App für Azure
app = Flask(__name__)

# Basis-Konfiguration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def hello():
    return '''
    <h1>🚀 Argo Aviation Referral Portal</h1>
    <p>Azure App Service Test - App is running!</p>
    <p>Status: <strong style="color: green;">ONLINE</strong></p>
    <hr>
    <p>Deployment successful. Full app initialization in progress...</p>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'app': 'argo-aviation-referral-portal'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
