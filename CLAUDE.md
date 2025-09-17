# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a KI-Reifegradanalyse (AI Maturity Analysis) application that evaluates organizational AI readiness through an interactive questionnaire. The project consists of a FastAPI backend for email processing and a single-page HTML frontend with sophisticated scoring algorithms.

## Commands

### Development
```bash
# Install dependencies
uv sync

uv run dev

# OR Start development server with auto-reload
uv run python run_dev.py

# Start production server
uv run python backend.py

# Run email tests
uv run python test_email.py
```

### Deployment
```bash
# Build and run with Docker
docker build -t ki-assessment .
docker run -p 8000:8080 --env-file .env ki-assessment

# Fly.io deployment sequence
./fly-launch.sh      # Initial setup
./fly-set-secrets.sh # Configure secrets (loads from .env automatically)
./fly-deploy.sh      # Deploy application
```

## Architecture

### Email System
The application uses **Microsoft Exchange OAuth** as the primary email backend via `ms_ews_email_env.py`. The email client (`MsEwsClient`) handles:
- OAuth token management
- HTML email composition with assessment results
- Multi-recipient support
- Connection testing via health check endpoint

### Data Flow
1. **Frontend** (`static/index.html`): 6-category questionnaire with 37 questions using range sliders
2. **Scoring Algorithm**: Converts Likert scale responses (0-4) to percentages, with reverse scoring for "Quick Wins" category
3. **Maturity Classification**: Maps scores to Gartner AI Maturity Model levels (Awareness → Transformational)
4. **Backend Processing**: Receives JSON payload, generates HTML email with insights
5. **Email Delivery**: Sends comprehensive results to configured recipients

### Frontend Architecture
- **Framework**: Vanilla JavaScript with Tailwind CSS
- **Questionnaire Engine**: Dynamic rendering from `questionnaireData` object
- **Visualization**: Chart.js radar charts and custom gauge visualizations
- **PDF Generation**: html2canvas + jsPDF for client-side PDF export
- **Scoring Logic**: Category-specific calculations with weighted insights

### Configuration Management
- **Environment Variables**: `.env` file with Azure AD OAuth credentials
- **Docker**: Multi-stage build using uv package manager
- **Fly.io**: Auto-scaling configuration in `fly.toml`

## Key Files

- `backend.py` - FastAPI server with CORS, static file serving, and email endpoint
- `static/index.html` - Complete frontend application (~1000 lines)
- `ms_ews_email_env.py` - Exchange email client with OAuth authentication
- `run_dev.py` - Development server with file watching
- `fly-*.sh` - Deployment automation scripts
- `.env` - Exchange OAuth configuration (gitignored in production)

## Development Notes

### Email Configuration
The system requires Azure AD App Registration with:
- API Permission: `Mail.Send` (Microsoft Graph)
- Client credentials flow for application permissions
- Variables: `EWS_CLIENT_ID`, `EWS_CLIENT_SECRET`, `EWS_TENANT_ID`, `EWS_SENDER_ADDRESS`, `EWS_RECIPIENT_ADDRESS`

### Questionnaire Structure
Questions are organized into 6 categories:
1. **Strategie** (5 questions) - Strategic AI alignment
2. **Organisation** (7 questions) - Organizational readiness
3. **Technik** (7 questions) - Technical infrastructure
4. **Kultur / Akzeptanz** (13 questions) - Cultural acceptance
5. **Regulatorik** (6 questions) - Compliance and governance
6. **Nutzung Quick Wins / KI-Potentiale** (5 questions) - Implementation opportunities (reverse scored)

### Scoring Algorithm
- Individual questions: 0-4 scale converted to 0-100%
- Category scores: Average of question percentages
- Total score: Average of all category scores
- Maturity levels: 5-tier classification (0-20%, 21-40%, 41-60%, 61-80%, 81-100%)

### Deployment Pipeline
The Fly.io deployment uses a 3-script approach:
1. `fly-launch.sh` - App creation and initial setup
2. `fly-set-secrets.sh` - Environment variable configuration (auto-loads from `.env`)
3. `fly-deploy.sh` - Code deployment with health checks