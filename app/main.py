# app/main.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, JobListing, Referral

main_bp = Blueprint('main', __name__)

# Superadmin-Konfiguration (muss mit auth.py übereinstimmen)
SUPERADMIN_EMAIL = "tobi196183@gmail.com"

def is_superadmin(email):
    """Überprüft, ob die E-Mail-Adresse ein Superadmin ist"""
    return email.lower() == SUPERADMIN_EMAIL.lower()

def get_basic_stats():
    """Grundlegende Statistiken für das Dashboard"""
    try:
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_jobs': JobListing.query.count(),
            'active_jobs': JobListing.query.filter_by(is_active=True).count(),
            'total_referrals': Referral.query.count(),
            'successful_referrals': Referral.query.filter_by(status='hired').count() if hasattr(Referral, 'status') else 0,
        }
        return stats
    except Exception as e:
        # Fallback bei Datenbankfehlern
        return {
            'total_users': 0,
            'active_users': 0,
            'total_jobs': 0,
            'active_jobs': 0,
            'total_referrals': 0,
            'successful_referrals': 0,
        }

@main_bp.route('/')
def index():
    """Startseite - leitet angemeldete Benutzer zum Dashboard um"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Hauptdashboard mit benutzer- und rollenspezifischen Inhalten"""
    
    # Basis-Dashboard-Daten
    context = {
        'user': current_user,
        'user_referrals_count': len(current_user.referrals_made) if current_user.referrals_made else 0,
    }
    
    # Erweiterte Daten für Superadmin
    if is_superadmin(current_user.email):
        try:
            context.update({
                'system_stats': get_basic_stats(),
                'is_superadmin': True
            })
        except Exception as e:
            # Fallback bei Fehlern
            context['is_superadmin'] = True
            context['system_stats'] = {}
    
    return render_template('dashboard.html', **context)

@main_bp.route('/profile')
@login_required
def profile():
    """Benutzerprofil-Seite"""
    return render_template('profile.html', user=current_user)

@main_bp.route('/jobs')
@login_required
def jobs():
    """Stellenausschreibungen anzeigen"""
    try:
        page = request.args.get('page', 1, type=int)
        jobs = JobListing.query.filter_by(is_active=True).paginate(
            page=page, per_page=10, error_out=False
        )
        return render_template('jobs.html', jobs=jobs)
    except Exception as e:
        flash('Fehler beim Laden der Stellenausschreibungen.', 'danger')
        return render_template('jobs.html', jobs=None)

@main_bp.route('/my-referrals')
@login_required
def my_referrals():
    """Benutzer-spezifische Referrals anzeigen"""
    try:
        page = request.args.get('page', 1, type=int)
        referrals = Referral.query.filter_by(referrer_id=current_user.user_id).paginate(
            page=page, per_page=10, error_out=False
        )
        return render_template('my_referrals.html', referrals=referrals)
    except Exception as e:
        flash('Fehler beim Laden der Referrals.', 'danger')
        return render_template('my_referrals.html', referrals=None)

# Superadmin-spezifische Routen
@main_bp.route('/admin')
@login_required
def admin_dashboard():
    """Admin-Dashboard - nur für Superadmin"""
    if not is_superadmin(current_user.email):
        flash('Zugriff verweigert. Superadmin-Berechtigung erforderlich.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        stats = get_basic_stats()
        return render_template('admin_dashboard.html', stats=stats)
    except Exception as e:
        flash('Fehler beim Laden des Admin-Dashboards.', 'danger')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/admin/users')
@login_required
def admin_users():
    """Benutzerverwaltung - nur für Superadmin"""
    if not is_superadmin(current_user.email):
        flash('Zugriff verweigert. Superadmin-Berechtigung erforderlich.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        page = request.args.get('page', 1, type=int)
        users = User.query.paginate(page=page, per_page=20, error_out=False)
        return render_template('admin_users.html', users=users)
    except Exception as e:
        flash('Fehler beim Laden der Benutzerliste.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

@main_bp.route('/admin/jobs')
@login_required
def admin_jobs():
    """Job-Verwaltung - nur für Superadmin"""
    if not is_superadmin(current_user.email):
        flash('Zugriff verweigert. Superadmin-Berechtigung erforderlich.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        page = request.args.get('page', 1, type=int)
        jobs = JobListing.query.paginate(page=page, per_page=20, error_out=False)
        return render_template('admin_jobs.html', jobs=jobs)
    except Exception as e:
        flash('Fehler beim Laden der Job-Liste.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

# API-Endpunkte für AJAX-Requests
@main_bp.route('/api/stats')
@login_required
def api_stats():
    """API-Endpunkt für Dashboard-Statistiken"""
    if not is_superadmin(current_user.email):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        return jsonify(get_basic_stats())
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/api/user/<user_id>/toggle-status', methods=['POST'])
@login_required
def api_toggle_user_status(user_id):
    """API-Endpunkt zum Aktivieren/Deaktivieren von Benutzern"""
    if not is_superadmin(current_user.email):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_status': user.is_active,
            'message': f'Benutzer {"aktiviert" if user.is_active else "deaktiviert"}'
        })
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# Template-Kontext-Prozessoren
@main_bp.app_context_processor
def inject_global_vars():
    """Globale Variablen für alle Templates"""
    return {
        'current_user': current_user,
        'is_superadmin': is_superadmin(current_user.email) if current_user.is_authenticated else False
    }

# Fehlerbehandlung
@main_bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@main_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
