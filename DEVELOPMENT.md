# Argo Aviation Referral Portal - Entwicklungsanleitung

## Projektstatus

Das Projekt wurde entsprechend der Wireframes umstrukturiert und erweitert:

### ✅ Implementiert
- **Authentifizierung**: Login/Register mit CSRF-Schutz
- **Dashboard**: Rollenabhängige Ansichten (User/Superadmin)
- **Job-Management**: Stellenausschreibungen durchsuchen und anzeigen
- **Referral-System**: Referrals einreichen und verwalten
- **Admin-Bereich**: Benutzer- und Job-Verwaltung für Superadmin
- **API-Endpunkte**: RESTful API für Frontend-Integration
- **Responsive Design**: Mobile-freundliche Templates
- **Error-Handling**: 404, 403, 500 Error-Seiten

### 🔄 Nächste Schritte
- Datei-Upload für Lebensläufe implementieren
- E-Mail-Benachrichtigungen
- Zoho ATS Integration
- Erweiterte Suchfilter
- Dashboard-Statistiken
- Unit-Tests erweitern

## Setup & Entwicklung

### 1. Umgebung aktivieren
```bash
# Windows
venv\Scripts\activate
# oder
argo-referral-env\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 3. Datenbank einrichten
```bash
# Migrationen ausführen
flask db upgrade

# Testdaten erstellen (optional)
python -c "from app import create_app, db; from app.models import *; app = create_app(); app.app_context().push(); db.create_all()"
```

### 4. Anwendung starten
```bash
# Entwicklungsserver
flask run

# Oder mit Python
python run.py
```

### 5. Tests ausführen
```bash
pytest tests/
```

## Projektstruktur

```
Argo-Referral-Portal/
├── app/
│   ├── __init__.py          # Flask App Factory
│   ├── auth.py              # Authentifizierung (Login/Register)
│   ├── main.py              # Haupt-Routen (Dashboard, Jobs, etc.)
│   ├── api.py               # REST API Endpunkte
│   ├── models/              # SQLAlchemy Modelle
│   ├── templates/           # Jinja2 Templates
│   │   ├── base.html        # Basis-Template
│   │   ├── dashboard.html   # Dashboard
│   │   ├── jobs.html        # Stellenausschreibungen
│   │   ├── job_detail.html  # Job-Details
│   │   ├── submit_referral.html # Referral-Submission
│   │   ├── my_referrals.html # Meine Referrals
│   │   ├── profile.html     # Benutzerprofil
│   │   ├── admin_*.html     # Admin-Templates
│   │   └── errors/          # Error-Seiten
│   └── static/              # CSS, JS, Bilder
├── migrations/              # Datenbank-Migrationen
├── tests/                   # Unit-Tests
├── config.py               # Konfiguration
├── requirements.txt        # Python-Dependencies
└── run.py                  # Anwendungs-Entry-Point
```

## Konfiguration

### Umgebungsvariablen (.env)
```env
DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

### Superadmin-Konfiguration
Der Superadmin wird über die E-Mail-Adresse in `app/main.py` definiert:
```python
SUPERADMIN_EMAIL = "tobi196183@gmail.com"
```

## API-Endpunkte

### Authentifizierung erforderlich
- `GET /api/users/profile` - Benutzerprofil abrufen
- `PUT /api/users/profile` - Benutzerprofil aktualisieren
- `GET /api/jobs` - Stellenausschreibungen (mit Filtern)
- `GET /api/jobs/<job_id>` - Job-Details
- `GET /api/referrals` - Benutzer-Referrals
- `POST /api/referrals` - Neues Referral erstellen

### Query-Parameter für Jobs-API
- `search` - Stellentitel-Suche
- `location` - Standort-Filter
- `employment_type` - Beschäftigungsart
- `sort_by` - Sortierung (posting_date, title, location)
- `sort_order` - Sortierreihenfolge (asc, desc)
- `page` - Seitennummer
- `per_page` - Einträge pro Seite (max. 50)

## Deployment

### Produktionsumgebung
1. `FLASK_ENV=production` setzen
2. Starke `SECRET_KEY` generieren
3. Produktions-Datenbank konfigurieren
4. Gunicorn oder uWSGI verwenden
5. Reverse-Proxy (Nginx) einrichten

### Azure DevOps Integration
- CI/CD-Pipeline konfiguriert
- Automatisierte Tests
- Deployment zu Azure App Service

## Troubleshooting

### Häufige Probleme
1. **Import-Fehler**: Virtual Environment aktivieren
2. **Datenbank-Fehler**: Migrationen ausführen
3. **Template-Fehler**: Flask-Cache leeren
4. **CSRF-Fehler**: Session-Cookie prüfen

### Debug-Modus
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

## Contributing

1. Feature-Branch erstellen
2. Änderungen implementieren
3. Tests schreiben/ausführen
4. Pull Request erstellen
5. Code Review durchführen

## Backup & Wiederherstellung

Das Projekt wurde mit Datums-/Zeitstempel gesichert:
```
Argo-Referral-Portal_backup_YYYYMMDD_HHMMSS/
```

Zur Wiederherstellung:
1. Aktuelles Projekt sichern
2. Backup-Ordner kopieren
3. Virtual Environment neu erstellen
4. Dependencies installieren
