from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from app.models import User
import re

class RegistrationForm(FlaskForm):
    first_name = StringField('Vorname', validators=[
        DataRequired(message='Vorname ist erforderlich'),
        Length(min=2, max=50, message='Vorname muss zwischen 2 und 50 Zeichen lang sein'),
        Regexp(r'^[A-Za-zÄÖÜäöüß\s-]+$', message='Vorname darf nur Buchstaben, Leerzeichen und Bindestriche enthalten')
    ])
    
    last_name = StringField('Nachname', validators=[
        DataRequired(message='Nachname ist erforderlich'),
        Length(min=2, max=50, message='Nachname muss zwischen 2 und 50 Zeichen lang sein'),
        Regexp(r'^[A-Za-zÄÖÜäöüß\s-]+$', message='Nachname darf nur Buchstaben, Leerzeichen und Bindestriche enthalten')
    ])
    
    email = StringField('E-Mail-Adresse', validators=[
        DataRequired(message='E-Mail-Adresse ist erforderlich'),
        Email(message='Gültige E-Mail-Adresse erforderlich'),
        Length(max=120, message='E-Mail-Adresse zu lang')
    ])
    
    password = PasswordField('Passwort', validators=[
        DataRequired(message='Passwort ist erforderlich'),
        Length(min=8, message='Passwort muss mindestens 8 Zeichen lang sein'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', 
               message='Passwort muss mindestens einen Kleinbuchstaben, einen Großbuchstaben und eine Zahl enthalten')
    ])
    
    password2 = PasswordField('Passwort wiederholen', validators=[
        DataRequired(message='Passwort-Wiederholung ist erforderlich'),
        EqualTo('password', message='Passwörter müssen übereinstimmen')
    ])
    
    phone_number = StringField('Telefonnummer (optional)', validators=[
        Length(max=20, message='Telefonnummer zu lang'),
        Regexp(r'^[\+]?[0-9\s\-\(\)]{0,20}$', message='Ungültiges Telefonnummer-Format')
    ])
    
    terms_accepted = BooleanField('Ich akzeptiere die Nutzungsbedingungen', validators=[
        DataRequired(message='Sie müssen die Nutzungsbedingungen akzeptieren')
    ])
    
    submit = SubmitField('Registrieren')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Diese E-Mail-Adresse ist bereits registriert.')

class LoginForm(FlaskForm):
    email = StringField('E-Mail-Adresse', validators=[
        DataRequired(message='E-Mail-Adresse ist erforderlich'),
        Email(message='Gültige E-Mail-Adresse erforderlich')
    ])
    
    password = PasswordField('Passwort', validators=[
        DataRequired(message='Passwort ist erforderlich')
    ])
    
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')

class ReferralForm(FlaskForm):
    applicant_name = StringField('Name des Bewerbers', validators=[
        DataRequired(message='Name des Bewerbers ist erforderlich'),
        Length(min=2, max=100, message='Name muss zwischen 2 und 100 Zeichen lang sein'),
        Regexp(r'^[A-Za-zÄÖÜäöüß\s\.-]+$', message='Name darf nur Buchstaben, Leerzeichen, Punkte und Bindestriche enthalten')
    ])
    
    applicant_email = StringField('E-Mail des Bewerbers', validators=[
        DataRequired(message='E-Mail-Adresse des Bewerbers ist erforderlich'),
        Email(message='Gültige E-Mail-Adresse erforderlich'),
        Length(max=120, message='E-Mail-Adresse zu lang')
    ])
    
    applicant_phone = StringField('Telefonnummer des Bewerbers', validators=[
        Length(max=20, message='Telefonnummer zu lang'),
        Regexp(r'^[\+]?[0-9\s\-\(\)]{0,20}$', message='Ungültiges Telefonnummer-Format')
    ])
    
    applicant_linkedin = StringField('LinkedIn-Profil (optional)', validators=[
        Length(max=200, message='LinkedIn-URL zu lang'),
        Regexp(r'^(https?://)?(www\.)?linkedin\.com/.*$|^$', message='Ungültige LinkedIn-URL')
    ])
    
    resume = FileField('Lebenslauf', validators=[
        FileRequired(message='Lebenslauf ist erforderlich'),
        FileAllowed(['pdf', 'doc', 'docx'], message='Nur PDF, DOC oder DOCX-Dateien sind erlaubt')
    ])
    
    cover_letter = TextAreaField('Anschreiben (optional)', validators=[
        Length(max=2000, message='Anschreiben zu lang (maximal 2000 Zeichen)')
    ])
    
    notes = TextAreaField('Zusätzliche Notizen', validators=[
        Length(max=1000, message='Notizen zu lang (maximal 1000 Zeichen)')
    ])
    
    submit = SubmitField('Referral einreichen')

class JobSearchForm(FlaskForm):
    search = StringField('Stellentitel', validators=[
        Length(max=100, message='Suchbegriff zu lang')
    ])
    
    location = StringField('Standort', validators=[
        Length(max=100, message='Standort zu lang')
    ])
    
    department = SelectField('Abteilung', choices=[
        ('', 'Alle Abteilungen'),
        ('Flight Operations', 'Flight Operations'),
        ('Maintenance', 'Maintenance'),
        ('Operations', 'Operations'),
        ('Cabin Services', 'Cabin Services'),
        ('Safety & Quality', 'Safety & Quality'),
        ('Administration', 'Administration'),
        ('IT', 'IT')
    ])
    
    employment_type = SelectField('Beschäftigungsart', choices=[
        ('', 'Alle Arten'),
        ('Vollzeit', 'Vollzeit'),
        ('Teilzeit', 'Teilzeit'),
        ('Befristet', 'Befristet'),
        ('Praktikum', 'Praktikum')
    ])
    
    submit = SubmitField('Suchen')

class ProfileForm(FlaskForm):
    first_name = StringField('Vorname', validators=[
        DataRequired(message='Vorname ist erforderlich'),
        Length(min=2, max=50, message='Vorname muss zwischen 2 und 50 Zeichen lang sein'),
        Regexp(r'^[A-Za-zÄÖÜäöüß\s-]+$', message='Vorname darf nur Buchstaben, Leerzeichen und Bindestriche enthalten')
    ])
    
    last_name = StringField('Nachname', validators=[
        DataRequired(message='Nachname ist erforderlich'),
        Length(min=2, max=50, message='Nachname muss zwischen 2 und 50 Zeichen lang sein'),
        Regexp(r'^[A-Za-zÄÖÜäöüß\s-]+$', message='Nachname darf nur Buchstaben, Leerzeichen und Bindestriche enthalten')
    ])
    
    phone_number = StringField('Telefonnummer', validators=[
        Length(max=20, message='Telefonnummer zu lang'),
        Regexp(r'^[\+]?[0-9\s\-\(\)]{0,20}$', message='Ungültiges Telefonnummer-Format')
    ])
    
    submit = SubmitField('Profil aktualisieren')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Aktuelles Passwort', validators=[
        DataRequired(message='Aktuelles Passwort ist erforderlich')
    ])
    
    new_password = PasswordField('Neues Passwort', validators=[
        DataRequired(message='Neues Passwort ist erforderlich'),
        Length(min=8, message='Passwort muss mindestens 8 Zeichen lang sein'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', 
               message='Passwort muss mindestens einen Kleinbuchstaben, einen Großbuchstaben und eine Zahl enthalten')
    ])
    
    new_password2 = PasswordField('Neues Passwort wiederholen', validators=[
        DataRequired(message='Passwort-Wiederholung ist erforderlich'),
        EqualTo('new_password', message='Passwörter müssen übereinstimmen')
    ])
    
    submit = SubmitField('Passwort ändern')

# Admin Forms
class JobListingForm(FlaskForm):
    title = StringField('Stellentitel', validators=[
        DataRequired(message='Stellentitel ist erforderlich'),
        Length(min=5, max=200, message='Stellentitel muss zwischen 5 und 200 Zeichen lang sein')
    ])
    
    description = TextAreaField('Beschreibung', validators=[
        DataRequired(message='Beschreibung ist erforderlich'),
        Length(min=50, max=5000, message='Beschreibung muss zwischen 50 und 5000 Zeichen lang sein')
    ])
    
    requirements = TextAreaField('Anforderungen', validators=[
        DataRequired(message='Anforderungen sind erforderlich'),
        Length(min=20, max=3000, message='Anforderungen müssen zwischen 20 und 3000 Zeichen lang sein')
    ])
    
    location = StringField('Standort', validators=[
        DataRequired(message='Standort ist erforderlich'),
        Length(min=2, max=100, message='Standort muss zwischen 2 und 100 Zeichen lang sein')
    ])
    
    salary_range = StringField('Gehaltsbereich', validators=[
        Length(max=100, message='Gehaltsbereich zu lang')
    ])
    
    employment_type = SelectField('Beschäftigungsart', choices=[
        ('Vollzeit', 'Vollzeit'),
        ('Teilzeit', 'Teilzeit'),
        ('Befristet', 'Befristet'),
        ('Praktikum', 'Praktikum')
    ], validators=[DataRequired(message='Beschäftigungsart ist erforderlich')])
    
    department = SelectField('Abteilung', choices=[
        ('Flight Operations', 'Flight Operations'),
        ('Maintenance', 'Maintenance'),
        ('Operations', 'Operations'),
        ('Cabin Services', 'Cabin Services'),
        ('Safety & Quality', 'Safety & Quality'),
        ('Administration', 'Administration'),
        ('IT', 'IT')
    ], validators=[DataRequired(message='Abteilung ist erforderlich')])
    
    referral_bonus = StringField('Referral-Bonus (EUR)', validators=[
        Regexp(r'^\d+(\.\d{2})?$', message='Ungültiges Bonus-Format (z.B. 1000.00)')
    ])
    
    is_active = BooleanField('Aktiv')
    
    submit = SubmitField('Stelle speichern')
