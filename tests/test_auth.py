import pytest
from app import create_app, db
from app.models import User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

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

def test_register_page(client):
    """Test dass die Registrierungsseite lädt"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Registrieren' in response.data

def test_login_page(client):
    """Test dass die Login-Seite lädt"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data