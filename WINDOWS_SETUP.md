# Argo Aviation Referral Portal - Windows Setup Guide

## Systemanforderungen

- **Windows 10/11** oder Windows Server 2019/2022
- **Python 3.8 oder höher** (empfohlen: Python 3.11)
- **Git** (optional, für Entwicklung)
- **Mindestens 2GB RAM**
- **500MB freier Speicherplatz**

## Schnellstart (Automatische Installation)

1. **Repository herunterladen**
   - Laden Sie das Repository als ZIP-Datei herunter
   - Entpacken Sie es in einen Ordner Ihrer Wahl (z.B. `C:\argo-referral-portal`)

2. **Automatische Installation ausführen**
   - Öffnen Sie die Eingabeaufforderung als Administrator
   - Navigieren Sie zum Projektordner: `cd C:\argo-referral-portal`
   - Führen Sie das Setup-Skript aus: `deploy_windows.bat`

3. **Anwendung starten**
   - Führen Sie das Startskript aus: `start_windows.bat`
   - Die Anwendung ist unter http://localhost:5001 verfügbar

## Manuelle Installation

### Schritt 1: Python installieren

1. Laden Sie Python von https://python.org herunter
2. **Wichtig**: Aktivieren Sie "Add Python to PATH" während der Installation
3. Überprüfen Sie die Installation:
   ```cmd
   python --version
   pip --version
   ```

### Schritt 2: Projekt einrichten

1. **Projektordner erstellen**
   ```cmd
   mkdir C:\argo-referral-portal
   cd C:\argo-referral-portal
   ```

2. **Virtuelle Umgebung erstellen**
   ```cmd
   python -m venv venv
   ```

3. **Virtuelle Umgebung aktivieren**
   ```cmd
   venv\Scripts\activate.bat
   ```

4. **Abhängigkeiten installieren**
   ```cmd
   pip install -r requirements.txt
   ```

### Schritt 3: Konfiguration

1. **Umgebungsvariablen einrichten**
   ```cmd
   copy .env.example .env
   ```

2. **Bearbeiten Sie die .env-Datei** mit einem Texteditor:
   - Ändern Sie `SECRET_KEY` zu einem sicheren Wert
   - Passen Sie andere Einstellungen nach Bedarf an

### Schritt 4: Datenbank einrichten

1. **Datenbank initialisieren**
   ```cmd
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

2. **Beispieldaten hinzufügen** (optional)
   ```cmd
   python add_sample_data.py
   ```

### Schritt 5: Anwendung starten

1. **Entwicklungsserver starten**
   ```cmd
   python run.py
   ```

2. **Öffnen Sie Ihren Browser** und navigieren Sie zu http://localhost:5001

## Produktionsdeployment

### Option 1: Waitress (empfohlen für Windows)

1. **Waitress installieren** (bereits in requirements.txt enthalten)
   ```cmd
   pip install waitress
   ```

2. **Produktionsserver starten**
   ```cmd
   waitress-serve --host=0.0.0.0 --port=5001 run:app
   ```

### Option 2: Windows Service

1. **NSSM (Non-Sucking Service Manager) herunterladen**
   - Download von https://nssm.cc/download

2. **Service erstellen**
   ```cmd
   nssm install ArgoReferralPortal
   ```

3. **Service konfigurieren**
   - Path: `C:\argo-referral-portal\venv\Scripts\python.exe`
   - Arguments: `run.py`
   - Startup directory: `C:\argo-referral-portal`

### Option 3: IIS (Internet Information Services)

1. **IIS und Python-Unterstützung installieren**
2. **wfastcgi installieren**
   ```cmd
   pip install wfastcgi
   wfastcgi-enable
   ```
3. **IIS-Site konfigurieren** (siehe IIS-Dokumentation)

## Fehlerbehebung

### Häufige Probleme

**Problem**: `'python' is not recognized as an internal or external command`
**Lösung**: Python ist nicht im PATH. Installieren Sie Python erneut und aktivieren Sie "Add Python to PATH"

**Problem**: `Permission denied` beim Erstellen der virtuellen Umgebung
**Lösung**: Führen Sie die Eingabeaufforderung als Administrator aus

**Problem**: Module können nicht importiert werden
**Lösung**: Stellen Sie sicher, dass die virtuelle Umgebung aktiviert ist:
```cmd
venv\Scripts\activate.bat
```

**Problem**: Datenbankfehler beim Start
**Lösung**: Führen Sie die Datenbankmigrationen aus:
```cmd
flask db upgrade
```

### Logs überprüfen

- **Anwendungslogs**: `logs\argo_referral.log`
- **Windows Event Viewer**: Für Service-bezogene Probleme

### Performance-Optimierung

1. **Datenbankindizes erstellen** (für Produktionsumgebung)
2. **Static Files über IIS bereitstellen**
3. **Caching aktivieren** (Redis empfohlen)

## Sicherheitshinweise

1. **Ändern Sie den SECRET_KEY** in der Produktionsumgebung
2. **Verwenden Sie HTTPS** in der Produktion
3. **Beschränken Sie Datenbankzugriffe**
4. **Aktivieren Sie Windows Firewall-Regeln**
5. **Regelmäßige Updates** von Python und Abhängigkeiten

## Support

Bei Problemen:
1. Überprüfen Sie die Logs in `logs\argo_referral.log`
2. Stellen Sie sicher, dass alle Abhängigkeiten installiert sind
3. Überprüfen Sie die Konfiguration in der `.env`-Datei

## Automatische Updates

Erstellen Sie ein Batch-Skript für automatische Updates:

```batch
@echo off
cd C:\argo-referral-portal
git pull origin main
venv\Scripts\activate.bat
pip install -r requirements.txt
flask db upgrade
echo Update completed!
pause
```

## Monitoring

Für Produktionsumgebungen empfehlen wir:
- **Windows Performance Monitor** für Systemüberwachung
- **Application Insights** (Azure) für Anwendungsmonitoring
- **Sentry** für Fehlerberichterstattung
