# KI-Reifegradanalyse Setup Guide

## Überblick
Diese Anwendung besteht aus:
- **Frontend**: HTML-Seite mit Selbsteinschätzungs-Fragebogen
- **Backend**: Python FastAPI Server für E-Mail-Versand der Ergebnisse

## Installation

### 1. Python-Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 2. E-Mail-Konfiguration einrichten

Kopieren Sie `.env.example` zu `.env` und tragen Sie Ihre E-Mail-Zugangsdaten ein:

```bash
cp .env.example .env
```

Bearbeiten Sie `.env` mit Ihren Zugangsdaten:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=ihre-email@gmail.com
SENDER_PASSWORD=ihr-app-passwort
```

#### Gmail App-Passwort erstellen:
1. Gehen Sie zu: https://myaccount.google.com/apppasswords
2. Erstellen Sie ein neues App-Passwort für "Mail"
3. Verwenden Sie dieses Passwort (nicht Ihr normales Gmail-Passwort)

#### Alternative E-Mail-Provider:
- **Outlook/Hotmail**: smtp-mail.outlook.com (Port 587)
- **Yahoo**: smtp.mail.yahoo.com (Port 587)
- **Firmen-E-Mail**: Kontaktieren Sie Ihre IT-Abteilung

## Backend starten

```bash
python backend.py
```

Der Server läuft dann auf http://localhost:8000

### API Endpunkte:
- `GET /` - Status-Check
- `GET /api/health` - Health Check
- `POST /api/submit-assessment` - Sendet Bewertungsergebnisse per E-Mail

## Frontend nutzen

1. Öffnen Sie `25_8_25_KIM_Reifegradanalyse.html` in einem Webbrowser
2. Füllen Sie den Fragebogen aus
3. Optional: Geben Sie Ihre Kontaktdaten ein
4. Klicken Sie auf "Scores berechnen"
5. Die Ergebnisse werden automatisch an benno.loeffler@gmx.de gesendet

## Deployment-Optionen

### Lokal
Frontend kann direkt als HTML-Datei geöffnet werden, Backend muss laufen.

### Production Server

#### Backend mit systemd (Linux):
Erstellen Sie `/etc/systemd/system/ki-assessment.service`:

```ini
[Unit]
Description=KI Assessment Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/kim-hosting-test
Environment="PATH=/usr/local/bin:/usr/bin"
ExecStart=/usr/bin/python3 backend.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Mit Docker:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend-Deployment:
- HTML kann auf jedem Webserver gehostet werden
- Backend-URL in HTML anpassen (Zeile 916): `http://localhost:8000` → `https://ihr-server.de`

## Anpassungen

### E-Mail-Empfänger ändern:
In `backend.py` Zeile 34:
```python
def send_email(data: AssessmentData, recipient_email: str = "neue-email@example.de"):
```

### Backend-URL im Frontend ändern:
In `25_8_25_KIM_Reifegradanalyse.html` Zeile 916:
```javascript
const response = await fetch('https://ihr-backend-server.de/api/submit-assessment', {
```

## Fehlerbehebung

### E-Mail wird nicht gesendet:
1. Prüfen Sie die `.env` Datei
2. Stellen Sie sicher, dass App-Passwort verwendet wird (nicht normales Passwort)
3. Prüfen Sie Firewall-Einstellungen für SMTP-Port

### CORS-Fehler:
Backend erlaubt bereits alle Origins. Bei Problemen, spezifische Domain in `backend.py` eintragen:
```python
allow_origins=["https://ihre-domain.de"]
```

### Backend nicht erreichbar:
1. Prüfen Sie, ob Backend läuft: `curl http://localhost:8000/api/health`
2. Prüfen Sie Firewall-Einstellungen
3. Bei Production: Prüfen Sie Reverse-Proxy-Konfiguration