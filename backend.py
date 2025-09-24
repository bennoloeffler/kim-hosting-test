from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import json
import os
import logging
import traceback
from dotenv import load_dotenv
from ms_ews_email_env import MsEwsClient

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load .env file (will NOT override existing shell environment variables)
load_dotenv(override=False)

logger.info("=" * 80)
logger.info("BACKEND STARTUP")
logger.info("=" * 80)
logger.info("Using Microsoft Exchange OAuth for email")
logger.info("Environment variable sources:")
logger.info("  - Shell environment variables take precedence")
logger.info("  - .env file used as fallback")
logger.info(f"EWS_SENDER_ADDRESS: {os.getenv('EWS_SENDER_ADDRESS', 'Not set')}")
logger.info(f"EWS_RECIPIENT_ADDRESS: {os.getenv('EWS_RECIPIENT_ADDRESS', 'Not set')}")
logger.info(f"EWS_CLIENT_ID: {os.getenv('EWS_CLIENT_ID', 'Not set')}")
logger.info(f"EWS_TENANT_ID: {os.getenv('EWS_TENANT_ID', 'Not set')}")
logger.info(f"EWS_CLIENT_SECRET: {'*' * len(os.getenv('EWS_CLIENT_SECRET', '')) if os.getenv('EWS_CLIENT_SECRET') else 'Not set'}")
logger.info("=" * 80)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class AssessmentData(BaseModel):
    scores: Dict[str, float]
    totalScore: float
    maturityLevel: str
    insights: Dict[str, str]
    contactInfo: Optional[Dict[str, str]] = None
    userAnswers: Dict[str, Any]
    timestamp: Optional[str] = None

def send_email(data: AssessmentData, recipient_email: str = None):
    """Send assessment results via email using Microsoft Exchange"""

    # Use environment variable if no recipient is specified
    if recipient_email is None:
        recipient_email = os.getenv('EWS_RECIPIENT_ADDRESS')
        if not recipient_email:
            raise HTTPException(
                status_code=500,
                detail="No recipient email specified and EWS_RECIPIENT_ADDRESS environment variable not set"
            )
        logger.info(f"Using recipient email from EWS_RECIPIENT_ADDRESS environment variable: {recipient_email}")
    else:
        logger.info(f"Using explicitly provided recipient email: {recipient_email}")

    logger.info("=" * 80)
    logger.info("EMAIL SENDING PROCESS STARTED (Exchange OAuth)")
    logger.info(f"Recipient: {recipient_email}")
    logger.info(f"Maturity Level: {data.maturityLevel}")
    logger.info(f"Total Score: {data.totalScore}")
    logger.info(f"Has Contact Info: {bool(data.contactInfo)}")
    if data.contactInfo:
        logger.info(f"Contact: {data.contactInfo.get('name', 'No name')} - {data.contactInfo.get('email', 'No email')}")
    logger.info("=" * 80)

    try:
        ews_client = MsEwsClient()

        if not ews_client.test_connection():
            logger.error("Failed to connect to Exchange server")
            raise HTTPException(status_code=500, detail="Failed to connect to email server")

        contact_info_html = ""
        if data.contactInfo:
            contact_info_html = f"""
            <h3>Kontaktinformationen:</h3>
            <ul>
                <li><strong>Name:</strong> {data.contactInfo.get('name', 'N/A')}</li>
                <li><strong>E-Mail:</strong> {data.contactInfo.get('email', 'N/A')}</li>
                <li><strong>Telefon:</strong> {data.contactInfo.get('phone', 'N/A')}</li>
                <li><strong>Unternehmen:</strong> {data.contactInfo.get('company', 'N/A')}</li>
            </ul>
            """

        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>KI-Reifegradanalyse Ergebnisse</h2>
            <p><strong>Datum:</strong> {data.timestamp or datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

            {contact_info_html}

            <h3>Gesamtergebnis:</h3>
            <p><strong>Gesamtscore:</strong> {data.totalScore:.1f}%</p>
            <p><strong>Reifegrad:</strong> {data.maturityLevel}</p>

            <h3>Kategorie-Scores:</h3>
            <ul>
                {"".join([f"<li><strong>{cat}:</strong> {score:.1f}%</li>" for cat, score in data.scores.items()])}
            </ul>

            <h3>Handlungsempfehlungen:</h3>
            <ul>
                {"".join([f"<li><strong>{cat}:</strong> {insight}</li>" for cat, insight in data.insights.items()])}
            </ul>

            <h3>Detaillierte Antworten:</h3>
            <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
{json.dumps(data.userAnswers, indent=2, ensure_ascii=False)}
            </pre>
          </body>
        </html>
        """

        subject = f"KI-Reifegradanalyse Ergebnisse - {data.maturityLevel}"

        logger.info(f"Sending email via Exchange to {recipient_email}...")
        ews_client.send_message(
            subject=subject,
            body=html_body,
            recipient=recipient_email,
            html_body=True
        )

        logger.info("=" * 80)
        logger.info("EMAIL PROCESS COMPLETED SUCCESSFULLY (Exchange)")
        logger.info("=" * 80)
        return True

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"ERROR SENDING EMAIL: {str(e)}")
        logger.error(f"Error Type: {type(e).__name__}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        logger.error("=" * 80)
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@app.post("/api/submit-assessment")
async def submit_assessment(data: AssessmentData):
    """Receive assessment data and send via email"""
    logger.info("=" * 80)
    logger.info("NEW ASSESSMENT SUBMISSION RECEIVED")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Total Score: {data.totalScore}")
    logger.info(f"Maturity Level: {data.maturityLevel}")
    logger.info("Category Scores:")
    for category, score in data.scores.items():
        logger.info(f"  - {category}: {score:.1f}%")
    logger.info("=" * 80)

    try:
        data.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        logger.info("Calling send_email function...")
        send_email(data)
        logger.info("send_email function returned successfully")

        response = {
            "status": "success",
            "message": "Assessment results sent successfully",
            "timestamp": data.timestamp
        }
        logger.info(f"Returning success response: {response}")
        return response

    except HTTPException as he:
        logger.error(f"HTTP Exception in submit_assessment: {str(he.detail)}")
        raise he

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"UNEXPECTED ERROR in submit_assessment: {str(e)}")
        logger.error(f"Error Type: {type(e).__name__}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        logger.error("=" * 80)
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/")
async def serve_html():
    """Serve the HTML file"""
    return FileResponse("static/index.html", media_type="text/html")

@app.get("/api/health")
async def health_check():
    """Health check endpoint that also verifies Exchange connection"""
    try:
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "email_backend": "Microsoft Exchange (OAuth)"
        }

        try:
            ews_client = MsEwsClient()
            if ews_client.test_connection():
                health["email_status"] = "connected"
            else:
                health["email_status"] = "disconnected"
        except Exception as e:
            health["email_status"] = f"error: {str(e)}"

        return health
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

def main():
    """Main entry point for production server"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()