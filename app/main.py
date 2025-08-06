# app/main.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, JobListing, Referral, get_system_stats, get_recent_activity

main_bp = Blueprint('main', __name__)

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
    # Aktualisiere das letzte Login-Datum
    if hasattr(current_user, 'update_last_login'):
        current_user.update_last_login()
    
    # Basis-Dashboard-Daten
    context = {
        'user': current_user,
        'user_referrals_count': len(current_user.referrals_made) if current_user.referrals_made else 0,
        'active_jobs_count': JobListing.query.filter_by(is_active=True).count()
    }
    
    # Erweiterte Daten für Superadmin
    if hasattr(current_user, 'is_superadmin') and current_user.is_superadmin:
        context.update({
            'system_stats': get_system_stats(),
            'recent_activity': get_recent_activity(5),
            'is_superadmin': True
        })
    
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
    page = request.args.get('page', 1, type=int)
    jobs = JobListing.query.filter_by(is_active=True).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('jobs.html', jobs=jobs)

@main_bp.route('/my-referrals')
@login_required
def my_referrals():
    """Benutzer-spezifische Referrals anzeigen"""
    page = request.args.get('page', 1, type=int)
    referrals = Referral.query.filter_by(referrer_id=current_user.user_id).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('my_referrals.html', referrals=referrals)

# Superadmin-spezifische Routen
@main_bp.route('/admin')
@login_required
def admin_dashboard():
    """Admin-Dashboard - nur für Superadmin"""
    if not (hasattr(current_user, 'is_superadmin') and current_user.is_superadmin):
        flash('Zugriff verweigert. Superadmin-Berechtigung erforderlich.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    stats = get_system_stats()
    recent_activity = get_recent_activity(10)
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         recent_activity=recent_activity)

@main_bp.route('/admin/users')
@login_required
def admin_users():
    """Benutzerverwaltung - nur für Superadmin"""
    if not (hasattr(current_user, 'is_superadmin') and current_user.is_superadmin):
        flash('Zugriff verweigert. Superadmin-Berechtigung erforderlich.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin_users.html', users=users)

@main_bp.route('/admin/jobs')
@login_required
def admin_jobs():
    """Job-Verwaltung - nur für Superadmin"""
    if not (hasattr(current_user, 'is_superadmin') and current_user.is_superadmin):
        flash('Zugriff verweigert. Superadmin-Berechtigung erforderlich.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    jobs = JobListing.query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin_jobs.html', jobs=jobs)

# API-Endpunkte für AJAX-Requests
@main_bp.route('/api/stats')
@login_required
def api_stats():
    """API-Endpunkt für Dashboard-Statistiken"""
    if not (hasattr(current_user, 'is_superadmin') and current_user.is_superadmin):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(get_system_stats())

@main_bp.route('/api/user/<user_id>/toggle-status', methods=['POST'])
@login_required
def api_toggle_user_status(user_id):
    """API-Endpunkt zum Aktivieren/Deaktivieren von Benutzern"""
    if not (hasattr(current_user, 'is_superadmin') and current_user.is_superadmin):
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    return jsonify({
        'success': True,
        'new_status': user.is_active,
        'message': f'Benutzer {"aktiviert" if user.is_active else "deaktiviert"}'
    })

# Template-Kontext-Prozessoren
@main_bp.app_context_processor
def inject_global_vars():
    """Globale Variablen für alle Templates"""
    return {
        'current_user': current_user,
        'is_superadmin': (hasattr(current_user, 'is_superadmin') and 
                         current_user.is_superadmin) if current_user.is_authenticated else False
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
