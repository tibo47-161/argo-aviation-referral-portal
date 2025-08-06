# app/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
# Importiere spezifische Funktionen von Flask-Login für Benutzerauthentifizierung
from flask_login import login_user, logout_user, login_required, current_user
from app import db # Importiere die SQLAlchemy-Datenbankinstanz
from app.models import User # Importiere das User-Modell

auth_bp = Blueprint('auth', __name__) # Definiere einen Blueprint für Authentifizierungs-Routen

# Superadmin-Konfiguration
SUPERADMIN_EMAIL = "tobi196183@gmail.com"

def is_superadmin(email):
    """Überprüft, ob die E-Mail-Adresse ein Superadmin ist"""
    return email.lower() == SUPERADMIN_EMAIL.lower()

def setup_superadmin_if_needed(user):
    """Setzt Superadmin-Eigenschaften für die spezielle E-Mail-Adresse"""
    if is_superadmin(user.email):
        # Hier können Sie zusätzliche Superadmin-Eigenschaften setzen
        # Zum Beispiel: user.is_admin = True, user.permissions = 'all', etc.
        flash(f'Willkommen zurück, Superadmin {user.first_name}!', 'success')
        return True
    return False

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Wenn der Benutzer bereits angemeldet ist, leite ihn zum Dashboard um
    if current_user.is_authenticated:
        flash('Sie sind bereits angemeldet.', 'info')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')

        # Einfache serverseitige Validierung der Eingabedaten
        if not email or not password or not first_name or not last_name:
            flash('Alle Pflichtfelder müssen ausgefüllt werden!', 'danger')
            return render_template('register.html')

        # Passwort-Validierung
        if len(password) < 6:
            flash('Das Passwort muss mindestens 6 Zeichen lang sein.', 'danger')
            return render_template('register.html')

        # Überprüfen, ob die E-Mail-Adresse bereits in der Datenbank existiert
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Diese E-Mail-Adresse ist bereits registriert.', 'warning')
            return render_template('register.html')

        # Erstelle ein neues User-Objekt und setze die Eigenschaften
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        new_user.set_password(password) # Hashe das Passwort sicher

        # Superadmin-Check
        if is_superadmin(email):
            flash(f'Superadmin-Account für {email} wird erstellt!', 'success')

        try:
            db.session.add(new_user) # Füge den neuen Benutzer zur Datenbank-Session hinzu
            db.session.commit() # Speichere die Änderungen in der Datenbank
            
            if is_superadmin(email):
                flash('Superadmin-Registrierung erfolgreich! Sie haben erweiterte Berechtigungen.', 'success')
            else:
                flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.', 'success')
            
            return redirect(url_for('auth.login')) # Leite zur Login-Seite um
        except Exception as e:
            db.session.rollback() # Mache Änderungen rückgängig, falls ein Fehler auftritt
            flash(f'Ein Fehler ist bei der Registrierung aufgetreten: {e}', 'danger')
            # Es ist ratsam, den Fehler hier auch zu loggen (z.B. mit app.logger.error(e))
            return render_template('register.html')

    return render_template('register.html') # Zeige das Registrierungsformular für GET-Anfragen

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Wenn der Benutzer bereits angemeldet ist, leite ihn zum Dashboard um
    if current_user.is_authenticated:
        flash('Sie sind bereits angemeldet.', 'info')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first() # Suche den Benutzer nach E-Mail

        # Überprüfe, ob der Benutzer existiert und das Passwort korrekt ist
        if user and user.check_password(password):
            login_user(user) # Meldet den Benutzer über Flask-Login an und verwaltet die Session
            
            # Superadmin-Check beim Login
            if setup_superadmin_if_needed(user):
                # Zusätzliche Superadmin-Logik hier
                pass
            else:
                flash('Erfolgreich angemeldet!', 'success')
            
            # Leite den Benutzer zur 'next' Seite (falls vorhanden) oder zum Standard-Dashboard um
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Ungültige E-Mail oder Passwort.', 'danger') # Fehlermeldung bei fehlgeschlagenem Login

    return render_template('login.html') # Zeige das Login-Formular für GET-Anfragen

@auth_bp.route('/logout')
@login_required # Stellt sicher, dass nur angemeldete Benutzer diese Route aufrufen können
def logout():
    logout_user() # Meldet den aktuellen Benutzer von der Session ab
    flash('Sie wurden abgemeldet.', 'info')
    return redirect(url_for('auth.login')) # Leite zur Login-Seite um nach dem Abmelden

# Hilfsfunktion für Templates
@auth_bp.app_template_global()
def is_current_user_superadmin():
    """Template-Funktion um zu prüfen, ob der aktuelle Benutzer ein Superadmin ist"""
    if current_user.is_authenticated:
        return is_superadmin(current_user.email)
    return False
