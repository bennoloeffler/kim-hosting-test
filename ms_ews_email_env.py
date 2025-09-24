"""
Microsoft Exchange Web Services (EWS) Email Client with OAuth2
Enhanced version that reads configuration from environment variables
"""

import os
import logging
from typing import Optional, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from exchangelib import (
    Configuration, Account, Message, Mailbox,
    FileAttachment, HTMLBody, OAUTH2, Identity,
    OAuth2AuthorizationCodeCredentials, IMPERSONATION
)
from exchangelib.protocol import BaseProtocol
import requests
from msal import ConfidentialClientApplication

# Load .env file (will NOT override existing shell environment variables)
load_dotenv(override=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MsEwsTokenProvider:
    """Provides OAuth2 access tokens for Microsoft Exchange"""

    @staticmethod
    def get_access_token(client_id: str, client_secret: str, tenant_id: str) -> str:
        """
        Get an access token using client credentials flow

        Args:
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret
            tenant_id: Azure AD tenant ID

        Returns:
            Access token string
        """
        authority = f"https://login.microsoftonline.com/{tenant_id}"

        app = ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret
        )

        # Scopes for EWS
        scopes = ["https://outlook.office365.com/.default"]

        result = app.acquire_token_for_client(scopes=scopes)

        if "access_token" in result:
            logger.info("Successfully acquired access token")
            return result["access_token"]
        else:
            error_msg = f"Failed to acquire token: {result.get('error_description', 'Unknown error')}"
            logger.error(error_msg)
            raise Exception(error_msg)


class OAuth2CredentialsWithToken(OAuth2AuthorizationCodeCredentials):
    """Custom OAuth2 credentials that uses a pre-fetched access token"""

    def __init__(self, access_token: str, identity: Identity, client_id: str, client_secret: str, tenant_id: str):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            identity=identity,
            access_token={
                'access_token': access_token,
                'token_type': 'Bearer'
            }
        )


class MsEwsClient:
    """Microsoft Exchange Web Services client with environment-based configuration"""

    def __init__(self):
        """Initialize client with configuration from environment variables"""
        self.client_id = os.getenv("EWS_CLIENT_ID")
        self.client_secret = os.getenv("EWS_CLIENT_SECRET")
        self.tenant_id = os.getenv("EWS_TENANT_ID")
        self.sender_address = os.getenv("EWS_SENDER_ADDRESS")
        self.recipient_address = os.getenv("EWS_RECIPIENT_ADDRESS")
        self.server = os.getenv("EWS_SERVER", "outlook.office365.com")

        # Validate configuration
        if not all([self.client_id, self.client_secret, self.tenant_id, self.sender_address]):
            raise ValueError("Missing required environment variables. Check .env.exchange file.")

        logger.info(f"Initialized EWS client for {self.sender_address}")

    def get_authenticated_account(self, token: str, email_address: str = None) -> Account:
        """
        Create an authenticated Exchange account

        Args:
            token: OAuth2 access token
            email_address: Email address of the mailbox to access (defaults to sender_address)

        Returns:
            Authenticated Account object
        """
        if email_address is None:
            email_address = self.sender_address

        credentials = OAuth2CredentialsWithToken(
            access_token=token,
            identity=Identity(primary_smtp_address=email_address),
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id
        )

        config = Configuration(
            server=self.server,
            credentials=credentials,
            auth_type=OAUTH2,
            version=None  # Auto-discover version
        )

        account = Account(
            primary_smtp_address=email_address,
            config=config,
            autodiscover=False,
            access_type=IMPERSONATION
        )

        return account

    def get_access_token(self) -> str:
        """
        Get OAuth2 access token

        Returns:
            Access token string
        """
        return MsEwsTokenProvider.get_access_token(
            self.client_id,
            self.client_secret,
            self.tenant_id
        )

    def send_message(self, subject: str, body: str, recipient: str = None, html_body: bool = True):
        """
        Send an email message

        Args:
            subject: Email subject
            body: Email body content
            recipient: Recipient email address(es) - can be string or comma-separated list
            html_body: Whether body is HTML (default) or plain text
        """
        if recipient is None:
            recipient = self.recipient_address

        recipients_list = []
        if isinstance(recipient, str):
            for email in recipient.split(','):
                email = email.strip()
                if email:
                    recipients_list.append(Mailbox(email_address=email))
        else:
            recipients_list.append(Mailbox(email_address=recipient))

        token = self.get_access_token()
        account = self.get_authenticated_account(token)

        msg = Message(
            account=account,
            subject=subject,
            body=HTMLBody(body) if html_body else body,
            to_recipients=recipients_list
        )

        msg.sender = Mailbox(email_address=self.sender_address)
        msg.send()

        recipient_names = ', '.join([r.email_address for r in recipients_list])
        logger.info(f"Message sent successfully to {recipient_names}")

    def read_inbox(self, limit: int = 10, folder_name: str = 'inbox'):
        """
        Read messages from a folder

        Args:
            limit: Maximum number of messages to retrieve
            folder_name: Folder to read from (default: 'inbox')

        Returns:
            List of message dictionaries
        """
        token = self.get_access_token()
        account = self.get_authenticated_account(token)

        folder = getattr(account, folder_name, account.inbox)
        messages = []

        for item in folder.all().order_by('-datetime_received')[:limit]:
            try:
                messages.append({
                    'subject': item.subject,
                    'from': item.sender.email_address if item.sender else 'Unknown',
                    'received': item.datetime_received.isoformat() if item.datetime_received else None,
                    'body': item.body[:200] if item.body else '',  # First 200 chars
                })
            except Exception as e:
                logger.error(f"Error processing item: {e}")

        return messages

    def test_connection(self):
        """Test the Exchange connection and authentication"""
        try:
            logger.info("Testing Exchange connection...")
            token = self.get_access_token()
            logger.info("✓ Successfully acquired access token")

            account = self.get_authenticated_account(token)
            logger.info(f"✓ Connected to account: {self.sender_address}")

            # Try to access inbox to verify permissions
            inbox_count = account.inbox.total_count
            logger.info(f"✓ Inbox access verified ({inbox_count} items)")

            return True
        except Exception as e:
            logger.error(f"✗ Connection test failed: {e}")
            return False


def main():
    """
    Example usage and testing
    """
    try:
        # Initialize client
        client = MsEwsClient()

        # Test connection
        if not client.test_connection():
            logger.error("Connection test failed. Check your credentials.")
            return

        # Send a test email
        logger.info("Sending test email...")
        client.send_message(
            subject="Test Email from Python EWS Client",
            body="<h1>Hello!</h1><p>This is a test email sent using OAuth2 authentication.</p>",
            html_body=True
        )

        # Read recent emails
        logger.info("Reading recent emails...")
        messages = client.read_inbox(limit=5)
        for msg in messages:
            logger.info(f"  - {msg['subject']} (from: {msg['from']})")

        logger.info("All operations completed successfully!")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()