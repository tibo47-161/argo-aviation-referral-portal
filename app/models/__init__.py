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
    
    # Erweiterte Benutzer-Eigenschaften
    is_admin = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Text)  # JSON-String für erweiterte Berechtigungen
    notes = db.Column(db.Text)  # Admin-Notizen über den Benutzer
    
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
    
    # Superadmin-Methoden
    @property
    def is_superadmin(self):
        """Überprüft, ob der Benutzer ein Superadmin ist"""
        return self.email.lower() == SUPERADMIN_EMAIL.lower()
    
    def has_permission(self, permission):
        """Überprüft, ob der Benutzer eine bestimmte Berechtigung hat"""
        if self.is_superadmin:
            return True  # Superadmin hat alle Berechtigungen
        
        if self.is_admin:
            # Admin-Berechtigungen hier definieren
            admin_permissions = ['view_users', 'edit_jobs', 'view_reports']
            return permission in admin_permissions
        
        # Standard-Benutzer-Berechtigungen
        user_permissions = ['create_referral', 'view_jobs']
        return permission in user_permissions
    
    def update_last_login(self):
        """Aktualisiert das letzte Login-Datum"""
        self.last_login = datetime.utcnow()
        db.session.commit()

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
    
    # Erweiterte Job-Eigenschaften
    created_by = db.Column(db.String(36), db.ForeignKey('Users.user_id'))
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    tags = db.Column(db.Text)  # JSON-String für Job-Tags
    external_job_id = db.Column(db.String(100))  # Für Zoho ATS Integration
    
    # Beziehungen
    referrals_for_job = db.relationship('Referral', backref='job_listing', lazy=True, 
                                      foreign_keys='Referral.job_id')
    creator = db.relationship('User', backref='created_jobs', foreign_keys=[created_by])
    
    def __repr__(self):
        return f"JobListing('{self.title}', '{self.location}')"
    
    @property
    def is_expired(self):
        """Überprüft, ob die Stellenausschreibung abgelaufen ist"""
        if self.expiry_date:
            return datetime.utcnow() > self.expiry_date
        return False
    
    def get_referral_count(self):
        """Gibt die Anzahl der Referrals für diese Stelle zurück"""
        return len(self.referrals_for_job)

class Referral(db.Model):
    __tablename__ = 'Referrals'
    
    referral_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    referrer_id = db.Column(db.String(36), db.ForeignKey('Users.user_id'), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey('Job_Listings.job_id'), nullable=False)
    applicant_email = db.Column(db.String(255), nullable=False)
    applicant_name = db.Column(db.String(255), nullable=False)
    referral_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='submitted')
    
    # TEXT für Notizen - SQL Server kompatibel
    notes = db.Column(db.Text)
    
    commission_amount = db.Column(db.Numeric(10, 2))
    commission_paid = db.Column(db.Boolean, default=False)
    
    # Erweiterte Referral-Eigenschaften
    applicant_phone = db.Column(db.String(20))
    applicant_linkedin = db.Column(db.String(255))
    resume_path = db.Column(db.String(500))  # Pfad zur Lebenslauf-Datei
    interview_date = db.Column(db.DateTime)
    hired_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Zoho ATS Integration
    zoho_candidate_id = db.Column(db.String(100))
    zoho_application_id = db.Column(db.String(100))
    
    def __repr__(self):
        return f"Referral('{self.applicant_name}', '{self.status}')"
    
    def update_status(self, new_status, notes=None):
        """Aktualisiert den Status des Referrals"""
        valid_statuses = [
            'submitted', 'under_review', 'interview_scheduled', 
            'interviewed', 'hired', 'rejected', 'withdrawn'
        ]
        
        if new_status in valid_statuses:
            self.status = new_status
            if notes:
                self.notes = notes
            
            # Automatische Datumsfelder setzen
            if new_status == 'hired':
                self.hired_date = datetime.utcnow()
            
            db.session.commit()
            return True
        return False

# Hilfsfunktionen für Superadmin
def get_system_stats():
    """Gibt System-Statistiken für das Admin-Dashboard zurück"""
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_jobs': JobListing.query.count(),
        'active_jobs': JobListing.query.filter_by(is_active=True).count(),
        'total_referrals': Referral.query.count(),
        'successful_referrals': Referral.query.filter_by(status='hired').count(),
        'pending_referrals': Referral.query.filter(
            Referral.status.in_(['submitted', 'under_review', 'interview_scheduled'])
        ).count()
    }
    return stats

def get_recent_activity(limit=10):
    """Gibt die neuesten Aktivitäten im System zurück"""
    recent_referrals = Referral.query.order_by(Referral.referral_date.desc()).limit(limit).all()
    recent_jobs = JobListing.query.order_by(JobListing.posting_date.desc()).limit(limit).all()
    recent_users = User.query.order_by(User.registration_date.desc()).limit(limit).all()
    
    return {
        'referrals': recent_referrals,
        'jobs': recent_jobs,
        'users': recent_users
    }
