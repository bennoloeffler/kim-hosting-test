# KI-Reifegradanalyse Setup Guide

## Überblick
Diese Anwendung besteht aus:
- **Frontend**: HTML-Seite mit Selbsteinschätzungs-Fragebogen
- **Backend**: Python FastAPI Server für E-Mail-Versand der Ergebnisse

## Installation

### 1. Voraussetzungen

Installieren Sie [uv](https://docs.astral.sh/uv/) als Python-Paketmanager:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Oder via pip
pip install uv
```

### 2. Projekt einrichten

```bash
# Abhängigkeiten installieren
uv sync

# Entwicklungsumgebung aktivieren
source .venv/bin/activate  # Linux/macOS
# oder
.venv\Scripts\activate     # Windows
```

### 3. E-Mail-Konfiguration einrichten

Kopieren Sie `.env.example` zu `.env` und tragen Sie Ihre E-Mail-Zugangsdaten ein:

```bash
cp .env.example .env
```

#### Microsoft Outlook/Exchange (empfohlen)

Die Anwendung ist für Microsoft Exchange/Outlook optimiert. Bearbeiten Sie `.env`:

```env
# Azure AD Application Registration
EWS_CLIENT_ID=ihre-client-id
EWS_CLIENT_SECRET=ihr-client-secret
EWS_TENANT_ID=ihre-tenant-id

# Email Configuration
EWS_SENDER_ADDRESS=sender@ihredomain.com
EWS_RECIPIENT_ADDRESS=empfaenger1@domain.com,empfaenger2@domain.com
EWS_SERVER=outlook.office365.com
```

##### Azure AD App Registration einrichten:

1. Gehen Sie zum [Azure Portal](https://portal.azure.com)
2. Navigieren Sie zu "Azure Active Directory" → "App registrations"
3. Klicken Sie "New registration"
4. Name: "KI-Reifegradanalyse"
5. Supported account types: "Accounts in this organizational directory only"
6. Klicken Sie "Register"

**API Permissions konfigurieren:**
1. Gehen Sie zu "API permissions"
2. Klicken Sie "Add a permission"
3. Wählen Sie "Microsoft Graph"
4. Wählen Sie "Application permissions"
5. Fügen Sie hinzu: `Mail.Send`
6. Klicken Sie "Grant admin consent"

**Client Secret erstellen:**
1. Gehen Sie zu "Certificates & secrets"
2. Klicken Sie "New client secret"
3. Beschreibung: "KI-Assessment"
4. Expiry: 24 Monate
5. Kopieren Sie den Secret-Wert sofort (wird nur einmal angezeigt)

**Tenant ID und Client ID finden:**
- Client ID: Auf der "Overview"-Seite als "Application (client) ID"
- Tenant ID: Auf der "Overview"-Seite als "Directory (tenant) ID"

## Development

### Backend starten

```bash
uv run dev
```

Der Server läuft dann auf http://localhost:8000

### API Endpunkte:
- `GET /` - Status-Check
- `GET /api/health` - Health Check
- `POST /api/submit-assessment` - Sendet Bewertungsergebnisse per E-Mail

## Frontend nutzen

1. Öffnen Sie `http://localhost:8000` in einem Webbrowser
2. Füllen Sie den Fragebogen aus
3. Optional: Geben Sie Ihre Kontaktdaten ein
4. Klicken Sie auf "Scores berechnen"
5. Die Ergebnisse werden automatisch per E-Mail gesendet

## Deployment

### Fly.io (empfohlen)

Das Projekt ist für Fly.io optimiert. Nutzen Sie die bereitgestellten Scripts:

```bash
# Erstmalige Einrichtung
./fly-launch.sh

# Secrets setzen (einmalig oder bei Änderungen)
./fly-set-secrets.sh

# Deployment
./fly-deploy.sh
```


### Lokale Production


## Anpassungen

### E-Mail-Empfänger ändern:
In `.env` die Variable `EWS_RECIPIENT_ADDRESS` anpassen.
