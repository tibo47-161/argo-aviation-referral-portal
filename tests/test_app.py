import pytest
import io
from app import create_app, db
from app.models import User, JobListing
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_full_user_flow(client, app):
    # Step 1: User Registration
    reg_response = client.post('/auth/register', data={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert reg_response.status_code == 200
    assert b'Registrierung erfolgreich' in reg_response.data

    # Step 2: User Login
    login_response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert login_response.status_code == 200
    assert b'Willkommen' in login_response.data

    # Step 3: Access Dashboard
    dashboard_response = client.get('/dashboard')
    assert dashboard_response.status_code == 200
    assert b'Dashboard' in dashboard_response.data

    # Step 4: Create a Job Listing in the database
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        job = JobListing(title='Test Job', description='A job for testing', location='Test Location', creator_id=user.user_id)
        db.session.add(job)
        db.session.commit()
        job_id = job.job_id

    # Step 5: View Jobs Page
    jobs_response = client.get('/jobs')
    assert jobs_response.status_code == 200
    assert b'Test Job' in jobs_response.data

    # Step 6: View Job Detail Page
    job_detail_response = client.get(f'/jobs/{job_id}')
    assert job_detail_response.status_code == 200
    assert b'A job for testing' in job_detail_response.data

    # Step 7: Submit a Referral
    data = {
        'applicant_name': 'Test Applicant',
        'applicant_email': 'applicant@test.com',
        'applicant_phone': '1234567890',
        'notes': 'A great candidate.',
        'resume': (io.BytesIO(b'Dies ist ein Test-Lebenslauf.'), 'test_resume.pdf')
    }
    referral_response = client.post(f'/jobs/{job_id}/submit-referral', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert referral_response.status_code == 200
    assert b'Referral erfolgreich eingereicht!' in referral_response.data

    # Step 8: View My Referrals
    my_referrals_response = client.get('/my-referrals')
    assert my_referrals_response.status_code == 200
    assert b'Test Applicant' in my_referrals_response.data

    # Step 9: Logout
    logout_response = client.get('/auth/logout', follow_redirects=True)
    assert logout_response.status_code == 200
    assert b'Sie wurden erfolgreich abgemeldet' in logout_response.data

