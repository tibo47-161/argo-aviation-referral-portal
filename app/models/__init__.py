# app/models/__init__.py - SQL Server optimiert mit Superadmin-Features
import uuid
from datetime import datetime
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# Superadmin-Konfiguration
SUPERADMIN_EMAIL = "tobi196183@gmail.com"

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    referrals_made = db.relationship('Referral', backref='referrer_user', lazy=True, 
                                   foreign_keys='Referral.referrer_id')
    
    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_superadmin(self):
        return self.email.lower() == SUPERADMIN_EMAIL.lower()

    def has_permission(self, permission):
        if self.is_superadmin:
            return True
        if self.is_admin:
            admin_permissions = ['view_users', 'edit_jobs', 'view_reports']
            return permission in admin_permissions
        user_permissions = ['create_referral', 'view_jobs']
        return permission in user_permissions

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

class JobListing(db.Model):
    __tablename__ = 'Job_Listings'
    
    job_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(255), nullable=False)
    salary_range = db.Column(db.String(100))
    employment_type = db.Column(db.String(50))
    department = db.Column(db.String(100))
    posting_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    referral_bonus = db.Column(db.Numeric(10, 2))
    creator_id = db.Column(db.String(36), db.ForeignKey('Users.user_id'))
    priority = db.Column(db.String(20), default='normal')
    tags = db.Column(db.Text)
    external_job_id = db.Column(db.String(100))
    
    referrals_for_job = db.relationship('Referral', backref='job_listing', lazy=True, 
                                      foreign_keys='Referral.job_id')
    creator = db.relationship('User', backref='created_jobs', foreign_keys=[creator_id])
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return datetime.utcnow() > self.expiry_date
        return False

class Referral(db.Model):
    __tablename__ = 'Referrals'
    
    referral_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    referrer_id = db.Column(db.String(36), db.ForeignKey('Users.user_id'), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey('Job_Listings.job_id'), nullable=False)
    applicant_email = db.Column(db.String(255), nullable=False)
    applicant_name = db.Column(db.String(255), nullable=False)
    referral_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='submitted')
    notes = db.Column(db.Text)
    commission_amount = db.Column(db.Numeric(10, 2))
    commission_paid = db.Column(db.Boolean, default=False)
    applicant_phone = db.Column(db.String(20))
    applicant_linkedin = db.Column(db.String(255))
    resume_path = db.Column(db.String(500))
    interview_date = db.Column(db.DateTime)
    hired_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    zoho_candidate_id = db.Column(db.String(100))
    zoho_application_id = db.Column(db.String(100))

    def update_status(self, new_status, notes=None):
        valid_statuses = [
            'submitted', 'under_review', 'interview_scheduled', 
            'interviewed', 'hired', 'rejected', 'withdrawn'
        ]
        
        if new_status in valid_statuses:
            self.status = new_status
            if notes:
                self.notes = notes
            if new_status == 'hired':
                self.hired_date = datetime.utcnow()
            db.session.commit()
            return True
        return False



    cover_letter = db.Column(db.Text)

