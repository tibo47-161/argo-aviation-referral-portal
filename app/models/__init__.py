# app/models/__init__.py - SQL Server optimiert
import uuid
from datetime import datetime
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    
    # SQL Server UNIQUEIDENTIFIER für bessere Performance
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    
    # DATETIMEOFFSET für SQL Server Zeitzone-Unterstützung
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Beziehungen
    referrals_made = db.relationship('Referral', backref='referrer_user', lazy=True, 
                                   foreign_keys='Referral.referrer_id')

    def __repr__(self):
        return f"User('{self.email}')"

    # Flask-Login erforderliche Methoden
    def get_id(self):
        return str(self.user_id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active_user(self):
        return bool(self.is_active)
    
    @property
    def is_anonymous(self):
        return False

    # Passwort-Methoden
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class JobListing(db.Model):
    __tablename__ = 'Job_Listings'
    
    job_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    
    # TEXT für große Textfelder - SQL Server kompatibel
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    
    location = db.Column(db.String(255), nullable=False)
    salary_range = db.Column(db.String(100))
    employment_type = db.Column(db.String(50))
    department = db.Column(db.String(100))
    posting_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # DECIMAL für Geldbeträge
    referral_bonus = db.Column(db.Numeric(10, 2))

    # Beziehungen
    referrals_for_job = db.relationship('Referral', backref='job_listing', lazy=True, 
                                      foreign_keys='Referral.job_id')

    def __repr__(self):
        return f"JobListing('{self.title}', '{self.location}')"


class Referral(db.Model):
    __tablename__ = 'Referrals'
    
    referral_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    referrer_id = db.Column(db.String(36), db.ForeignKey('Users.user_id'), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey('Job_Listings.job_id'), nullable=False)
    applicant_email = db.Column(db.String(255), nullable=False)
    applicant_name = db.Column(db.String(255), nullable=False)
    referral_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)
    
    # TEXT für Notizen - SQL Server kompatibel
    notes = db.Column(db.Text)
    
    commission_amount = db.Column(db.Numeric(10, 2))
    commission_paid = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Referral('{self.applicant_name}', '{self.status}')"