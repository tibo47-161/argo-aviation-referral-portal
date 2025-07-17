# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager # Importiere LoginManager für die Benutzerauthentifizierung
from config import Config # Importiere die Konfigurationsklasse

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

print("DEBUG: create_app Funktion wird definiert.")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    print("DEBUG: Flask-App in create_app initialisiert.")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    print("DEBUG: DB, Migrate, LoginManager initialisiert.")

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        print(f"DEBUG: load_user aufgerufen für User ID: {user_id}")
        return User.query.get(user_id)

    from app.models import User, JobListing, Referral
    print("DEBUG: Modelle importiert.")

    from app.auth import auth_bp
    from app.main import main_bp
    print("DEBUG: Blueprints auth_bp und main_bp importiert.")

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    print("DEBUG: Blueprints auth_bp und main_bp registriert.")

    return app
