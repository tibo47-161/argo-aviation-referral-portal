from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.models import User, JobListing, Referral


api_bp = Blueprint('api', __name__)


def paginate_query(query, page_default: int = 1, per_page_default: int = 10):
    page = request.args.get('page', page_default, type=int)
    per_page = request.args.get('per_page', per_page_default, type=int)
    per_page = min(max(per_page, 1), 50)
    return query.paginate(page=page, per_page=per_page, error_out=False)


@api_bp.route('/users/profile', methods=['GET'])
@login_required
def get_profile():
    user: User = current_user
    return jsonify({
        'user_id': user.user_id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number,
        'is_active': user.is_active,
    })


@api_bp.route('/users/profile', methods=['PUT'])
@login_required
def update_profile():
    payload = request.get_json(silent=True) or {}
    allowed_fields = {'first_name', 'last_name', 'phone_number'}
    updated = False
    for key in allowed_fields:
        if key in payload:
            setattr(current_user, key, payload[key])
            updated = True
    if updated:
        db.session.commit()
    return jsonify({'message': 'Profile updated', 'updated': updated})


@api_bp.route('/jobs', methods=['GET'])
@login_required
def list_jobs():
    query = JobListing.query.filter_by(is_active=True)

    # Filters
    search = request.args.get('search', type=str)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(JobListing.title.ilike(like), JobListing.description.ilike(like)))

    location = request.args.get('location', type=str)
    if location:
        query = query.filter(JobListing.location.ilike(f"%{location}%"))

    employment_type = request.args.get('employment_type', type=str)
    if employment_type:
        query = query.filter(JobListing.employment_type == employment_type)

    # Sort
    sort_by = request.args.get('sort_by', 'posting_date')
    sort_order = request.args.get('sort_order', 'desc')
    sort_col = getattr(JobListing, sort_by, JobListing.posting_date)
    if sort_order == 'asc':
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    page = paginate_query(query)

    return jsonify({
        'jobs': [
            {
                'job_id': j.job_id,
                'title': j.title,
                'location': j.location,
                'employment_type': j.employment_type,
                'referral_bonus': float(j.referral_bonus) if j.referral_bonus is not None else None,
                'posting_date': j.posting_date.isoformat() if j.posting_date else None,
                'is_active': j.is_active,
            }
            for j in page.items
        ],
        'pagination': {
            'page': page.page,
            'per_page': page.per_page,
            'total': page.total,
            'pages': page.pages
        }
    })


@api_bp.route('/jobs/<job_id>', methods=['GET'])
@login_required
def get_job(job_id):
    job = JobListing.query.get_or_404(job_id)
    return jsonify({
        'job_id': job.job_id,
        'title': job.title,
        'location': job.location,
        'employment_type': job.employment_type,
        'referral_bonus': float(job.referral_bonus) if job.referral_bonus is not None else None,
        'description': job.description,
        'requirements': job.requirements,
        'posting_date': job.posting_date.isoformat() if job.posting_date else None,
        'expiry_date': job.expiry_date.isoformat() if job.expiry_date else None,
        'is_active': job.is_active,
    })


@api_bp.route('/referrals', methods=['GET'])
@login_required
def list_referrals():
    query = Referral.query.filter_by(referrer_id=current_user.user_id)
    page = paginate_query(query)
    return jsonify({
        'referrals': [
            {
                'referral_id': r.referral_id,
                'job_id': r.job_id,
                'job_title': r.job_listing.title if getattr(r, 'job_listing', None) else None,
                'applicant_name': r.applicant_name,
                'applicant_email': r.applicant_email,
                'status': r.status,
                'referral_date': r.referral_date.isoformat() if r.referral_date else None,
            }
            for r in page.items
        ],
        'pagination': {
            'page': page.page,
            'per_page': page.per_page,
            'total': page.total,
            'pages': page.pages
        }
    })


@api_bp.route('/referrals', methods=['POST'])
@login_required
def create_referral():
    payload = request.get_json(silent=True) or {}
    required = ['job_id', 'applicant_email', 'applicant_name']
    missing = [f for f in required if not payload.get(f)]
    if missing:
        return jsonify({'error': 'Validation error', 'missing': missing}), 400

    job = JobListing.query.get(payload['job_id'])
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    referral = Referral(
        referrer_id=current_user.user_id,
        job_id=job.job_id,
        applicant_email=payload['applicant_email'],
        applicant_name=payload['applicant_name'],
        status=payload.get('status', 'submitted'),
        notes=payload.get('notes'),
    )
    db.session.add(referral)
    db.session.commit()

    return jsonify({'message': 'Referral submitted', 'referral_id': referral.referral_id, 'status': referral.status}), 201


