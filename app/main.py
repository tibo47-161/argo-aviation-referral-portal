# app/main.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user # Importiere Flask-Login Funktionen

main_bp = Blueprint('main', __name__) # Definiere einen Blueprint für die Hauptrouten

@main_bp.route('/') # Hauptseite der Anwendung
@main_bp.route('/dashboard') # Spezifische Route für das Dashboard
@login_required # Stellt sicher, dass nur angemeldete Benutzer auf diese Seiten zugreifen können
def dashboard():
    # Übergibt das aktuelle Benutzerobjekt (current_user von Flask-Login) an das Template
    # Das 'user'-Objekt kann dann im dashboard.html Template verwendet werden, z.B. {{ user.first_name }}
    return render_template('dashboard.html', user=current_user)

