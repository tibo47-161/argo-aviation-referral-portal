"""
Argo Aviation Referral Portal - Final Version with Correct Colors
A Flask application for the aviation referral system with proper Argo branding
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'argo-aviation-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///argo_referral.db'
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

# HTML Template with Correct Argo Aviation Colors
HTML_TEMPLATE = '''
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
            transform: translateY(-1px);
        }
        .main { padding: 2rem 0; min-height: calc(100vh - 200px); }
        .card { 
            background: white; 
            padding: 2rem; 
            border-radius: 12px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
            margin-bottom: 2rem; 
            border-left: 4px solid #DAA520;
        }
        .btn { 
            display: inline-block; 
            padding: 12px 24px; 
            background: linear-gradient(135deg, #DAA520, #B8860B); 
            color: #2F2F2F; 
            text-decoration: none; 
            border-radius: 6px; 
            border: none; 
            cursor: pointer; 
            font-size: 14px; 
            font-weight: 600;
            transition: all 0.3s ease; 
            box-shadow: 0 2px 10px rgba(218,165,32,0.3);
        }
        .btn:hover { 
            background: linear-gradient(135deg, #B8860B, #DAA520); 
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(218,165,32,0.4);
        }
        .btn-secondary { 
            background: linear-gradient(135deg, #4A4A4A, #2F2F2F); 
            color: #DAA520;
        }
        .btn-secondary:hover { 
            background: linear-gradient(135deg, #2F2F2F, #4A4A4A); 
            color: #F4D03F;
        }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600; 
            color: #2F2F2F;
        }
        .form-group input, .form-group textarea, .form-group select { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e0e0e0; 
            border-radius: 6px; 
            font-size: 14px; 
            transition: border-color 0.3s ease;
        }
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
            outline: none;
            border-color: #DAA520;
            box-shadow: 0 0 0 3px rgba(218,165,32,0.1);
        }
        .alert { 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 1.5rem; 
            font-weight: 500;
        }
        .alert-success { 
            background: #f0f9e8; 
            border: 2px solid #4ade80; 
            color: #166534; 
        }
        .alert-error { 
            background: #fef2f2; 
            border: 2px solid #ef4444; 
            color: #dc2626; 
        }
        .footer { 
            background: #2F2F2F; 
            color: #DAA520; 
            text-align: center; 
            padding: 2rem 0; 
            border-top: 3px solid #DAA520;
        }
        .job-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); 
            gap: 2rem; 
        }
        .job-card { 
            background: white; 
            padding: 2rem; 
            border-radius: 12px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
            border-left: 4px solid #DAA520;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .job-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        .job-title { 
            color: #2F2F2F; 
            font-size: 1.3rem; 
            font-weight: 700; 
            margin-bottom: 0.5rem; 
        }
        .job-company { 
            color: #DAA520; 
            font-weight: 600;
            margin-bottom: 1rem; 
        }
        .job-bonus {
            background: linear-gradient(135deg, #DAA520, #B8860B);
            color: #2F2F2F;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            display: inline-block;
            margin: 10px 0;
        }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 2rem; 
            margin-bottom: 3rem; 
        }
        .stat-card { 
            background: white; 
            padding: 2rem; 
            border-radius: 12px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
            text-align: center; 
            border-left: 4px solid #DAA520;
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-3px);
        }
        .stat-number { 
            font-size: 3rem; 
            font-weight: 900; 
            color: #DAA520; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .stat-label { 
            color: #2F2F2F; 
            margin-top: 10px; 
            font-weight: 600;
            font-size: 1.1rem;
        }
        .welcome-section {
            background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%);
            color: #2F2F2F;
            padding: 4rem 0;
            text-align: center;
            margin-bottom: 3rem;
            border-radius: 12px;
        }
        .welcome-section h2 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .welcome-section p {
            font-size: 1.2rem;
            font-weight: 500;
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>✈️ Argo Aviation Referral Portal</h1>
        </div>
    </header>
    
    {% if session.user_id %}
    <nav class="nav">
        <div class="container">
            <a href="{{ url_for('dashboard') }}" {% if request.endpoint == 'dashboard' %}class="active"{% endif %}>Dashboard</a>
            <a href="{{ url_for('jobs') }}" {% if request.endpoint == 'jobs' %}class="active"{% endif %}>Jobs</a>
            <a href="{{ url_for('my_referrals') }}" {% if request.endpoint == 'my_referrals' %}class="active"{% endif %}>Meine Referrals</a>
            <a href="{{ url_for('logout') }}">Abmelden</a>
        </div>
    </nav>
    {% endif %}

    <main class="main">
        <div class="container">
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-success">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            {{ content }}
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
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    
    content = '''
    <div class="welcome-section">
        <h2>Willkommen bei Argo Aviation</h2>
        <p>Ihr Partner für Luftfahrt-Recruiting und Referral-Programme</p>
        <a href="{{ url_for('login') }}" class="btn">Anmelden</a>
        <a href="{{ url_for('register') }}" class="btn btn-secondary">Registrieren</a>
    </div>
    '''
    return render_template_string(HTML_TEMPLATE.replace('{{ content }}', content), title="Willkommen")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('Diese E-Mail-Adresse ist bereits registriert.')
            return redirect(url_for('register'))
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.')
        return redirect(url_for('login'))
    
    content = '''
    <div class="card">
        <h2>Registrieren</h2>
        <form method="POST">
            <div class="form-group">
                <label>Name:</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>E-Mail:</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Passwort:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Registrieren</button>
            <a href="{{ url_for('login') }}" class="btn btn-secondary">Bereits registriert? Anmelden</a>
        </form>
    </div>
    '''
    return render_template_string(HTML_TEMPLATE.replace('{{ content }}', content), title="Registrieren")

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
            return redirect(url_for('dashboard'))
        else:
            flash('Ungültige Anmeldedaten.')
    
    content = '''
    <div class="card">
        <h2>Anmelden</h2>
        <form method="POST">
            <div class="form-group">
                <label>E-Mail:</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Passwort:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Anmelden</button>
            <a href="{{ url_for('register') }}" class="btn btn-secondary">Noch kein Konto? Registrieren</a>
        </form>
    </div>
    '''
    return render_template_string(HTML_TEMPLATE.replace('{{ content }}', content), title="Anmelden")

@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    total_jobs = Job.query.filter_by(is_active=True).count()
    total_referrals = Referral.query.count()
    user_referrals = Referral.query.filter_by(referrer_id=session['user_id']).count()
    
    content = f'''
    <h2>Willkommen zurück, {session['user_name']}!</h2>
    
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
            <div class="stat-number">{user_referrals}</div>
            <div class="stat-label">Meine Referrals</div>
        </div>
    </div>
    
    <div class="card">
        <h3>Schnellzugriff</h3>
        <a href="{{ url_for('jobs') }}" class="btn">Jobs ansehen</a>
        <a href="{{ url_for('my_referrals') }}" class="btn btn-secondary">Meine Referrals</a>
    </div>
    '''
    return render_template_string(HTML_TEMPLATE.replace('{{ content }}', content), title="Dashboard")

@app.route('/jobs')
def jobs():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    jobs = Job.query.filter_by(is_active=True).all()
    
    jobs_html = ''
    for job in jobs:
        jobs_html += f'''
        <div class="job-card">
            <div class="job-title">{job.title}</div>
            <div class="job-company">{job.company} - {job.location}</div>
            <p>{job.description[:150]}...</p>
            <div class="job-bonus">Bonus: €{job.bonus_amount:.0f}</div>
            <a href="{{ url_for('job_detail', job_id={job.id}) }}" class="btn">Details</a>
        </div>
        '''
    
    content = f'''
    <h2>Aktuelle Stellenausschreibungen</h2>
    <div class="job-grid">
        {jobs_html}
    </div>
    '''
    return render_template_string(HTML_TEMPLATE.replace('{{ content }}', content), title="Jobs")

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    job = Job.query.get_or_404(job_id)
    
    content = f'''
    <div class="card">
        <h2>{job.title}</h2>
        <p><strong>{job.company} - {job.location}</strong></p>
        
        <h3>Beschreibung</h3>
        <p>{job.description}</p>
        
        <h3>Anforderungen</h3>
        <p>{job.requirements}</p>
        
        <div class="job-bonus">
            <strong>Referral-Bonus</strong><br>
            €{job.bonus_amount:.0f}
        </div>
        
        <a href="{{ url_for('submit_referral', job_id={job.id}) }}" class="btn">Referral einreichen</a>
        <a href="{{ url_for('jobs') }}" class="btn btn-secondary">Zurück zu Jobs</a>
    </div>
    '''
    return render_template_string(HTML_TEMPLATE.replace('{{ content }}', content), title=job.title)

@app.route('/submit_referral/<int:job_id>', methods=['GET', 'POST'])
def submit_referral(job_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        referral = Referral(
            job_id=job_id,
            referrer_id=session['user_id'],
            candidate_name=request.form['candidate_name'],
            candidate_email=request.form['candidate_email'],
            candidate_phone=request.form.get('candidate_phone', ''),
            notes=request.form.get('notes', '')
        )
        db.session.add(referral)
        db.session.commit()
        
        flash('Referral erfolgreich eingereicht!')
        return redirect(url_for('my_referrals'))
    
    content = f'''
    <div class="card">
        <h2>Referral einreichen für: {job.title}</h2>
        <form method="POST">
            <div class="form-group">
                <label>Kandidat Name:</label>
                <input type="text" name="candidate_name" required>
            </div>
            <div class="form-group">
                <label>Kandidat E-Mail:</label>
                <input type="email" name="candidate_email" required>
            </div>
            <div class="form-group">
                <label>Kandidat Telefon:</label>
                <input type="tel" name="candidate_phone">
            </div>
            <div class="form-group">
                <label>Notizen:</label>
                <textarea name="notes" rows="4"></textarea>
            </div>
            <button type="submit" class="btn">Referral einreichen</button>
            <a href="{{ url_for('job_detail', job_id={job.id}) }}" class="btn btn-secondary">Zurück</a>
        </form>
    </div>
    '''
    return render_template_string(HTML_TEMPLATE.replace('{{ content }}', content), title="Referral einreichen")

@app.route('/my_referrals')
def my_referrals():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    referrals = db.session.query(Referral, Job).join(Job).filter(Referral.referrer_id == session['user_id']).all()
    
    referrals_html = ''
    for referral, job in referrals:
        status_color = '#4ade80' if referral.status == 'approved' else '#f59e0b' if referral.status == 'pending' else '#ef4444'
        referrals_html += f'''
        <div class="job-card">
            <div class="job-title">{job.title}</div>
            <div class="job-company">{job.company}</div>
            <p><strong>Kandidat:</strong> {referral.candidate_name}</p>
            <p><strong>E-Mail:</strong> {referral.candidate_email}</p>
            <p><strong>Status:</strong> <span style="color: {status_color}; font-weight: bold;">{referral.status}</span></p>
            <p><strong>Eingereicht:</strong> {referral.created_at.strftime('%d.%m.%Y')}</p>
        </div>
        '''
    
    if not referrals_html:
        referrals_html = '<div class="card"><p>Sie haben noch keine Referrals eingereicht.</p></div>'
    
    content = f'''
    <h2>Meine Referrals</h2>
    <div class="job-grid">
        {referrals_html}
    </div>
    '''
    return render_template_string(HTML_TEMPLATE.replace('{{ content }}', content), title="Meine Referrals")

@app.route('/logout')
def logout():
    session.clear()
    flash('Erfolgreich abgemeldet!')
    return redirect(url_for('index'))

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if admin user exists
        if not User.query.filter_by(email='admin@argo-aviation.com').first():
            admin = User(
                name='Admin',
                email='admin@argo-aviation.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
        
        # Check if jobs exist
        if Job.query.count() == 0:
            jobs = [
                Job(
                    title='Pilot (A320)',
                    company='Argo Aviation GmbH',
                    location='Frankfurt am Main',
                    description='Wir suchen einen erfahrenen Piloten für unsere A320 Flotte. Sie werden nationale und internationale Flüge durchführen.',
                    requirements='ATPL Lizenz, A320 Type Rating, Mindestens 3000 Flugstunden',
                    bonus_amount=2000.0
                ),
                Job(
                    title='Flugbegleiter/in',
                    company='Argo Aviation GmbH',
                    location='München',
                    description='Freundliche und professionelle Flugbegleiter für unsere Kabinencrew gesucht.',
                    requirements='Abgeschlossene Flugbegleiter-Ausbildung, Mehrsprachigkeit von Vorteil',
                    bonus_amount=1000.0
                ),
                Job(
                    title='Flugzeugmechaniker',
                    company='Argo Aviation GmbH',
                    location='Hamburg',
                    description='Wartung und Instandhaltung unserer Flugzeugflotte.',
                    requirements='Abgeschlossene Ausbildung als Flugzeugmechaniker, EASA Lizenz',
                    bonus_amount=1500.0
                )
            ]
            for job in jobs:
                db.session.add(job)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)), debug=False)
