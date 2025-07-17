# app.py (im Root-Verzeichnis des Projekts)

# Importiere die create_app Funktion aus dem 'app' Paket
# Das 'app' Paket ist der Ordner 'app/' in Ihrem Projekt,
# der die __init__.py Datei enthält, wo create_app definiert ist.
from app import create_app

# Importiere die Config-Klasse aus der config.py Datei
# Diese Datei sollte sich im 'config/' Ordner befinden, wie in Ihrer Architektur.
from config import Config

# Erstelle die Flask-Anwendung Instanz
# Hier wird die create_app Funktion aufgerufen, um die Anwendung zu initialisieren.
# Die Config-Klasse wird übergeben, um die Anwendungseinstellungen zu laden.
app = create_app(Config)

# Dieser Block stellt sicher, dass die Anwendung nur gestartet wird,
# wenn das Skript direkt ausgeführt wird (z.B. mit 'python app.py').
# Wenn Sie 'flask run' verwenden, ist dieser Block optional, aber gute Praxis.
if __name__ == '__main__':
    app.run(debug=True) # Starte den Entwicklungsserver im Debug-Modus
# app.py (im Root-Verzeichnis des Projekts)

print("DEBUG: app.py wird ausgeführt.")

from app import create_app
from config import Config

print("DEBUG: create_app und Config importiert.")

app = create_app(Config)

print("DEBUG: Flask-App Instanz erstellt.")

if __name__ == '__main__':
    print("DEBUG: app.py wird direkt gestartet.")
    app.run(debug=True)
else:
    print("DEBUG: app.py wird importiert (z.B. von 'flask run').")

