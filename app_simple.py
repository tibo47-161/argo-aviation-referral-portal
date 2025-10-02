#!/usr/bin/env python3
"""
Vereinfachte aber vollständige Argo Aviation Referral Portal App
Garantiert Azure-kompatibel mit allen Hauptfeatures
"""

import os
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Flask App Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'argo-aviation-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///argo_referral.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database Setup
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    referral_bonus = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_listing.id'), nullable=False)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    candidate_name = db.Column(db.String(100), nullable=False)
    candidate_email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Templates als Strings (Azure-sicher)
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Argo Aviation Referral Portal{% endblock %}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #334155; }
        .header { background: linear-gradient(135deg, #1e3a8a, #3730a3); color: white; padding: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .nav { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; }
        .nav-links { display: flex; gap: 20px; }
        .nav-links a { color: white; text-decoration: none; padding: 8px 16px; border-radius: 4px; transition: background 0.3s; }
        .nav-links a:hover { background: rgba(255,255,255,0.1); }
        .main { padding: 2rem 0; min-height: 80vh; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 2rem; margin-bottom: 2rem; }
        .btn { display: inline-block; padding: 10px 20px; background: #1e3a8a; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; transition: background 0.3s; }
        .btn:hover { background: #1e40af; }
        .btn-secondary { background: #64748b; }
        .btn-secondary:hover { background: #475569; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 14px; }
        .alert { padding: 12px; border-radius: 4px; margin-bottom: 1rem; }
        .alert-success { background: #dcfce7; border: 1px solid #16a34a; color: #15803d; }
        .alert-error { background: #fef2f2; border: 1px solid #dc2626; color: #dc2626; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .stat-number { font-size: 2rem; font-weight: bold; color: #1e3a8a; }
        .stat-label { color: #64748b; margin-top: 5px; }
        .job-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
        .job-card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 1.5rem; }
        .job-title { font-size: 1.25rem; font-weight: bold; color: #1e3a8a; margin-bottom: 10px; }
        .job-location { color: #64748b; margin-bottom: 10px; }
        .job-bonus { font-size: 1.1rem; font-weight: bold; color: #16a34a; margin-bottom: 15px; }
        .footer { background: #1e3a8a; color: white; text-align: center; padding: 2rem 0; }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <nav class="nav">
                <div class="logo">✈️ Argo Aviation Referral Portal</div>
                <div class="nav-links">
                    {% if session.user_id %}
                        <a href="{{ url_for('dashboard') }}">Dashboard</a>
                        <a href="{{ url_for('jobs') }}">Jobs</a>
                        <a href="{{ url_for('my_referrals') }}">Meine Referrals</a>
                        <a href="{{ url_for('logout') }}">Logout</a>
                    {% else %}
                        <a href="{{ url_for('login') }}">Login</a>
                        <a href="{{ url_for('register') }}">Registrieren</a>
                    {% endif %}
                </div>
            </nav>
        </div>
    </header>

    <main class="main">
        <div class="container">
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-success">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="content">
                {CONTENT}
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 Argo Aviation GmbH. Alle Rechte vorbehalten.</p>
        </div>
    </footer>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    content = '''
    <div class="card" style="text-align: center; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #1e3a8a; margin-bottom: 1rem;">Willkommen bei Argo Aviation</h1>
        <p style="font-size: 1.1rem; margin-bottom: 2rem; color: #64748b;">
            Ihr Partner für Luftfahrt-Recruiting und Referral-Programme
        </p>
        <div style="display: flex; gap: 1rem; justify-content: center;">
            <a href="{{ url_for('login') }}" class="btn">Anmelden</a>
            <a href="{{ url_for('register') }}" class="btn btn-secondary">Registrieren</a>
        </div>
    </div>
    '''
    template = BASE_TEMPLATE.replace('{CONTENT}', content)
    return render_template_string(template)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = f"{user.first_name} {user.last_name}"
            flash(f'Willkommen zurück, {user.first_name}!')
            return redirect(url_for('dashboard'))
        else:
            flash('Ungültige Anmeldedaten!')
    
    template = BASE_TEMPLATE + '''
    {% block content %}
    <div class="card" style="max-width: 400px; margin: 0 auto;">
        <h2 style="text-align: center; margin-bottom: 2rem; color: #1e3a8a;">Anmelden</h2>
        <form method="POST">
            <div class="form-group">
                <label>E-Mail:</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Passwort:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn" style="width: 100%;">Anmelden</button>
        </form>
        <p style="text-align: center; margin-top: 1rem;">
            Noch kein Konto? <a href="{{ url_for('register') }}">Hier registrieren</a>
        </p>
    </div>
    {% endblock %}
    '''
    return render_template_string(template)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('E-Mail bereits registriert!')
        else:
            user = User(first_name=first_name, last_name=last_name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.')
            return redirect(url_for('login'))
    
    template = BASE_TEMPLATE + '''
    {% block content %}
    <div class="card" style="max-width: 400px; margin: 0 auto;">
        <h2 style="text-align: center; margin-bottom: 2rem; color: #1e3a8a;">Registrieren</h2>
        <form method="POST">
            <div class="form-group">
                <label>Vorname:</label>
                <input type="text" name="first_name" required>
            </div>
            <div class="form-group">
                <label>Nachname:</label>
                <input type="text" name="last_name" required>
            </div>
            <div class="form-group">
                <label>E-Mail:</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Passwort:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn" style="width: 100%;">Registrieren</button>
        </form>
    </div>
    {% endblock %}
    '''
    return render_template_string(template)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Statistiken
    total_jobs = JobListing.query.filter_by(is_active=True).count()
    my_referrals = Referral.query.filter_by(referrer_id=session['user_id']).count()
    successful_referrals = Referral.query.filter_by(referrer_id=session['user_id'], status='hired').count()
    
    template = BASE_TEMPLATE + '''
    {% block content %}
    <h1 style="margin-bottom: 2rem;">Willkommen zurück, {{ session.user_name }}!</h1>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{{ total_jobs }}</div>
            <div class="stat-label">Aktive Stellen</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ my_referrals }}</div>
            <div class="stat-label">Meine Referrals</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ successful_referrals }}</div>
            <div class="stat-label">Erfolgreich</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">€{{ successful_referrals * 1500 }}</div>
            <div class="stat-label">Verdiente Boni</div>
        </div>
    </div>
    
    <div class="card">
        <h2 style="margin-bottom: 1rem;">Schnellzugriff</h2>
        <div style="display: flex; gap: 1rem;">
            <a href="{{ url_for('jobs') }}" class="btn">Stellen durchsuchen</a>
            <a href="{{ url_for('my_referrals') }}" class="btn btn-secondary">Meine Referrals</a>
        </div>
    </div>
    {% endblock %}
    '''
    return render_template_string(template, total_jobs=total_jobs, my_referrals=my_referrals, successful_referrals=successful_referrals)

@app.route('/jobs')
def jobs():
    jobs = JobListing.query.filter_by(is_active=True).all()
    
    template = BASE_TEMPLATE + '''
    {% block content %}
    <h1 style="margin-bottom: 2rem;">Aktuelle Stellenausschreibungen</h1>
    
    <div class="job-grid">
        {% for job in jobs %}
        <div class="job-card">
            <div class="job-title">{{ job.title }}</div>
            <div class="job-location">📍 {{ job.location }}</div>
            <div class="job-bonus">💰 €{{ job.referral_bonus }} Referral-Bonus</div>
            <p style="margin-bottom: 15px;">{{ job.description[:100] }}...</p>
            <a href="{{ url_for('job_detail', job_id=job.id) }}" class="btn">Details ansehen</a>
        </div>
        {% endfor %}
    </div>
    {% endblock %}
    '''
    return render_template_string(template, jobs=jobs)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = JobListing.query.get_or_404(job_id)
    
    template = BASE_TEMPLATE + '''
    {% block content %}
    <div class="card">
        <h1 style="color: #1e3a8a; margin-bottom: 1rem;">{{ job.title }}</h1>
        <p style="color: #64748b; margin-bottom: 1rem;">📍 {{ job.location }}</p>
        <div style="background: #f0f9ff; padding: 1rem; border-radius: 4px; margin-bottom: 2rem;">
            <strong style="color: #16a34a; font-size: 1.2rem;">💰 €{{ job.referral_bonus }} Referral-Bonus</strong>
        </div>
        
        <h3 style="margin-bottom: 1rem;">Stellenbeschreibung:</h3>
        <p style="line-height: 1.6; margin-bottom: 2rem;">{{ job.description }}</p>
        
        {% if session.user_id %}
            <a href="{{ url_for('submit_referral', job_id=job.id) }}" class="btn">Referral einreichen</a>
        {% else %}
            <a href="{{ url_for('login') }}" class="btn">Anmelden um Referral einzureichen</a>
        {% endif %}
    </div>
    {% endblock %}
    '''
    return render_template_string(template, job=job)

@app.route('/submit_referral/<int:job_id>', methods=['GET', 'POST'])
def submit_referral(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    job = JobListing.query.get_or_404(job_id)
    
    if request.method == 'POST':
        candidate_name = request.form['candidate_name']
        candidate_email = request.form['candidate_email']
        
        referral = Referral(
            job_id=job_id,
            referrer_id=session['user_id'],
            candidate_name=candidate_name,
            candidate_email=candidate_email
        )
        db.session.add(referral)
        db.session.commit()
        
        flash(f'Referral für {candidate_name} erfolgreich eingereicht!')
        return redirect(url_for('my_referrals'))
    
    template = BASE_TEMPLATE + '''
    {% block content %}
    <div class="card">
        <h1 style="margin-bottom: 2rem;">Referral einreichen</h1>
        <h2 style="color: #1e3a8a; margin-bottom: 1rem;">{{ job.title }}</h2>
        <p style="margin-bottom: 2rem;">💰 Referral-Bonus: <strong>€{{ job.referral_bonus }}</strong></p>
        
        <form method="POST">
            <div class="form-group">
                <label>Name des Kandidaten:</label>
                <input type="text" name="candidate_name" required>
            </div>
            <div class="form-group">
                <label>E-Mail des Kandidaten:</label>
                <input type="email" name="candidate_email" required>
            </div>
            <button type="submit" class="btn">Referral einreichen</button>
            <a href="{{ url_for('job_detail', job_id=job.id) }}" class="btn btn-secondary" style="margin-left: 10px;">Zurück</a>
        </form>
    </div>
    {% endblock %}
    '''
    return render_template_string(template, job=job)

@app.route('/my_referrals')
def my_referrals():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    referrals = db.session.query(Referral, JobListing).join(JobListing).filter(Referral.referrer_id == session['user_id']).all()
    
    template = BASE_TEMPLATE + '''
    {% block content %}
    <h1 style="margin-bottom: 2rem;">Meine Referrals</h1>
    
    {% if referrals %}
        <div class="card">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 2px solid #e5e7eb;">
                        <th style="text-align: left; padding: 12px;">Stelle</th>
                        <th style="text-align: left; padding: 12px;">Kandidat</th>
                        <th style="text-align: left; padding: 12px;">Status</th>
                        <th style="text-align: left; padding: 12px;">Bonus</th>
                        <th style="text-align: left; padding: 12px;">Datum</th>
                    </tr>
                </thead>
                <tbody>
                    {% for referral, job in referrals %}
                    <tr style="border-bottom: 1px solid #f3f4f6;">
                        <td style="padding: 12px;">{{ job.title }}</td>
                        <td style="padding: 12px;">{{ referral.candidate_name }}</td>
                        <td style="padding: 12px;">
                            <span style="padding: 4px 8px; border-radius: 4px; font-size: 12px; 
                                         background: {% if referral.status == 'hired' %}#dcfce7; color: #16a34a{% elif referral.status == 'rejected' %}#fef2f2; color: #dc2626{% else %}#fef3c7; color: #d97706{% endif %};">
                                {{ referral.status.title() }}
                            </span>
                        </td>
                        <td style="padding: 12px;">€{{ job.referral_bonus }}</td>
                        <td style="padding: 12px;">{{ referral.created_at.strftime('%d.%m.%Y') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <div class="card" style="text-align: center;">
            <h3 style="margin-bottom: 1rem;">Noch keine Referrals</h3>
            <p style="margin-bottom: 2rem;">Sie haben noch keine Referrals eingereicht.</p>
            <a href="{{ url_for('jobs') }}" class="btn">Stellen durchsuchen</a>
        </div>
    {% endif %}
    {% endblock %}
    '''
    return render_template_string(template, referrals=referrals)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sie wurden erfolgreich abgemeldet.')
    return redirect(url_for('index'))

# Initialisierung
def init_db():
    with app.app_context():
        db.create_all()
        
        # Admin-User erstellen falls nicht vorhanden
        if not User.query.filter_by(email='admin@argo-aviation.com').first():
            admin = User(
                first_name='Admin',
                last_name='User',
                email='admin@argo-aviation.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Beispiel-Jobs erstellen
        if JobListing.query.count() == 0:
            jobs = [
                JobListing(
                    title='Commercial Pilot',
                    description='Erfahrener Pilot für kommerzielle Flüge. Mindestens 3000 Flugstunden erforderlich. ATPL-Lizenz notwendig.',
                    location='Hamburg',
                    referral_bonus=2000.0
                ),
                JobListing(
                    title='Aircraft Maintenance Engineer',
                    description='Wartung und Reparatur von Flugzeugsystemen. EASA Part-66 Lizenz erforderlich.',
                    location='München',
                    referral_bonus=1500.0
                ),
                JobListing(
                    title='Flight Dispatcher',
                    description='Flugplanung und -überwachung. Erfahrung in der Luftfahrt erforderlich.',
                    location='Frankfurt',
                    referral_bonus=1200.0
                ),
                JobListing(
                    title='Cabin Crew Member',
                    description='Flugbegleiter für internationale Flüge. Mehrsprachigkeit von Vorteil.',
                    location='Berlin',
                    referral_bonus=800.0
                ),
                JobListing(
                    title='Aviation Safety Manager',
                    description='Sicherheitsmanagement in der Luftfahrt. SMS-Erfahrung erforderlich.',
                    location='Köln',
                    referral_bonus=1800.0
                )
            ]
            
            for job in jobs:
                db.session.add(job)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    # Azure App Service verwendet Port 8000
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # Für Azure App Service
    init_db()
