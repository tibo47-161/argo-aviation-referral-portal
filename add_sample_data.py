from app import create_app, db
from app.models import JobListing, User
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Beispiel-Stellenausschreibungen hinzufügen
    jobs = [
        JobListing(
            title='Commercial Pilot - A320',
            description='Wir suchen einen erfahrenen Piloten für unsere A320-Flotte. Mindestens 3000 Flugstunden erforderlich.',
            requirements='ATPL-Lizenz, A320 Type Rating, Mindestens 3000 Flugstunden, Englisch Level 4',
            location='Hamburg',
            salary_range='80.000 - 120.000 EUR',
            employment_type='Vollzeit',
            department='Flight Operations',
            referral_bonus=2000.00,
            is_active=True,
            expiry_date=datetime.utcnow() + timedelta(days=30)
        ),
        JobListing(
            title='Aircraft Maintenance Engineer',
            description='Wartungsingenieur für unsere Flotte. Verantwortlich für die technische Wartung und Instandhaltung.',
            requirements='EASA Part-66 Lizenz, Mindestens 5 Jahre Erfahrung, Deutsch und Englisch fließend',
            location='München',
            salary_range='60.000 - 85.000 EUR',
            employment_type='Vollzeit',
            department='Maintenance',
            referral_bonus=1500.00,
            is_active=True,
            expiry_date=datetime.utcnow() + timedelta(days=45)
        ),
        JobListing(
            title='Flight Dispatcher',
            description='Flugdisponent für die Planung und Überwachung von Flugoperationen.',
            requirements='Flight Dispatcher Lizenz, Meteorologie-Kenntnisse, Mindestens 2 Jahre Erfahrung',
            location='Frankfurt',
            salary_range='45.000 - 65.000 EUR',
            employment_type='Vollzeit',
            department='Operations',
            referral_bonus=1000.00,
            is_active=True,
            expiry_date=datetime.utcnow() + timedelta(days=60)
        ),
        JobListing(
            title='Cabin Crew Member',
            description='Flugbegleiter/in für internationale Flüge. Freundlicher Service und Sicherheit stehen im Vordergrund.',
            requirements='Cabin Crew Attestation, Erste-Hilfe-Schein, Mehrsprachigkeit von Vorteil',
            location='Berlin',
            salary_range='35.000 - 50.000 EUR',
            employment_type='Vollzeit',
            department='Cabin Services',
            referral_bonus=750.00,
            is_active=True,
            expiry_date=datetime.utcnow() + timedelta(days=20)
        ),
        JobListing(
            title='Aviation Safety Manager',
            description='Sicherheitsmanager für die Überwachung und Verbesserung der Flugsicherheit.',
            requirements='Safety Management System Erfahrung, Luftfahrt-Hintergrund, Analytische Fähigkeiten',
            location='Köln',
            salary_range='70.000 - 95.000 EUR',
            employment_type='Vollzeit',
            department='Safety & Quality',
            referral_bonus=1800.00,
            is_active=True,
            expiry_date=datetime.utcnow() + timedelta(days=40)
        )
    ]
    
    for job in jobs:
        db.session.add(job)
    
    db.session.commit()
    print("Beispieldaten erfolgreich hinzugefügt!")
    print(f"Hinzugefügte Jobs: {len(jobs)}")
