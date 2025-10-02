#!/usr/bin/env python3
"""
Argo Aviation Referral Portal - Production Version
A Flask application for the aviation referral system
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'argo-aviation-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///argo_referral.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    salary_range = db.Column(db.String(100))
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

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Argo Aviation Referral Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #334155; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .header { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header h1 { font-size: 1.8rem; font-weight: 600; }
        .nav { display: flex; gap: 1rem; margin-top: 0.5rem; }
        .nav a { color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 4px; transition: background 0.3s; }
        .nav a:hover { background: rgba(255,255,255,0.2); }
        .main { padding: 2rem 0; min-height: calc(100vh - 200px); }
        .card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .btn { display: inline-block; padding: 12px 24px; background: #1e3a8a; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; font-size: 14px; transition: background 0.3s; }
        .btn:hover { background: #1e40af; }
        .btn-secondary { background: #64748b; }
        .btn-secondary:hover { background: #475569; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 14px; }
        .alert { padding: 12px; border-radius: 4px; margin-bottom: 1rem; }
        .alert-success { background: #dcfce7; border: 1px solid #16a34a; color: #15803d; }
        .alert-error { background: #fef2f2; border: 1px solid #dc2626; color: #dc2626; }
        .footer { background: #1e3a8a; color: white; text-align: center; padding: 1rem 0; }
        .job-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
        .job-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .job-title { color: #1e3a8a; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem; }
        .job-company { color: #64748b; margin-bottom: 1rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .stat-number { font-size: 2rem; font-weight: bold; color: #1e3a8a; }
        .stat-label { color: #64748b; margin-top: 5px; }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>🛩️ Argo Aviation Referral Portal</h1>
            {% if session.user_id %}
            <nav class="nav">
                <a href="/dashboard">Dashboard</a>
                <a href="/jobs">Jobs</a>
                <a href="/my_referrals">Meine Referrals</a>
                <a href="/logout">Abmelden</a>
            </nav>
            {% endif %}
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
            
            {{ content|safe }}
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

def render_page(title, content):
    """Render a page with the given title and content"""
    return render_template_string(HTML_TEMPLATE, title=title, content=content)

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    
    content = '''
    <div class="card" style="text-align: center; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #1e3a8a; margin-bottom: 1rem;">Willkommen bei Argo Aviation</h1>
        <p style="font-size: 1.1rem; margin-bottom: 2rem; color: #64748b;">
            Ihr Partner für Luftfahrt-Recruiting und Referral-Programme
        </p>
        <div style="display: flex; gap: 1rem; justify-content: center;">
            <a href="/login" class="btn">Anmelden</a>
            <a href="/register" class="btn btn-secondary">Registrieren</a>
        </div>
    </div>
    '''
    return render_page('Willkommen', content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            flash('Erfolgreich angemeldet!')
            return redirect('/dashboard')
        else:
            flash('Ungültige Anmeldedaten!')
    
    content = '''
    <div class="card" style="max-width: 400px; margin: 0 auto;">
        <h2 style="text-align: center; margin-bottom: 2rem; color: #1e3a8a;">Anmelden</h2>
        <form method="POST">
            <div class="form-group">
                <label for="email">E-Mail:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Passwort:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn" style="width: 100%;">Anmelden</button>
        </form>
        <p style="text-align: center; margin-top: 1rem;">
            <a href="/register">Noch kein Konto? Registrieren</a>
        </p>
    </div>
    '''
    return render_page('Anmelden', content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('E-Mail bereits registriert!')
        else:
            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.')
            return redirect('/login')
    
    content = '''
    <div class="card" style="max-width: 400px; margin: 0 auto;">
        <h2 style="text-align: center; margin-bottom: 2rem; color: #1e3a8a;">Registrieren</h2>
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
            <button type="submit" class="btn" style="width: 100%;">Registrieren</button>
        </form>
        <p style="text-align: center; margin-top: 1rem;">
            <a href="/login">Bereits registriert? Anmelden</a>
        </p>
    </div>
    '''
    return render_page('Registrieren', content)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    total_jobs = Job.query.filter_by(is_active=True).count()
    total_referrals = Referral.query.count()
    my_referrals = Referral.query.filter_by(referrer_id=session['user_id']).count()
    
    content = f'''
    <h1 style="margin-bottom: 2rem;">Willkommen zurück, {session['user_name']}!</h1>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{total_jobs}</div>
            <div class="stat-label">Aktive Jobs</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{total_referrals}</div>
            <div class="stat-label">Gesamt Referrals</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{my_referrals}</div>
            <div class="stat-label">Meine Referrals</div>
        </div>
    </div>
    
    <div style="display: flex; gap: 1rem; margin-bottom: 2rem;">
        <a href="/jobs" class="btn">Jobs ansehen</a>
        <a href="/my_referrals" class="btn btn-secondary">Meine Referrals</a>
    </div>
    '''
    return render_page('Dashboard', content)

@app.route('/jobs')
def jobs():
    if 'user_id' not in session:
        return redirect('/login')
    
    jobs_list = Job.query.filter_by(is_active=True).all()
    
    jobs_html = ''
    for job in jobs_list:
        jobs_html += f'''
        <div class="job-card">
            <div class="job-title">{job.title}</div>
            <div class="job-company">{job.company} - {job.location}</div>
            <p style="margin-bottom: 1rem;">{job.description[:150]}...</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #16a34a; font-weight: 600;">Bonus: €{job.bonus_amount}</span>
                <a href="/job/{job.id}" class="btn">Details</a>
            </div>
        </div>
        '''
    
    content = f'''
    <h1 style="margin-bottom: 2rem;">Aktuelle Stellenausschreibungen</h1>
    <div class="job-grid">
        {jobs_html}
    </div>
    '''
    return render_page('Jobs', content)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    job = Job.query.get_or_404(job_id)
    
    content = f'''
    <div class="card">
        <h1 style="color: #1e3a8a; margin-bottom: 1rem;">{job.title}</h1>
        <p style="font-size: 1.1rem; color: #64748b; margin-bottom: 2rem;">{job.company} - {job.location}</p>
        
        <h3 style="margin-bottom: 1rem;">Beschreibung</h3>
        <p style="margin-bottom: 2rem;">{job.description}</p>
        
        <h3 style="margin-bottom: 1rem;">Anforderungen</h3>
        <p style="margin-bottom: 2rem;">{job.requirements}</p>
        
        <div style="background: #f0f9ff; padding: 1rem; border-radius: 4px; margin-bottom: 2rem;">
            <h4 style="color: #1e3a8a;">Referral-Bonus</h4>
            <p style="font-size: 1.2rem; font-weight: 600; color: #16a34a;">€{job.bonus_amount}</p>
        </div>
        
        <a href="/submit_referral/{job.id}" class="btn">Referral einreichen</a>
        <a href="/jobs" class="btn btn-secondary">Zurück zu Jobs</a>
    </div>
    '''
    return render_page(job.title, content)

@app.route('/submit_referral/<int:job_id>', methods=['GET', 'POST'])
def submit_referral(job_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        referral = Referral(
            job_id=job_id,
            referrer_id=session['user_id'],
            candidate_name=request.form['candidate_name'],
            candidate_email=request.form['candidate_email'],
            candidate_phone=request.form['candidate_phone'],
            notes=request.form['notes']
        )
        db.session.add(referral)
        db.session.commit()
        flash('Referral erfolgreich eingereicht!')
        return redirect('/my_referrals')
    
    content = f'''
    <div class="card">
        <h1 style="margin-bottom: 2rem;">Referral einreichen</h1>
        <h3 style="color: #1e3a8a; margin-bottom: 1rem;">Position: {job.title}</h3>
        
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
                <label for="candidate_phone">Telefon des Kandidaten:</label>
                <input type="tel" id="candidate_phone" name="candidate_phone">
            </div>
            <div class="form-group">
                <label for="notes">Zusätzliche Notizen:</label>
                <textarea id="notes" name="notes" rows="4"></textarea>
            </div>
            <button type="submit" class="btn">Referral einreichen</button>
            <a href="/job/{job.id}" class="btn btn-secondary">Abbrechen</a>
        </form>
    </div>
    '''
    return render_page('Referral einreichen', content)

@app.route('/my_referrals')
def my_referrals():
    if 'user_id' not in session:
        return redirect('/login')
    
    referrals = db.session.query(Referral, Job).join(Job).filter(Referral.referrer_id == session['user_id']).all()
    
    referrals_html = ''
    for referral, job in referrals:
        status_color = {'pending': '#f59e0b', 'approved': '#16a34a', 'rejected': '#dc2626'}.get(referral.status, '#64748b')
        referrals_html += f'''
        <div class="card">
            <h3 style="color: #1e3a8a;">{job.title}</h3>
            <p><strong>Kandidat:</strong> {referral.candidate_name} ({referral.candidate_email})</p>
            <p><strong>Status:</strong> <span style="color: {status_color}; font-weight: 600;">{referral.status}</span></p>
            <p><strong>Eingereicht:</strong> {referral.created_at.strftime('%d.%m.%Y')}</p>
        </div>
        '''
    
    if not referrals_html:
        referrals_html = '<p>Sie haben noch keine Referrals eingereicht.</p>'
    
    content = f'''
    <h1 style="margin-bottom: 2rem;">Meine Referrals</h1>
    {referrals_html}
    <a href="/jobs" class="btn">Neue Referrals einreichen</a>
    '''
    return render_page('Meine Referrals', content)

@app.route('/logout')
def logout():
    session.clear()
    flash('Erfolgreich abgemeldet!')
    return redirect('/')

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(email='admin@argo-aviation.com').first():
            admin = User(
                name='Admin',
                email='admin@argo-aviation.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
        
        # Create sample jobs if not exist
        if Job.query.count() == 0:
            jobs = [
                Job(
                    title='Pilot (A320)',
                    company='Argo Aviation GmbH',
                    location='Frankfurt am Main',
                    description='Wir suchen einen erfahrenen Piloten für unsere A320 Flotte. Sie werden nationale und internationale Flüge durchführen.',
                    requirements='ATPL Lizenz, A320 Type Rating, Mindestens 3000 Flugstunden',
                    salary_range='€80.000 - €120.000',
                    bonus_amount=2000.0
                ),
                Job(
                    title='Flugbegleiter/in',
                    company='Argo Aviation GmbH',
                    location='München',
                    description='Freundliche und professionelle Flugbegleiter für unsere Kabinencrew gesucht.',
                    requirements='Abgeschlossene Flugbegleiter-Ausbildung, Deutsch und Englisch fließend',
                    salary_range='€35.000 - €45.000',
                    bonus_amount=1000.0
                ),
                Job(
                    title='Flugzeugmechaniker',
                    company='Argo Aviation GmbH',
                    location='Hamburg',
                    description='Wartung und Instandhaltung unserer Flugzeugflotte.',
                    requirements='Ausbildung als Flugzeugmechaniker, EASA Part-66 Lizenz',
                    salary_range='€50.000 - €70.000',
                    bonus_amount=1500.0
                )
            ]
            for job in jobs:
                db.session.add(job)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # For production deployment
    init_db()
