# app/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
# Importiere spezifische Funktionen von Flask-Login für Benutzerauthentifizierung
from flask_login import login_user, logout_user, login_required, current_user
from app import db # Importiere die SQLAlchemy-Datenbankinstanz
from app.models import User, UserType # Importiere das User-Modell und die UserType Enum

auth_bp = Blueprint('auth', __name__) # Definiere einen Blueprint für Authentifizierungs-Routen

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
        user_type_str = request.form.get('user_type') # Erwartet 'referrer', 'applicant' oder 'admin'

        # Einfache serverseitige Validierung der Eingabedaten
        if not email or not password or not first_name or not last_name or not user_type_str:
            flash('Alle Pflichtfelder müssen ausgefüllt werden!', 'danger')
            return render_template('register.html')

        # Überprüfen, ob die E-Mail-Adresse bereits in der Datenbank existiert
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Diese E-Mail-Adresse ist bereits registriert.', 'warning')
            return render_template('register.html')

        try:
            # Konvertiere den String des Benutzertyps in das entsprechende Enum-Objekt
            # Hier erhalten wir direkt den String-Wert, da UserType von SQLEnum erbt
            user_type_value = UserType[user_type_str.upper()] # KORREKTUR: Umbenannt zu _value
        except KeyError:
            flash('Ungültiger Benutzertyp ausgewählt.', 'danger')
            return render_template('register.html')

        # Erstelle ein neues User-Objekt und setze die Eigenschaften
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            user_type=user_type_value # KORREKTUR: .value entfernt
        )
        new_user.set_password(password) # Hashe das Passwort sicher

        try:
            db.session.add(new_user) # Füge den neuen Benutzer zur Datenbank-Session hinzu
            db.session.commit() # Speichere die Änderungen in der Datenbank
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
