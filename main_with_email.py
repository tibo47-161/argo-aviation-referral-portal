"""
Argo Aviation Referral Portal - Enhanced with Email Confirmation
Completely working version with proper URL routing, Argo colors, and email confirmation
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

# SendGrid configuration
SENDGRID_API_KEY = "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"
FROM_EMAIL = "noreply@argo-aviation.com"
FROM_NAME = "Argo Aviation Referral Portal"

db = SQLAlchemy(app)

# Enhanced Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Email confirmation fields (optional - existing users not affected)
    email_confirmed = db.Column(db.Boolean, default=True)  # Default True for backward compatibility
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
                .header {{ background: linear-gradient(135deg, #DAA520, #B8860B); color: white; padding: 20px; text-align: center; border-radius: 5px; margin-bottom: 20px; }}
                .content {{ color: #333; line-height: 1.6; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #DAA520, #B8860B); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
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
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# HTML Template with Argo Colors (unchanged)
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} - Argo Aviation Referral Portal</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #2c3e50, #34495e);
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #DAA520, #B8860B);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .nav {
            display: flex;
            gap: 2rem;
            align-items: center;
        }
        
        .nav a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: opacity 0.3s;
        }
        
        .nav a:hover {
            opacity: 0.8;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
            outline: none;
            border-color: #DAA520;
        }
        
        .btn {
            background: linear-gradient(135deg, #DAA520, #B8860B);
            color: white;
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(218, 165, 32, 0.4);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #6c757d, #5a6268);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #dc3545, #c82333);
        }
        
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .alert-success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-info {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #DAA520, #B8860B);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
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
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .job-card:hover {
            transform: translateY(-5px);
        }
        
        .job-title {
            color: #DAA520;
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .job-company {
            color: #666;
            margin-bottom: 0.5rem;
        }
        
        .job-location {
            color: #888;
            margin-bottom: 1rem;
        }
        
        .job-bonus {
            background: linear-gradient(135deg, #DAA520, #B8860B);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 1rem;
        }
        
        .referral-status {
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.875rem;
            font-weight: 600;
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
        
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav {
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .container {
                padding: 1rem;
            }
            
            .jobs-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">
                🛩️ Argo Aviation Referral Portal
            </div>
            <nav class="nav">
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
            </nav>
        </div>
    </div>
    
    <div class="container">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.category }}">{{ message.text }}</div>
            {% endfor %}
        {% endif %}
        
        {{content}}
    </div>
</body>
</html>
"""

def render_template(template_content, **kwargs):
    """Render template with base template"""
    # Handle flash messages
    messages = []
    if hasattr(session, '_flashes') and session._flashes:
        for category, message in session._flashes:
            messages.append({'category': category if category != 'message' else 'info', 'text': message})
        session._flashes.clear()
    
    kwargs['messages'] = messages
    kwargs['session'] = session
    
    # Replace content placeholder
    full_template = BASE_TEMPLATE.replace('{{content}}', template_content)
    
    # Simple template rendering
    for key, value in kwargs.items():
        if isinstance(value, str):
            full_template = full_template.replace('{{' + key + '}}', str(value))
        elif key == 'jobs' and isinstance(value, list):
            # Handle jobs list
            jobs_html = ""
            for job in value:
                jobs_html += f"""
                <div class="job-card">
                    <div class="job-title">{job.title}</div>
                    <div class="job-company">{job.company}</div>
                    <div class="job-location">📍 {job.location}</div>
                    <div class="job-bonus">💰 Referral Bonus: €{job.bonus_amount:,.0f}</div>
                    <p>{job.description[:150]}...</p>
                    <a href="/job/{job.id}" class="btn">Details ansehen</a>
                </div>
                """
            full_template = full_template.replace('{{jobs_html}}', jobs_html)
        elif key == 'referrals' and isinstance(value, list):
            # Handle referrals list
            referrals_html = ""
            for referral in value:
                job = Job.query.get(referral.job_id)
                status_class = f"status-{referral.status}"
                referrals_html += f"""
                <div class="job-card">
                    <div class="job-title">{job.title if job else 'Job nicht gefunden'}</div>
                    <div class="job-company">Kandidat: {referral.candidate_name}</div>
                    <div class="job-location">📧 {referral.candidate_email}</div>
                    <div class="referral-status {status_class}">{referral.status.title()}</div>
                    <p>Eingereicht: {referral.created_at.strftime('%d.%m.%Y')}</p>
                    {f'<p>Notizen: {referral.notes}</p>' if referral.notes else ''}
                </div>
                """
            full_template = full_template.replace('{{referrals_html}}', referrals_html)
    
    return full_template

# Routes (unchanged functionality, enhanced with email)
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    template = """
    <div class="card">
        <h1>Willkommen beim Argo Aviation Referral Portal</h1>
        <p>Empfehlen Sie qualifizierte Kandidaten für Luftfahrt-Positionen und verdienen Sie attraktive Referral-Boni.</p>
        
        <h2>Warum Argo Aviation?</h2>
        <ul>
            <li>🛩️ Führender Anbieter in der Luftfahrtbranche</li>
            <li>💰 Attraktive Referral-Boni bis zu €5.000</li>
            <li>🎯 Vielfältige Karrieremöglichkeiten</li>
            <li>🌍 Internationale Standorte</li>
        </ul>
        
        <div style="margin-top: 2rem;">
            <a href="/register" class="btn">Jetzt registrieren</a>
            <a href="/login" class="btn btn-secondary" style="margin-left: 1rem;">Anmelden</a>
        </div>
    </div>
    """
    
    return render_template(template, title="Willkommen")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.', 'error')
            return redirect(url_for('register'))
        
        # Create new user with email confirmation
        confirmation_token = secrets.token_urlsafe(32)
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            email_confirmed=False,  # New users need confirmation
            confirmation_token=confirmation_token,
            confirmation_sent_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Send confirmation email
        email_sent = send_confirmation_email(email, name, confirmation_token)
        
        if email_sent:
            flash('Registrierung erfolgreich! Bitte überprüfen Sie Ihre E-Mails zur Bestätigung.', 'success')
        else:
            flash('Registrierung erfolgreich! E-Mail-Bestätigung konnte nicht gesendet werden, aber Sie können sich trotzdem anmelden.', 'info')
            # Allow login even if email fails
            user.email_confirmed = True
            db.session.commit()
        
        return redirect(url_for('login'))
    
    template = """
    <div class="card">
        <h2>Registrierung</h2>
        <form method="POST">
            <div class="form-group">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="email">E-Mail:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Passwort:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Registrieren</button>
        </form>
        <p style="margin-top: 1rem;">
            Bereits registriert? <a href="/login">Hier anmelden</a>
        </p>
    </div>
    """
    
    return render_template(template, title="Registrierung")

@app.route('/confirm-email/<token>')
def confirm_email(token):
    user = User.query.filter_by(confirmation_token=token).first()
    
    if not user:
        flash('Ungültiger Bestätigungslink.', 'error')
        return redirect(url_for('login'))
    
    # Check if token is expired (24 hours)
    if user.confirmation_sent_at and datetime.utcnow() - user.confirmation_sent_at > timedelta(hours=24):
        flash('Bestätigungslink ist abgelaufen. Bitte registrieren Sie sich erneut.', 'error')
        return redirect(url_for('register'))
    
    # Confirm email
    user.email_confirmed = True
    user.confirmation_token = None
    user.confirmation_sent_at = None
    db.session.commit()
    
    flash('E-Mail erfolgreich bestätigt! Sie können sich jetzt anmelden.', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Allow login even if email not confirmed (backward compatibility)
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            
            if not user.email_confirmed:
                flash('Hinweis: Ihre E-Mail-Adresse ist noch nicht bestätigt. Überprüfen Sie Ihre E-Mails.', 'info')
            
            flash('Erfolgreich angemeldet!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Ungültige E-Mail oder Passwort.', 'error')
    
    template = """
    <div class="card">
        <h2>Anmeldung</h2>
        <form method="POST">
            <div class="form-group">
                <label for="email">E-Mail:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Passwort:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Anmelden</button>
        </form>
        <p style="margin-top: 1rem;">
            Noch nicht registriert? <a href="/register">Hier registrieren</a>
        </p>
    </div>
    """
    
    return render_template(template, title="Anmeldung")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get statistics
    total_jobs = Job.query.filter_by(is_active=True).count()
    user_referrals = Referral.query.filter_by(referrer_id=session['user_id']).count()
    
    template = f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{total_jobs}</div>
            <div>Aktive Jobs</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{user_referrals}</div>
            <div>Meine Referrals</div>
        </div>
    </div>
    
    <div class="card">
        <h2>Willkommen zurück, {session['user_name']}!</h2>
        <p>Hier ist Ihr Dashboard für das Argo Aviation Referral Portal.</p>
        
        <div style="margin-top: 2rem;">
            <a href="/jobs" class="btn">Jobs durchsuchen</a>
            <a href="/my-referrals" class="btn btn-secondary" style="margin-left: 1rem;">Meine Referrals</a>
        </div>
    </div>
    """
    
    return render_template(template, title="Dashboard")

@app.route('/jobs')
def jobs():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    jobs_list = Job.query.filter_by(is_active=True).all()
    
    template = """
    <div class="card">
        <h2>Verfügbare Stellenausschreibungen</h2>
        <p>Empfehlen Sie qualifizierte Kandidaten für diese Positionen:</p>
    </div>
    
    <div class="jobs-grid">
        {{jobs_html}}
    </div>
    """
    
    return render_template(template, title="Jobs", jobs=jobs_list)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    job = Job.query.get_or_404(job_id)
    
    template = f"""
    <div class="card">
        <h1>{job.title}</h1>
        <div class="job-company" style="font-size: 1.2rem; margin-bottom: 1rem;">
            <strong>{job.company}</strong> - {job.location}
        </div>
        
        <div class="job-bonus" style="font-size: 1.1rem; margin-bottom: 2rem;">
            💰 Referral Bonus: €{job.bonus_amount:,.0f}
        </div>
        
        <h3>Beschreibung</h3>
        <p style="margin-bottom: 2rem;">{job.description}</p>
        
        <h3>Anforderungen</h3>
        <p style="margin-bottom: 2rem;">{job.requirements}</p>
        
        <div>
            <a href="/submit-referral/{job.id}" class="btn">Referral einreichen</a>
            <a href="/jobs" class="btn btn-secondary" style="margin-left: 1rem;">Zurück zu Jobs</a>
        </div>
    </div>
    """
    
    return render_template(template, title=job.title)

@app.route('/submit-referral/<int:job_id>', methods=['GET', 'POST'])
def submit_referral(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        candidate_name = request.form['candidate_name']
        candidate_email = request.form['candidate_email']
        candidate_phone = request.form.get('candidate_phone', '')
        notes = request.form.get('notes', '')
        
        referral = Referral(
            job_id=job_id,
            referrer_id=session['user_id'],
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_phone=candidate_phone,
            notes=notes
        )
        
        db.session.add(referral)
        db.session.commit()
        
        flash('Referral erfolgreich eingereicht!', 'success')
        return redirect(url_for('my_referrals'))
    
    template = f"""
    <div class="card">
        <h2>Referral einreichen</h2>
        <p><strong>Position:</strong> {job.title} bei {job.company}</p>
        <p><strong>Referral Bonus:</strong> €{job.bonus_amount:,.0f}</p>
        
        <form method="POST" style="margin-top: 2rem;">
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
                <textarea id="notes" name="notes" rows="4" placeholder="Warum ist dieser Kandidat geeignet?"></textarea>
            </div>
            <button type="submit" class="btn">Referral einreichen</button>
            <a href="/job/{job.id}" class="btn btn-secondary" style="margin-left: 1rem;">Abbrechen</a>
        </form>
    </div>
    """
    
    return render_template(template, title="Referral einreichen")

@app.route('/my-referrals')
def my_referrals():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    referrals_list = Referral.query.filter_by(referrer_id=session['user_id']).order_by(Referral.created_at.desc()).all()
    
    template = """
    <div class="card">
        <h2>Meine Referrals</h2>
        <p>Hier sehen Sie alle Ihre eingereichten Referrals:</p>
    </div>
    
    <div class="jobs-grid">
        {{referrals_html}}
    </div>
    """
    
    if not referrals_list:
        template = """
        <div class="card">
            <h2>Meine Referrals</h2>
            <p>Sie haben noch keine Referrals eingereicht.</p>
            <a href="/jobs" class="btn">Jobs durchsuchen</a>
        </div>
        """
    
    return render_template(template, title="Meine Referrals", referrals=referrals_list)

@app.route('/logout')
def logout():
    session.clear()
    flash('Erfolgreich abgemeldet.', 'success')
    return redirect(url_for('index'))

# Initialize database and sample data
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add sample jobs if none exist
        if Job.query.count() == 0:
            sample_jobs = [
                Job(
                    title="Pilot (A320)",
                    company="Argo Aviation",
                    location="Frankfurt, Deutschland",
                    description="Wir suchen einen erfahrenen Piloten für unsere A320-Flotte. Sie werden nationale und internationale Flüge durchführen und dabei höchste Sicherheitsstandards einhalten.",
                    requirements="• Gültige ATPL-Lizenz\n• Mindestens 3.000 Flugstunden\n• A320 Type Rating\n• Englisch fließend\n• EU-Arbeitserlaubnis",
                    bonus_amount=2000.0
                ),
                Job(
                    title="Flugbegleiter/in",
                    company="Argo Aviation",
                    location="München, Deutschland",
                    description="Werden Sie Teil unseres Kabinen-Teams und sorgen Sie für das Wohlbefinden unserer Passagiere auf nationalen und internationalen Flügen.",
                    requirements="• Abgeschlossene Flugbegleiter-Ausbildung\n• Mindestens 2 Jahre Erfahrung\n• Mehrsprachigkeit (Deutsch, Englisch + weitere)\n• Kundenorientierung\n• Flexibilität bei Arbeitszeiten",
                    bonus_amount=800.0
                ),
                Job(
                    title="Flugzeug-Mechaniker",
                    company="Argo Aviation",
                    location="Hamburg, Deutschland",
                    description="Wartung und Instandhaltung unserer modernen Flugzeugflotte. Sie arbeiten in einem hochmodernen Hangar mit neuester Technologie.",
                    requirements="• Abgeschlossene Ausbildung als Fluggerätmechaniker\n• EASA Part-66 Lizenz\n• Mindestens 5 Jahre Berufserfahrung\n• Teamfähigkeit\n• Bereitschaft zu Schichtarbeit",
                    bonus_amount=1500.0
                )
            ]
            
            for job in sample_jobs:
                db.session.add(job)
            
            # Add admin user
            admin = User(
                name="Admin",
                email="admin@argo-aviation.com",
                password_hash=generate_password_hash("admin123"),
                is_admin=True,
                email_confirmed=True
            )
            db.session.add(admin)
            
            db.session.commit()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
