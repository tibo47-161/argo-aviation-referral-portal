# app/models/__init__.py
import uuid # Benötigt für UUID-Generierung
from datetime import datetime # Benötigt für datetime.utcnow (falls verwendet)
from .. import db # Importiert die db-Instanz aus dem übergeordneten Modul (app/__init__.py)
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, NVARCHAR, BIT, DATETIMEOFFSET, DECIMAL, TEXT # Spezifische SQL Server Typen
from sqlalchemy import Enum as SQLEnum # Für Python-Enum-Typen
from werkzeug.security import generate_password_hash, check_password_hash # Für Passwort-Hashing

# Definition der UserType Enum (für Typsicherheit in Python)
class UserType(SQLEnum):
    REFERRER = "referrer"
    APPLICANT = "applicant"
    ADMIN = "admin"

# --- Datenbank-Modelle definieren ---
# Stellen Sie sicher, dass die Tabellennamen ('__tablename__') exakt mit denen übereinstimmen,
# die Sie im Azure SQL Abfrage-Editor erstellt haben (Users, Job_Listings, Referrals).

class User(db.Model):
    __tablename__ = 'Users'
    # KORREKTUR: UUID wird in Python generiert und explizit als uuid.UUID-Objekt gespeichert.
    # SQLAlchemy und pyodbc sollten dies dann korrekt in UNIQUEIDENTIFIER konvertieren.
    user_id = db.Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: uuid.uuid4()) # WICHTIGE KORREKTUR
    email = db.Column(NVARCHAR(255), unique=True, nullable=False)
    password_hash = db.Column(NVARCHAR(255), nullable=False) # Länge für Hashes
    first_name = db.Column(NVARCHAR(100), nullable=False)
    last_name = db.Column(NVARCHAR(100), nullable=False)
    phone_number = db.Column(NVARCHAR(20))
    registration_date = db.Column(DATETIMEOFFSET, default=db.func.GETUTCDATE())
    last_login = db.Column(DATETIMEOFFSET)
    is_active = db.Column(BIT, default=True)
    user_type = db.Column(NVARCHAR(50), nullable=False)

    # Beziehungen (optional, aber gut für Navigation)
    referrals_made = db.relationship('Referral', backref='referrer_user', lazy=True, foreign_keys='Referral.referrer_id', overlaps="referrer_obj")


    def __repr__(self):
        return f"User('{self.email}', '{self.user_type}')"

    # Methoden zum Hashen und Überprüfen von Passwörtern
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class JobListing(db.Model):
    __tablename__ = 'Job_Listings'
    job_id = db.Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: uuid.uuid4()) # KORREKTUR
    title = db.Column(NVARCHAR(255), nullable=False)
    description = db.Column(NVARCHAR(max)) # NVARCHAR(MAX) in SQL Server
    requirements = db.Column(NVARCHAR(max))
    location = db.Column(NVARCHAR(255), nullable=False)
    salary_range = db.Column(NVARCHAR(100))
    employment_type = db.Column(NVARCHAR(50)) # 'full-time', 'part-time', 'contract'
    department = db.Column(NVARCHAR(100))
    posting_date = db.Column(DATETIMEOFFSET, default=db.func.GETUTCDATE())
    expiry_date = db.Column(DATETIMEOFFSET)
    is_active = db.Column(BIT, default=True)
    referral_bonus = db.Column(DECIMAL(10, 2))

    # Beziehungen (optional)
    referrals_for_job = db.relationship('Referral', backref='job_listing', lazy=True, foreign_keys='Referral.job_id', overlaps="job_obj")


    def __repr__(self):
        return f"JobListing('{self.title}', '{self.location}')"


class Referral(db.Model):
    __tablename__ = 'Referrals'
    referral_id = db.Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: uuid.uuid4()) # KORREKTUR
    referrer_id = db.Column(UNIQUEIDENTIFIER, db.ForeignKey('Users.user_id'), nullable=False)
    job_id = db.Column(UNIQUEIDENTIFIER, db.ForeignKey('Job_Listings.job_id'), nullable=False)
    applicant_email = db.Column(NVARCHAR(255), nullable=False)
    applicant_name = db.Column(NVARCHAR(255), nullable=False)
    referral_date = db.Column(DATETIMEOFFSET, default=db.func.GETUTCDATE())
    status = db.Column(NVARCHAR(50), nullable=False) # 'pending', 'reviewed', 'hired', 'rejected'
    notes = db.Column(NVARCHAR(max))
    commission_amount = db.Column(DECIMAL(10, 2))
    commission_paid = db.Column(BIT, default=False)

    # Beziehungen: explizite Definitionen für den Zugriff auf die verknüpften Objekte
    referrer_obj = db.relationship('User', foreign_keys=[referrer_id], overlaps="referrals_made")
    job_obj = db.relationship('JobListing', foreign_keys=[job_id], overlaps="referrals_for_job")


    def __repr__(self):
        return f"Referral('{self.applicant_name}', '{self.status}')"