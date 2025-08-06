#!/usr/bin/env python3
"""
Argo Aviation Referral Portal - Python Setup Script
Plattformübergreifendes Setup-Script für die Implementierung der wiederhergestellten Codes
"""

import os
import sys
import subprocess
import shutil
import platform
from datetime import datetime
from pathlib import Path

class Colors:
    """ANSI-Farbcodes für Terminal-Ausgabe"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_colored(message, color=Colors.NC):
    """Druckt farbige Nachrichten"""
    if platform.system() == "Windows":
        # Windows unterstützt ANSI-Codes möglicherweise nicht
        print(message)
    else:
        print(f"{color}{message}{Colors.NC}")

def print_success(message):
    print_colored(f"✅ {message}", Colors.GREEN)

def print_warning(message):
    print_colored(f"⚠️  {message}", Colors.YELLOW)

def print_error(message):
    print_colored(f"❌ {message}", Colors.RED)

def print_info(message):
    print_colored(f"ℹ️  {message}", Colors.BLUE)

def print_header(message):
    print_colored(f"\n{'='*50}", Colors.PURPLE)
    print_colored(f"🚀 {message}", Colors.WHITE)
    print_colored(f"{'='*50}", Colors.PURPLE)

def check_prerequisites():
    """Überprüft Systemvoraussetzungen"""
    print_info("Überprüfe Systemvoraussetzungen...")
    
    # Python Version überprüfen
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print_error(f"Python 3.8+ erforderlich, gefunden: {python_version.major}.{python_version.minor}")
        return False
    else:
        print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} gefunden")
    
    # Git überprüfen
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print_success("Git ist verfügbar")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Git ist nicht installiert oder nicht im PATH!")
        return False
    
    # pip überprüfen
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, check=True)
        print_success("pip ist verfügbar")
    except subprocess.CalledProcessError:
        print_error("pip ist nicht verfügbar!")
        return False
    
    return True

def create_backup():
    """Erstellt ein Backup der aktuellen Konfiguration"""
    print_info("Erstelle Backup der aktuellen Konfiguration...")
    
    current_dir = Path.cwd()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = current_dir.parent / f"argo-aviation-backup-{timestamp}"
    
    try:
        if current_dir.exists() and any(current_dir.iterdir()):
            shutil.copytree(current_dir, backup_dir, ignore=shutil.ignore_patterns('.git', '__pycache__', 'venv', 'env'))
            print_success(f"Backup erstellt in: {backup_dir}")
        else:
            print_warning("Kein bestehendes Verzeichnis gefunden - überspringe Backup")
    except Exception as e:
        print_warning(f"Backup konnte nicht erstellt werden: {e}")

def create_directory_structure():
    """Erstellt die vollständige Projektstruktur"""
    print_info("Erstelle Projektstruktur...")
    
    directories = [
        "app/templates",
        "app/static/css",
        "app/static/js", 
        "app/static/images",
        "docs",
        "tests",
        "config",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print_success("Verzeichnisstruktur erstellt")

def create_templates():
    """Erstellt die wiederhergestellten HTML-Templates"""
    print_info("Implementiere wiederhergestellte Templates...")
    
    # Dashboard Template
    dashboard_html = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; text-align: center; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
        h1 { color: #333; }
        p { color: #555; }
        .logout-btn { padding: 10px 20px; background-color: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; text-decoration: none; display: inline-block; margin-top: 20px; }
        .logout-btn:hover { background-color: #c82333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Willkommen im Dashboard, {{ user.first_name }}!</h1>
        <p>Dies ist Ihre Hauptseite nach dem Login.</p>
        <a href="{{ url_for('auth.logout') }}" class="logout-btn">Abmelden</a>
    </div>
</body>
</html>'''
    
    # Login Template
    login_html = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        h1 { text-align: center; color: #333; }
        label { display: block; margin-bottom: 5px; color: #555; }
        input[type="email"], input[type="password"] {
            width: calc(100% - 22px); padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px;
        }
        button {
            width: 100%; padding: 10px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;
        }
        button:hover { background-color: #218838; }
        .flash-message { padding: 10px; margin-bottom: 15px; border-radius: 4px; text-align: center; }
        .flash-message.danger { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .flash-message.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <label for="email">E-Mail:</label>
            <input type="email" id="email" name="email" required>

            <label for="password">Passwort:</label>
            <input type="password" id="password" name="password" required>

            <button type="submit">Anmelden</button>
        </form>
        <p style="text-align: center; margin-top: 15px;"><a href="{{ url_for('auth.register') }}">Noch kein Konto? Registrieren Sie sich hier.</a></p>
    </div>
</body>
</html>'''
    
    # Register Template
    register_html = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrierung</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
        h1 { text-align: center; color: #333; }
        label { display: block; margin-bottom: 5px; color: #555; }
        input[type="email"], input[type="password"], input[type="text"], select {
            width: calc(100% - 22px); padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px;
        }
        button {
            width: 100%; padding: 10px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;
        }
        button:hover { background-color: #0056b3; }
        .flash-message { padding: 10px; margin-bottom: 15px; border-radius: 4px; text-align: center; }
        .flash-message.danger { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .flash-message.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .flash-message.warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Registrieren</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <label for="first_name">Vorname:</label>
            <input type="text" id="first_name" name="first_name" required>

            <label for="last_name">Nachname:</label>
            <input type="text" id="last_name" name="last_name" required>

            <label for="email">E-Mail:</label>
            <input type="email" id="email" name="email" required>

            <label for="password">Passwort:</label>
            <input type="password" id="password" name="password" required>

            <label for="phone_number">Telefonnummer (optional):</label>
            <input type="text" id="phone_number" name="phone_number">

            <label for="user_type">Benutzertyp:</label>
            <select id="user_type" name="user_type" required>
                <option value="">Bitte auswählen</option>
                <option value="referrer">Referrer</option>
                <option value="applicant">Applicant</option>
                <option value="admin">Admin</option>
            </select>

            <button type="submit">Registrieren</button>
        </form>
        <p style="text-align: center; margin-top: 15px;"><a href="{{ url_for('auth.login') }}">Bereits ein Konto? Hier anmelden.</a></p>
    </div>
</body>
</html>'''
    
    # Templates schreiben
    templates = {
        "app/templates/dashboard.html": dashboard_html,
        "app/templates/login.html": login_html,
        "app/templates/register.html": register_html
    }
    
    for filepath, content in templates.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print_success("Templates erfolgreich erstellt")

def create_requirements():
    """Erstellt die requirements.txt Datei"""
    print_info("Aktualisiere requirements.txt...")
    
    requirements_content = '''# KORRIGIERTE requirements.txt für Argo Aviation Referral Portal

# Flask Core
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5

# Authentication & Security
Flask-Login==0.6.3
Flask-WTF==1.1.1
WTForms==3.0.1
Werkzeug==2.3.7

# Database
pyodbc==4.0.39
SQLAlchemy==2.0.21

# Configuration & Environment
python-dotenv==1.0.0

# Development & Debugging
Flask-DebugToolbar==0.13.1

# Production Server (optional)
gunicorn==21.2.0

# Validation & Forms
email-validator==2.0.0

# Security
cryptography==41.0.4

# Utilities
python-dateutil==2.8.2

# Testing (optional)
pytest==7.4.2
pytest-flask==1.2.0

# Azure Integration (optional)
azure-identity==1.14.0
azure-keyvault-secrets==4.7.0'''
    
    with open("requirements.txt", 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print_success("requirements.txt aktualisiert")

def setup_virtual_environment():
    """Richtet die virtuelle Umgebung ein und installiert Dependencies"""
    print_info("Richte virtuelle Umgebung ein...")
    
    venv_path = Path("venv")
    
    # Virtuelle Umgebung erstellen
    if not venv_path.exists():
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print_success("Virtuelle Umgebung erstellt")
        except subprocess.CalledProcessError as e:
            print_error(f"Fehler beim Erstellen der virtuellen Umgebung: {e}")
            return False
    else:
        print_warning("Virtuelle Umgebung bereits vorhanden")
    
    # Python-Executable in der virtuellen Umgebung finden
    if platform.system() == "Windows":
        venv_python = venv_path / "Scripts" / "python.exe"
        venv_pip = venv_path / "Scripts" / "pip.exe"
    else:
        venv_python = venv_path / "bin" / "python"
        venv_pip = venv_path / "bin" / "pip"
    
    # pip aktualisieren
    try:
        print_info("Aktualisiere pip...")
        subprocess.run([str(venv_pip), "install", "--upgrade", "pip"], check=True, capture_output=True)
        print_success("pip aktualisiert")
    except subprocess.CalledProcessError as e:
        print_warning(f"pip-Update fehlgeschlagen: {e}")
    
    # Dependencies installieren
    try:
        print_info("Installiere Dependencies...")
        subprocess.run([str(venv_pip), "install", "-r", "requirements.txt"], check=True)
        print_success("Dependencies erfolgreich installiert")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Fehler bei der Installation der Dependencies: {e}")
        return False

def create_additional_files():
    """Erstellt zusätzliche Projektdateien"""
    print_info("Erstelle zusätzliche Projektdateien...")
    
    # .gitignore
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Flask
instance/
.webassets-cache

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Azure
.azure/

# Backup files
*backup*
recovered_*'''
    
    # README.md
    readme_content = '''# Argo Aviation Referral Portal

Ein professionelles Referral-Portal für Argo Aviation, entwickelt als Teil einer IHK-Abschlussarbeit.

## 🚀 Quick Start

1. **Setup ausführen:**
   ```bash
   python setup.py
   ```

2. **Anwendung starten:**
   ```bash
   # Linux/Mac:
   source venv/bin/activate
   # Windows:
   venv\\Scripts\\activate.bat
   
   python app.py
   ```

## 📋 Features

- ✅ Benutzerregistrierung und -authentifizierung
- ✅ Rollenbasierte Zugriffskontrolle  
- ✅ Responsive Design
- ✅ Azure SQL Database Integration
- ✅ CI/CD mit Azure DevOps

## 🛠️ Technologie-Stack

- **Backend:** Flask 2.3.3, SQLAlchemy, Flask-Login
- **Frontend:** HTML5, CSS3, JavaScript
- **Datenbank:** Azure SQL Database
- **Deployment:** Azure App Service
- **CI/CD:** Azure DevOps

## 📊 Projektfortschritt

- [x] Infrastruktur Setup (95%)
- [x] Backend-Architektur (80%)
- [x] Frontend-Templates (70%)
- [ ] Job-Listing-Management (30%)
- [ ] Referral-System (25%)

## 🔒 Sicherheit

- Passwort-Hashing mit Werkzeug
- CSRF-Schutz mit Flask-WTF
- Session-Management mit Flask-Login
- SQL-Injection-Schutz mit SQLAlchemy

## 📞 Support

Bei Fragen erstellen Sie ein Issue im GitHub-Repository.

---
**Entwickelt für Argo Aviation | IHK-Abschlussarbeit 2025**'''
    
    # Test-Datei
    test_content = '''import pytest
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
    assert b'Login' in response.data'''
    
    # Dateien schreiben
    files = {
        ".gitignore": gitignore_content,
        "README.md": readme_content,
        "tests/__init__.py": "# Test package initialization",
        "tests/test_auth.py": test_content
    }
    
    for filepath, content in files.items():
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print_success("Zusätzliche Dateien erstellt")

def main():
    """Hauptfunktion des Setup-Scripts"""
    print_header("Argo Aviation Referral Portal Setup")
    
    try:
        # Schritt 1: Voraussetzungen überprüfen
        if not check_prerequisites():
            print_error("Voraussetzungen nicht erfüllt. Setup abgebrochen.")
            return False
        
        # Schritt 2: Backup erstellen
        create_backup()
        
        # Schritt 3: Projektstruktur erstellen
        create_directory_structure()
        
        # Schritt 4: Templates implementieren
        create_templates()
        
        # Schritt 5: Requirements aktualisieren
        create_requirements()
        
        # Schritt 6: Virtuelle Umgebung einrichten
        if not setup_virtual_environment():
            print_error("Fehler bei der Einrichtung der virtuellen Umgebung")
            return False
        
        # Schritt 7: Zusätzliche Dateien erstellen
        create_additional_files()
        
        # Erfolgreicher Abschluss
        print_colored(f"\n{'='*50}", Colors.GREEN)
        print_success("🎉 Setup erfolgreich abgeschlossen!")
        print_colored(f"{'='*50}", Colors.GREEN)
        
        print_info("\nNächste Schritte:")
        if platform.system() == "Windows":
            print("1. Aktivieren Sie die virtuelle Umgebung: venv\\Scripts\\activate.bat")
        else:
            print("1. Aktivieren Sie die virtuelle Umgebung: source venv/bin/activate")
        print("2. Konfigurieren Sie Ihre .env-Datei mit den korrekten Datenbankdaten")
        print("3. Führen Sie Datenbankmigrationen aus: flask db upgrade")
        print("4. Starten Sie die Anwendung: python app.py")
        print("\nDie Anwendung wird dann unter http://localhost:5000 verfügbar sein.")
        print_warning("\nVergessen Sie nicht, Ihre .env-Datei mit den korrekten Azure-Datenbank-Credentials zu konfigurieren!")
        
        return True
        
    except KeyboardInterrupt:
        print_error("\nSetup durch Benutzer abgebrochen.")
        return False
    except Exception as e:
        print_error(f"Unerwarteter Fehler: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

