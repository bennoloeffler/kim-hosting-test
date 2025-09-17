"""
Microsoft Exchange Web Services (EWS) Email Client with OAuth2
Python translation of the Java EWS OAuth implementation
"""

import logging
from typing import Optional, List
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from exchangelib import (
    Configuration, Account, Message, Mailbox,
    FileAttachment, HTMLBody, OAUTH2, Identity,
    OAuth2AuthorizationCodeCredentials, IMPERSONATION
)
from exchangelib.protocol import BaseProtocol
import requests
from msal import ConfidentialClientApplication

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

    def __init__(self, access_token: str, identity: Identity, client_id: str, client_secret: str):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=None,
            identity=identity
        )
        self.access_token = access_token

    def refresh(self, session):
        # In production, implement token refresh logic here
        return self.access_token


class MsEwsMain:
    """Main class for Microsoft Exchange Web Services operations"""

    # Configuration - replace with your values or load from environment
    CLIENT_ID = "0247f6b2-5b9f-4704-941a-47cf8de9fef8"
    CLIENT_SECRET = "Tx.UZm-9jnQ.pb442MVIAR7_.29D6G9yMD"
    TENANT_ID = "18eb4642-9f05-4071-b559-6f7d33824220"
    RECIPIENT_ADDRESS = "loeffler@v-und-s.de"
    SENDER_ADDRESS = "crm@v-und-s.de"

    @classmethod
    def get_authenticated_service(cls, token: str, email_address: str) -> Account:
        """
        Create an authenticated Exchange service/account

        Args:
            token: OAuth2 access token
            email_address: Email address of the mailbox to access

        Returns:
            Authenticated Account object
        """
        credentials = OAuth2CredentialsWithToken(
            access_token=token,
            identity=Identity(primary_smtp_address=email_address),
            client_id=cls.CLIENT_ID,
            client_secret=cls.CLIENT_SECRET
        )

        config = Configuration(
            server='outlook.office365.com',
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

    @classmethod
    def get_auth_exchange_service(cls) -> Account:
        """
        Get an ExchangeService with OAuth, without password

        Returns:
            Authenticated Account object
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                MsEwsTokenProvider.get_access_token,
                cls.CLIENT_ID,
                cls.CLIENT_SECRET,
                cls.TENANT_ID
            )
            token = future.result()

        return cls.get_authenticated_service(token, cls.SENDER_ADDRESS)

    @staticmethod
    def send_test_message(account: Account, recipient_addr: str, sender_addr: str):
        """
        Send a test email message

        Args:
            account: Authenticated Account object
            recipient_addr: Recipient email address
            sender_addr: Sender email address
        """
        msg = Message(
            account=account,
            subject='Hello world!',
            body=HTMLBody('Sent using the Python exchangelib library with OAuth2.'),
            to_recipients=[Mailbox(email_address=recipient_addr)]
        )

        # Set sender if different from account
        msg.sender = Mailbox(email_address=sender_addr)

        msg.send()
        logger.info(f"Message sent successfully to {recipient_addr}")

    @staticmethod
    def list_inbox_messages(account: Account, limit: int = 50):
        """
        List messages from the inbox

        Args:
            account: Authenticated Account object
            limit: Maximum number of messages to retrieve
        """
        inbox = account.inbox

        # Get the most recent messages
        for item in inbox.all().order_by('-datetime_received')[:limit]:
            try:
                logger.info(f"Subject: {item.subject}")
                logger.info(f"  From: {item.sender.email_address if item.sender else 'Unknown'}")
                logger.info(f"  Received: {item.datetime_received}")
                logger.info("-" * 50)
            except Exception as e:
                logger.error(f"Error processing item: {e}")

    @classmethod
    def main(cls):
        """
        Entry point for testing
        """
        logger.info("Starting Microsoft Exchange EWS OAuth2 client")

        with ThreadPoolExecutor(max_workers=1) as executor:
            # Get access token
            future = executor.submit(
                MsEwsTokenProvider.get_access_token,
                cls.CLIENT_ID,
                cls.CLIENT_SECRET,
                cls.TENANT_ID
            )
            token = future.result()

            # Don't log this in production!
            logger.debug(f"Token acquired (length: {len(token)} chars)")

            # Test mailbox read access
            logger.info("Getting emails from inbox...")
            try:
                account = cls.get_authenticated_service(token, cls.SENDER_ADDRESS)
                cls.list_inbox_messages(account)
            except Exception as e:
                logger.error(f"Error reading inbox: {e}")

            # Send a test message
            logger.info("Sending a test message...")
            try:
                account = cls.get_authenticated_service(token, cls.SENDER_ADDRESS)
                cls.send_test_message(account, cls.RECIPIENT_ADDRESS, cls.SENDER_ADDRESS)
            except Exception as e:
                logger.error(f"Error sending message: {e}")

        logger.info("Finished")


if __name__ == "__main__":
    # Run the main function
    MsEwsMain.main()