#!/usr/bin/env python3
"""
Test script to send email via Microsoft Exchange OAuth
"""

import os
from datetime import datetime
from ms_ews_email_env import MsEwsClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_send_email():
    """Test sending an email with multiple recipients"""

    try:
        logger.info("=" * 80)
        logger.info("TESTING EXCHANGE EMAIL SENDING")
        logger.info("=" * 80)

        client = MsEwsClient()

        logger.info("Testing Exchange connection...")
        if not client.test_connection():
            logger.error("Connection test failed!")
            return False

        recipients = os.getenv("EWS_RECIPIENT_ADDRESS", "loeffler@v-und-s.de")
        logger.info(f"Recipients: {recipients}")

        test_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Test Email - Exchange OAuth Integration</h2>
            <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <h3>Test Information:</h3>
            <ul>
                <li><strong>From:</strong> {client.sender_address}</li>
                <li><strong>To:</strong> {recipients}</li>
                <li><strong>Server:</strong> {client.server}</li>
            </ul>

            <h3>Status:</h3>
            <p style="color: green; font-weight: bold;">✓ Exchange OAuth integration working successfully!</p>

            <hr>
            <p><small>This is an automated test email sent via Microsoft Exchange OAuth2 authentication.</small></p>
        </body>
        </html>
        """

        logger.info("Sending test email...")
        client.send_message(
            subject=f"Exchange OAuth Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            body=test_body,
            recipient=recipients,
            html_body=True
        )

        logger.info("=" * 80)
        logger.info("TEST EMAIL SENT SUCCESSFULLY!")
        logger.info("=" * 80)
        return True

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"TEST FAILED: {str(e)}")
        logger.error("=" * 80)
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_send_email()
    exit(0 if success else 1)