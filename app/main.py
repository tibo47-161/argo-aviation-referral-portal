import logging
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, JobListing, Referral

main_bp = Blueprint('main', __name__)

logging.basicConfig(level=logging.DEBUG)

SUPERADMIN_EMAIL = "tobi196183@gmail.com"

def is_superadmin(email):
    return email.lower() == SUPERADMIN_EMAIL.lower()

def get_basic_stats():
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
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    context = {
        'user': current_user,
        'user_referrals_count': len(current_user.referrals_made) if current_user.referrals_made else 0,
    }
    if is_superadmin(current_user.email):
        try:
            context.update({
                'system_stats': get_basic_stats(),
                'is_superadmin': True
            })
        except Exception as e:
            context['is_superadmin'] = True
            context['system_stats'] = {}
    return render_template('dashboard.html', **context)

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main_bp.route('/jobs')
@login_required
def jobs():
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        location = request.args.get('location', '')
        query = JobListing.query.filter_by(is_active=True)
        if search:
            query = query.filter(JobListing.title.ilike(f'%{search}%'))
        if location:
            query = query.filter(JobListing.location.ilike(f'%{location}%'))
        jobs = query.order_by(JobListing.posting_date.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        return render_template('jobs.html', jobs=jobs, search=search, location=location)
    except Exception as e:
        flash('Fehler beim Laden der Stellenausschreibungen.', 'danger')
        return render_template('jobs.html', jobs=None, search='', location='')

@main_bp.route('/jobs/<job_id>')
@login_required
def job_detail(job_id):
    try:
        job = JobListing.query.get_or_404(job_id)
        if not job.is_active:
            flash('Diese Stellenausschreibung ist nicht mehr aktiv.', 'warning')
            return redirect(url_for('main.jobs'))
        return render_template('job_detail.html', job=job)
    except Exception as e:
        flash('Fehler beim Laden der Job-Details.', 'danger')
        return redirect(url_for('main.jobs'))

@main_bp.route('/jobs/<job_id>/submit-referral', methods=['GET', 'POST'])
@login_required
def submit_referral(job_id):
    logging.debug(f"Accessing submit_referral for job_id: {job_id} with method: {request.method}")
    try:
        job = JobListing.query.get_or_404(job_id)
        if not job.is_active:
            flash('Diese Stellenausschreibung ist nicht mehr aktiv.', 'warning')
            return redirect(url_for('main.jobs'))
        
        if request.method == 'POST':
            logging.debug(f"POST request form data: {request.form}")
            logging.debug(f"POST request files: {request.files}")
            form_data = {
                'applicant_name': request.form.get('applicant_name', '').strip(),
                'applicant_email': request.form.get('applicant_email', '').strip(),
                'applicant_phone': request.form.get('applicant_phone', '').strip(),
                'cover_letter': request.form.get('cover_letter', '').strip(),
                'notes': request.form.get('notes', '').strip(),
            }
            
            if not form_data['applicant_name'] or not form_data['applicant_email']:
                logging.debug("Validation failed: Applicant name or email is missing.")
                flash('Name und E-Mail des Bewerbers sind erforderlich.', 'error')
                return render_template('submit_referral.html', job=job, form_data=form_data)
            
            resume_file = request.files.get('resume')
            if not resume_file or resume_file.filename == '':
                logging.debug("Validation failed: Resume file is missing.")
                flash('Bitte laden Sie einen Lebenslauf hoch.', 'error')
                return render_template('submit_referral.html', job=job, form_data=form_data)
            
            referral = Referral(
                referrer_id=current_user.user_id,
                job_id=job.job_id,
                applicant_name=form_data['applicant_name'],
                applicant_email=form_data['applicant_email'],
                applicant_phone=form_data['applicant_phone'] or None,
                cover_letter=form_data['cover_letter'] or None,
                notes=form_data['notes'] or None,
                status='submitted'
            )
            
            db.session.add(referral)
            db.session.commit()
            
            flash('Referral erfolgreich eingereicht!', 'success')
            logging.debug("Referral submitted successfully. Redirecting to my_referrals.")
            return redirect(url_for('main.my_referrals'))
        
        return render_template('submit_referral.html', job=job, form_data=None)
        
    except Exception as e:
        logging.error(f"Error in submit_referral: {e}", exc_info=True)
        flash('Fehler beim Einreichen des Referrals.', 'danger')
        return redirect(url_for('main.job_detail', job_id=job_id))

@main_bp.route('/my-referrals')
@login_required
def my_referrals():
    try:
        page = request.args.get('page', 1, type=int)
        referrals = Referral.query.filter_by(referrer_id=current_user.user_id).paginate(
            page=page, per_page=10, error_out=False
        )
        return render_template('my_referrals.html', referrals=referrals)
    except Exception as e:
        flash('Fehler beim Laden der Referrals.', 'danger')
        return render_template('my_referrals.html', referrals=None)

@main_bp.route('/admin')
@login_required
def admin_dashboard():
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

@main_bp.route('/api/stats')
@login_required
def api_stats():
    if not is_superadmin(current_user.email):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        return jsonify(get_basic_stats())
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/api/user/<user_id>/toggle-status', methods=['POST'])
@login_required
def api_toggle_user_status(user_id):
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

@main_bp.app_context_processor
def inject_global_vars():
    return {
        'current_user': current_user,
        'is_superadmin': is_superadmin(current_user.email) if current_user.is_authenticated else False
    }

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

