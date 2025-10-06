"""
Argo Aviation Referral Portal - FIXED VERSION
Completely working version with proper URL routing and Argo colors
Updated: 2025-01-06 - Template rendering fix
"""

from flask import Flask, request, redirect, url_for, session, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import secrets
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

app = Flask(__name__)
app.config['SECRET_KEY'] = 'argo-aviation-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///argo_referral.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# SendGrid configuration
SENDGRID_API_KEY = "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"
FROM_EMAIL = "noreply@argo-aviation.com"
FROM_NAME = "Argo Aviation Referral Portal"

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Email confirmation fields
    email_confirmed = db.Column(db.Boolean, default=False)
    confirmation_token = db.Column(db.String(100), nullable=True)
    confirmation_sent_at = db.Column(db.DateTime, nullable=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    bonus_amount = db.Column(db.Float, default=1000.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    candidate_name = db.Column(db.String(100), nullable=False)
    candidate_email = db.Column(db.String(120), nullable=False)
    candidate_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# HTML Template with Argo Colors
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Argo Aviation Referral Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #f5f5f5; 
            color: #2F2F2F; 
            line-height: 1.6; 
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .header { 
            background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%); 
            color: #2F2F2F; 
            padding: 1rem 0; 
            box-shadow: 0 4px 15px rgba(218,165,32,0.3); 
        }
        .header h1 { 
            font-size: 1.8rem; 
            font-weight: 700; 
            color: #2F2F2F;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .nav { 
            background: #2F2F2F; 
            padding: 0; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.2); 
        }
        .nav a { 
            display: inline-block;
            color: #DAA520; 
            text-decoration: none; 
            padding: 15px 25px; 
            transition: all 0.3s ease;
            border-right: 1px solid #4A4A4A;
            font-weight: 600;
        }
        .nav a:hover, .nav a.active { 
            background: #4A4A4A; 
            color: #F4D03F; 
        }
        .main { padding: 2rem 0; min-height: calc(100vh - 200px); }
        .card { 
            background: white; 
            padding: 2rem; 
            border-radius: 10px; 
            box-shadow: 0 5px 20px rgba(0,0,0,0.1); 
            margin-bottom: 2rem;
            border-left: 5px solid #DAA520;
        }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { 
            display: block; 
            margin-bottom: 0.5rem; 
            font-weight: 600; 
            color: #2F2F2F; 
        }
        .form-group input, .form-group textarea, .form-group select { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus { 
            outline: none; 
            border-color: #DAA520; 
            box-shadow: 0 0 0 3px rgba(218,165,32,0.1);
        }
        .btn { 
            background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%); 
            color: #2F2F2F; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1rem; 
            font-weight: 600;
            text-decoration: none; 
            display: inline-block; 
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(218,165,32,0.3);
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 6px 25px rgba(218,165,32,0.4);
        }
        .btn-secondary { 
            background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%); 
            color: white;
        }
        .btn-danger { 
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); 
            color: white;
        }
        .alert { 
            padding: 1rem; 
            border-radius: 8px; 
            margin-bottom: 1rem; 
            border-left: 5px solid;
        }
        .alert-success { 
            background-color: #d4edda; 
            color: #155724; 
            border-left-color: #28a745;
        }
        .alert-error { 
            background-color: #f8d7da; 
            color: #721c24; 
            border-left-color: #dc3545;
        }
        .alert-info { 
            background-color: #d1ecf1; 
            color: #0c5460; 
            border-left-color: #17a2b8;
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 1.5rem; 
            margin-bottom: 2rem; 
        }
        .stat-card { 
            background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%); 
            color: #2F2F2F; 
            padding: 2rem; 
            border-radius: 10px; 
            text-align: center;
            box-shadow: 0 5px 20px rgba(218,165,32,0.3);
        }
        .stat-number { 
            font-size: 2.5rem; 
            font-weight: 700; 
            margin-bottom: 0.5rem; 
        }
        .stat-label { 
            font-size: 1.1rem; 
            font-weight: 600; 
        }
        .jobs-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); 
            gap: 1.5rem; 
        }
        .job-card { 
            background: white; 
            border-radius: 10px; 
            padding: 1.5rem; 
            box-shadow: 0 5px 20px rgba(0,0,0,0.1); 
            transition: all 0.3s ease;
            border-left: 5px solid #DAA520;
        }
        .job-card:hover { 
            transform: translateY(-5px); 
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        .job-title { 
            color: #DAA520; 
            font-size: 1.3rem; 
            font-weight: 700; 
            margin-bottom: 0.5rem; 
        }
        .job-company { 
            color: #666; 
            margin-bottom: 0.5rem; 
            font-weight: 600;
        }
        .job-location { 
            color: #888; 
            margin-bottom: 1rem; 
        }
        .job-bonus { 
            background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%); 
            color: #2F2F2F; 
            padding: 0.5rem 1rem; 
            border-radius: 20px; 
            font-weight: 700; 
            display: inline-block; 
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }
        .referral-status { 
            padding: 0.3rem 1rem; 
            border-radius: 15px; 
            font-size: 0.85rem; 
            font-weight: 600; 
            text-transform: uppercase;
        }
        .status-pending { 
            background-color: #fff3cd; 
            color: #856404; 
        }
        .status-approved { 
            background-color: #d4edda; 
            color: #155724; 
        }
        .status-rejected { 
            background-color: #f8d7da; 
            color: #721c24; 
        }
        .footer { 
            background: #2F2F2F; 
            color: #DAA520; 
            text-align: center; 
            padding: 2rem 0; 
            margin-top: 3rem;
        }
        @media (max-width: 768px) { 
            .nav a { padding: 12px 15px; font-size: 0.9rem; }
            .jobs-grid { grid-template-columns: 1fr; }
            .stats-grid { grid-template-columns: 1fr; }
            .card { padding: 1.5rem; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🛩️ Argo Aviation Referral Portal</h1>
        </div>
    </div>
    
    <div class="nav">
        <div class="container">
            {% if session.user_id %}
                <a href="/dashboard">Dashboard</a>
                <a href="/jobs">Jobs</a>
                <a href="/my-referrals">Meine Referrals</a>
                <a href="/logout">Abmelden</a>
            {% else %}
                <a href="/">Home</a>
                <a href="/login">Anmelden</a>
                <a href="/register">Registrieren</a>
            {% endif %}
        </div>
    </div>
    
    <div class="main">
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'info' }}">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            {{ content|safe }}
        </div>
    </div>
    
    <div class="footer">
        <div class="container">
            <p>&copy; 2024 Argo Aviation. Alle Rechte vorbehalten.</p>
        </div>
    </div>
</body>
</html>
'''

def send_confirmation_email(user_email, user_name, confirmation_token):
    """Send email confirmation to new user"""
    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        
        confirmation_url = f"https://web-production-9c059.up.railway.app/confirm-email/{confirmation_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #DAA520, #B8860B); color: #2F2F2F; padding: 20px; text-align: center; border-radius: 5px; margin-bottom: 20px; }}
                .content {{ color: #333; line-height: 1.6; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #DAA520, #B8860B); color: #2F2F2F; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛩️ Argo Aviation</h1>
                    <p>Referral Portal - E-Mail Bestätigung</p>
                </div>
                <div class="content">
                    <h2>Willkommen, {user_name}!</h2>
                    <p>Vielen Dank für Ihre Registrierung beim Argo Aviation Referral Portal.</p>
                    <p>Um Ihr Konto zu aktivieren, klicken Sie bitte auf den folgenden Button:</p>
                    
                    <a href="{confirmation_url}" class="button">E-Mail Adresse bestätigen</a>
                    
                    <p>Falls der Button nicht funktioniert, kopieren Sie diesen Link in Ihren Browser:</p>
                    <p style="word-break: break-all; color: #666;">{confirmation_url}</p>
                    
                    <p><strong>Wichtig:</strong> Dieser Link ist 24 Stunden gültig.</p>
                    
                    <p>Mit freundlichen Grüßen,<br>
                    Ihr Argo Aviation Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        from_email = Email(FROM_EMAIL, FROM_NAME)
        to_email = To(user_email)
        subject = "Argo Aviation - E-Mail Bestätigung erforderlich"
        
        mail = Mail(from_email, to_email, subject, Content("text/html", html_content))
        
        response = sg.send(mail)
        print(f"Email sent successfully. Status code: {response.status_code}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    content = '''
    <div class="card">
        <h1>Willkommen beim Argo Aviation Referral Portal</h1>
        <p style="font-size: 1.2rem; margin-bottom: 2rem;">Empfehlen Sie qualifizierte Kandidaten für Luftfahrt-Positionen und verdienen Sie attraktive Referral-Boni.</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">€5.000</div>
                <div class="stat-label">Max. Referral Bonus</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">50+</div>
                <div class="stat-label">Aktive Positionen</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">15</div>
                <div class="stat-label">Länder weltweit</div>
            </div>
        </div>
        
        <h2>Warum Argo Aviation?</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin: 2rem 0;">
            <div>
                <h3 style="color: #DAA520; margin-bottom: 1rem;">🛩️ Branchenführer</h3>
                <p>Führender Anbieter in der Luftfahrtbranche mit internationaler Präsenz</p>
            </div>
            <div>
                <h3 style="color: #DAA520; margin-bottom: 1rem;">💰 Attraktive Boni</h3>
                <p>Referral-Boni bis zu €5.000 für erfolgreiche Vermittlungen</p>
            </div>
            <div>
                <h3 style="color: #DAA520; margin-bottom: 1rem;">🎯 Vielfältige Jobs</h3>
                <p>Von Piloten bis hin zu Technikern - vielfältige Karrieremöglichkeiten</p>
            </div>
            <div>
                <h3 style="color: #DAA520; margin-bottom: 1rem;">🌍 Global</h3>
                <p>Internationale Standorte in über 15 Ländern weltweit</p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 3rem;">
            <a href="/register" class="btn" style="margin-right: 1rem;">Jetzt registrieren</a>
            <a href="/login" class="btn btn-secondary">Anmelden</a>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Willkommen", content=content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('E-Mail-Adresse bereits registriert!', 'error')
            return redirect(url_for('register'))
        
        # Generate confirmation token
        confirmation_token = secrets.token_urlsafe(32)
        
        # Create new user (not confirmed yet)
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            email_confirmed=False,
            confirmation_token=confirmation_token,
            confirmation_sent_at=datetime.utcnow()
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Send confirmation email
            if send_confirmation_email(email, name, confirmation_token):
                flash('Registrierung erfolgreich! Bitte überprüfen Sie Ihre E-Mails und bestätigen Sie Ihr Konto.', 'success')
            else:
                flash('Registrierung erfolgreich, aber E-Mail konnte nicht gesendet werden. Bitte kontaktieren Sie den Support.', 'error')
            
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Fehler bei der Registrierung. Bitte versuchen Sie es erneut.', 'error')
            return redirect(url_for('register'))
    
    content = '''
    <div class="card">
        <h1>Registrierung</h1>
        <p style="margin-bottom: 2rem;">Erstellen Sie Ihr Konto für das Argo Aviation Referral Portal</p>
        
        <form method="POST">
            <div class="form-group">
                <label for="name">Vollständiger Name:</label>
                <input type="text" id="name" name="name" required>
            </div>
            
            <div class="form-group">
                <label for="email">E-Mail-Adresse:</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="password">Passwort:</label>
                <input type="password" id="password" name="password" required minlength="6">
            </div>
            
            <button type="submit" class="btn">Registrieren</button>
            <a href="/login" class="btn btn-secondary" style="margin-left: 1rem;">Bereits registriert? Anmelden</a>
        </form>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Registrierung", content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Check if email is confirmed
            if not user.email_confirmed:
                flash('Bitte bestätigen Sie zuerst Ihre E-Mail-Adresse. Überprüfen Sie Ihr Postfach.', 'error')
                return redirect(url_for('login'))
            
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            flash(f'Willkommen zurück, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Ungültige E-Mail-Adresse oder Passwort!', 'error')
    
    content = '''
    <div class="card">
        <h1>Anmeldung</h1>
        <p style="margin-bottom: 2rem;">Melden Sie sich in Ihrem Argo Aviation Referral Portal Konto an</p>
        
        <form method="POST">
            <div class="form-group">
                <label for="email">E-Mail-Adresse:</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="password">Passwort:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn">Anmelden</button>
            <a href="/register" class="btn btn-secondary" style="margin-left: 1rem;">Noch kein Konto? Registrieren</a>
        </form>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Anmeldung", content=content)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get statistics
    total_jobs = Job.query.filter_by(is_active=True).count()
    user_referrals = Referral.query.filter_by(referrer_id=session['user_id']).count()
    approved_referrals = Referral.query.filter_by(referrer_id=session['user_id'], status='approved').count()
    
    # Get recent jobs
    recent_jobs = Job.query.filter_by(is_active=True).order_by(Job.created_at.desc()).limit(3).all()
    
    jobs_html = ""
    for job in recent_jobs:
        jobs_html += f'''
        <div class="job-card">
            <div class="job-title">{job.title}</div>
            <div class="job-company">{job.company}</div>
            <div class="job-location">📍 {job.location}</div>
            <div class="job-bonus">💰 Referral Bonus: €{job.bonus_amount:,.0f}</div>
            <p>{job.description[:150]}...</p>
            <a href="/job/{job.id}" class="btn">Details ansehen</a>
        </div>
        '''
    
    content = f'''
    <div class="card">
        <h1>Dashboard - Willkommen, {session['user_name']}!</h1>
        <p style="font-size: 1.1rem; margin-bottom: 2rem;">Hier ist Ihre Übersicht über aktuelle Referral-Möglichkeiten</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_jobs}</div>
                <div class="stat-label">Aktive Jobs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{user_referrals}</div>
                <div class="stat-label">Meine Referrals</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{approved_referrals}</div>
                <div class="stat-label">Genehmigte Referrals</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">€{approved_referrals * 2500:,.0f}</div>
                <div class="stat-label">Geschätzter Bonus</div>
            </div>
        </div>
        
        <h2>Neueste Job-Möglichkeiten</h2>
        <div class="jobs-grid">
            {jobs_html}
        </div>
        
        <div style="text-align: center; margin-top: 2rem;">
            <a href="/jobs" class="btn">Alle Jobs ansehen</a>
            <a href="/my-referrals" class="btn btn-secondary" style="margin-left: 1rem;">Meine Referrals</a>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Dashboard", content=content)

@app.route('/jobs')
def jobs():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    jobs = Job.query.filter_by(is_active=True).order_by(Job.created_at.desc()).all()
    
    jobs_html = ""
    for job in jobs:
        jobs_html += f'''
        <div class="job-card">
            <div class="job-title">{job.title}</div>
            <div class="job-company">{job.company}</div>
            <div class="job-location">📍 {job.location}</div>
            <div class="job-bonus">💰 Referral Bonus: €{job.bonus_amount:,.0f}</div>
            <p>{job.description[:150]}...</p>
            <a href="/job/{job.id}" class="btn">Details ansehen</a>
        </div>
        '''
    
    content = f'''
    <div class="card">
        <h1>Verfügbare Positionen</h1>
        <p style="font-size: 1.1rem; margin-bottom: 2rem;">Entdecken Sie aktuelle Job-Möglichkeiten und verdienen Sie Referral-Boni</p>
        
        <div class="jobs-grid">
            {jobs_html}
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Jobs", content=content)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    job = Job.query.get_or_404(job_id)
    
    content = f'''
    <div class="card">
        <h1>{job.title}</h1>
        <div style="margin-bottom: 2rem;">
            <p style="font-size: 1.2rem; color: #666; margin-bottom: 0.5rem;"><strong>{job.company}</strong></p>
            <p style="color: #888; margin-bottom: 1rem;">📍 {job.location}</p>
            <div class="job-bonus" style="font-size: 1.1rem;">💰 Referral Bonus: €{job.bonus_amount:,.0f}</div>
        </div>
        
        <h2>Stellenbeschreibung</h2>
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; line-height: 1.8;">
            {job.description.replace(chr(10), '<br>')}
        </div>
        
        <h2>Anforderungen</h2>
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; line-height: 1.8;">
            {job.requirements.replace(chr(10), '<br>')}
        </div>
        
        <div style="text-align: center;">
            <a href="/refer/{job.id}" class="btn" style="font-size: 1.1rem; padding: 15px 40px;">Kandidaten empfehlen</a>
            <a href="/jobs" class="btn btn-secondary" style="margin-left: 1rem;">Zurück zu Jobs</a>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title=job.title, content=content)

@app.route('/refer/<int:job_id>', methods=['GET', 'POST'])
def refer_candidate(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        candidate_name = request.form['candidate_name']
        candidate_email = request.form['candidate_email']
        candidate_phone = request.form.get('candidate_phone', '')
        notes = request.form.get('notes', '')
        
        # Check if referral already exists
        existing_referral = Referral.query.filter_by(
            job_id=job_id, 
            candidate_email=candidate_email
        ).first()
        
        if existing_referral:
            flash('Dieser Kandidat wurde bereits für diese Position empfohlen!', 'error')
            return redirect(url_for('refer_candidate', job_id=job_id))
        
        # Create new referral
        referral = Referral(
            job_id=job_id,
            referrer_id=session['user_id'],
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_phone=candidate_phone,
            notes=notes
        )
        
        try:
            db.session.add(referral)
            db.session.commit()
            flash(f'Referral für {candidate_name} erfolgreich eingereicht!', 'success')
            return redirect(url_for('my_referrals'))
        except Exception as e:
            db.session.rollback()
            flash('Fehler beim Einreichen des Referrals. Bitte versuchen Sie es erneut.', 'error')
    
    content = f'''
    <div class="card">
        <h1>Kandidaten empfehlen</h1>
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
            <h3 style="color: #DAA520; margin-bottom: 1rem;">{job.title}</h3>
            <p><strong>{job.company}</strong> • {job.location}</p>
            <div class="job-bonus" style="margin-top: 1rem;">💰 Referral Bonus: €{job.bonus_amount:,.0f}</div>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label for="candidate_name">Name des Kandidaten:</label>
                <input type="text" id="candidate_name" name="candidate_name" required>
            </div>
            
            <div class="form-group">
                <label for="candidate_email">E-Mail des Kandidaten:</label>
                <input type="email" id="candidate_email" name="candidate_email" required>
            </div>
            
            <div class="form-group">
                <label for="candidate_phone">Telefonnummer (optional):</label>
                <input type="tel" id="candidate_phone" name="candidate_phone">
            </div>
            
            <div class="form-group">
                <label for="notes">Zusätzliche Notizen:</label>
                <textarea id="notes" name="notes" rows="4" placeholder="Warum ist dieser Kandidat geeignet? Besondere Qualifikationen, Erfahrungen..."></textarea>
            </div>
            
            <button type="submit" class="btn">Referral einreichen</button>
            <a href="/job/{job.id}" class="btn btn-secondary" style="margin-left: 1rem;">Zurück</a>
        </form>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Kandidaten empfehlen", content=content)

@app.route('/my-referrals')
def my_referrals():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    referrals = Referral.query.filter_by(referrer_id=session['user_id']).order_by(Referral.created_at.desc()).all()
    
    referrals_html = ""
    for referral in referrals:
        job = Job.query.get(referral.job_id)
        status_class = f"status-{referral.status}"
        
        referrals_html += f'''
        <div class="job-card">
            <div class="job-title">{job.title if job else 'Job nicht gefunden'}</div>
            <div class="job-company">Kandidat: {referral.candidate_name}</div>
            <div class="job-location">📧 {referral.candidate_email}</div>
            {f'<div class="job-location">📞 {referral.candidate_phone}</div>' if referral.candidate_phone else ''}
            <div class="referral-status {status_class}">{referral.status.title()}</div>
            <p><strong>Eingereicht:</strong> {referral.created_at.strftime('%d.%m.%Y um %H:%M')}</p>
            {f'<p><strong>Notizen:</strong> {referral.notes}</p>' if referral.notes else ''}
            {f'<div class="job-bonus">💰 Bonus: €{job.bonus_amount:,.0f}</div>' if job else ''}
        </div>
        '''
    
    if not referrals_html:
        referrals_html = '<p style="text-align: center; color: #666; font-size: 1.1rem;">Sie haben noch keine Referrals eingereicht.</p>'
    
    content = f'''
    <div class="card">
        <h1>Meine Referrals</h1>
        <p style="font-size: 1.1rem; margin-bottom: 2rem;">Übersicht über alle Ihre eingereichten Kandidaten-Empfehlungen</p>
        
        <div class="jobs-grid">
            {referrals_html}
        </div>
        
        <div style="text-align: center; margin-top: 2rem;">
            <a href="/jobs" class="btn">Neue Referrals erstellen</a>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Meine Referrals", content=content)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sie wurden erfolgreich abgemeldet.', 'info')
    return redirect(url_for('index'))

# Initialize database and sample data
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add sample jobs if none exist
        if Job.query.count() == 0:
            sample_jobs = [
                Job(
                    title="Senior Pilot - Airbus A320",
                    company="Argo Aviation",
                    location="Frankfurt, Deutschland",
                    description="Wir suchen einen erfahrenen Piloten für unsere Airbus A320 Flotte. Sie werden internationale Routen fliegen und Teil unseres professionellen Piloten-Teams sein.\n\nVerantwortlichkeiten:\n• Sichere Durchführung von Flügen gemäß EASA-Vorschriften\n• Zusammenarbeit mit der Kabinencrew\n• Regelmäßige Schulungen und Weiterbildungen\n• Einhaltung aller Sicherheitsprotokoll",
                    requirements="• ATPL-Lizenz mit A320 Type Rating\n• Mindestens 3.000 Flugstunden\n• Fließende Deutsch- und Englischkenntnisse\n• EU-Arbeitserlaubnis\n• Medizinisches Tauglichkeitszeugnis Klasse 1\n• Teamfähigkeit und Stressresistenz",
                    bonus_amount=5000.0
                ),
                Job(
                    title="Flugzeugmechaniker - Wartung",
                    company="Argo Aviation",
                    location="München, Deutschland",
                    description="Für unser Wartungsteam suchen wir einen qualifizierten Flugzeugmechaniker. Sie werden für die Instandhaltung und Reparatur unserer Flugzeugflotte verantwortlich sein.\n\nAufgaben:\n• Durchführung von Wartungsarbeiten\n• Inspektion und Reparatur von Flugzeugsystemen\n• Dokumentation aller Arbeiten\n• Einhaltung der Luftfahrtvorschriften",
                    requirements="• Abgeschlossene Ausbildung als Fluggerätmechaniker\n• EASA Part-66 Lizenz (Kategorie A oder B)\n• Berufserfahrung in der Luftfahrt\n• Technisches Verständnis\n• Sorgfältige und gewissenhafte Arbeitsweise\n• Schichtbereitschaft",
                    bonus_amount=3000.0
                ),
                Job(
                    title="Kabinenpersonal - Flight Attendant",
                    company="Argo Aviation",
                    location="Berlin, Deutschland",
                    description="Werden Sie Teil unseres Kabinen-Teams und sorgen Sie für das Wohlbefinden unserer Passagiere. Wir bieten eine umfassende Ausbildung und attraktive Arbeitsbedingungen.\n\nIhre Aufgaben:\n• Betreuung der Passagiere während des Fluges\n• Sicherheitseinweisungen und Notfallmaßnahmen\n• Service und Verpflegung\n• Zusammenarbeit mit dem Cockpit-Team",
                    requirements="• Mindestalter 18 Jahre\n• Abitur oder gleichwertige Qualifikation\n• Sehr gute Deutsch- und Englischkenntnisse\n• Kundenorientierung und Servicebereitschaft\n• Körperliche Fitness\n• Flexibilität bei Arbeitszeiten\n• EU-Staatsbürgerschaft oder Arbeitserlaubnis",
                    bonus_amount=2000.0
                ),
                Job(
                    title="Luftverkehrskaufmann/-frau",
                    company="Argo Aviation",
                    location="Hamburg, Deutschland",
                    description="Für unsere Verwaltung suchen wir einen Luftverkehrskaufmann zur Unterstützung unserer operativen Abläufe. Sie werden in verschiedenen Bereichen der Luftfahrt tätig sein.\n\nTätigkeitsbereich:\n• Flugplanung und -koordination\n• Kundenbetreuung und Buchungsmanagement\n• Zusammenarbeit mit Behörden\n• Administrative Aufgaben",
                    requirements="• Abgeschlossene Ausbildung als Luftverkehrskaufmann/-frau\n• Kenntnisse der Luftfahrtbranche\n• Sehr gute Kommunikationsfähigkeiten\n• MS Office Kenntnisse\n• Organisationstalent\n• Teamfähigkeit",
                    bonus_amount=2500.0
                ),
                Job(
                    title="Fluglotse",
                    company="Argo Aviation Partners",
                    location="Köln, Deutschland",
                    description="Als Fluglotse übernehmen Sie die verantwortungsvolle Aufgabe der Flugverkehrskontrolle. Sie sorgen für einen sicheren und effizienten Luftverkehr.\n\nVerantwortlichkeiten:\n• Überwachung des Luftraums\n• Erteilung von Flugfreigaben\n• Koordination mit anderen Kontrollstellen\n• Notfallmanagement",
                    requirements="• Abgeschlossene Fluglotsen-Ausbildung\n• Fluglotsen-Lizenz\n• Sehr gute Englischkenntnisse\n• Stressresistenz und Konzentrationsfähigkeit\n• Schnelle Entscheidungsfindung\n• Medizinische Tauglichkeit",
                    bonus_amount=4000.0
                ),
                Job(
                    title="Aviation Safety Manager",
                    company="Argo Aviation",
                    location="Düsseldorf, Deutschland",
                    description="Verstärken Sie unser Safety-Team als Aviation Safety Manager. Sie entwickeln und überwachen Sicherheitsstandards für unsere gesamte Flotte.\n\nAufgaben:\n• Entwicklung von Sicherheitsrichtlinien\n• Durchführung von Safety-Audits\n• Unfalluntersuchungen\n• Schulung der Mitarbeiter\n• Berichtswesen an Behörden",
                    requirements="• Studium der Luftfahrttechnik oder vergleichbar\n• Mehrjährige Erfahrung im Aviation Safety\n• Kenntnisse der EASA-Vorschriften\n• Analytische Fähigkeiten\n• Führungsqualitäten\n• Sehr gute Englischkenntnisse",
                    bonus_amount=4500.0
                )
            ]
            
            for job in sample_jobs:
                db.session.add(job)
            
            db.session.commit()
            print("Sample jobs added successfully!")

@app.route('/confirm-email/<token>')
def confirm_email(token):
    """Confirm user email with token"""
    user = User.query.filter_by(confirmation_token=token).first()
    
    if not user:
        flash('Ungültiger oder abgelaufener Bestätigungslink.', 'error')
        return redirect(url_for('login'))
    
    # Check if token is expired (24 hours)
    if user.confirmation_sent_at and datetime.utcnow() - user.confirmation_sent_at > timedelta(hours=24):
        flash('Der Bestätigungslink ist abgelaufen. Bitte registrieren Sie sich erneut.', 'error')
        return redirect(url_for('register'))
    
    # Confirm the user
    user.email_confirmed = True
    user.confirmation_token = None
    user.confirmation_sent_at = None
    
    try:
        db.session.commit()
        flash('E-Mail erfolgreich bestätigt! Sie können sich jetzt anmelden.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Fehler bei der E-Mail-Bestätigung. Bitte versuchen Sie es erneut.', 'error')
    
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
