"""Module for handling Google Photos OAuth integration with Streamlit UI."""

import logging
import json
from datetime import datetime
import keyring
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests

# Configure logging
photos_logger = logging.getLogger("pixel_harmony.photos")
photos_logger.setLevel(logging.INFO)
if not photos_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    photos_logger.addHandler(handler)


class GooglePhotosAuth:
    """Handles Google Photos authentication and API interactions."""

    SCOPES = [
        "https://www.googleapis.com/auth/photoslibrary.readonly",
        "https://www.googleapis.com/auth/photoslibrary.sharing",
        "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata",
    ]
    KEYRING_SERVICE = "pixel_harmony_photos"
    KEYRING_USERNAME = "google_photos_creds"
    API_VERSION = "v1"
    PHOTOS_LIBRARY_API = "https://photoslibrary.googleapis.com"

    @staticmethod
    def _save_credentials(creds: Credentials) -> None:
        """Save credentials securely using keyring."""
        creds_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
            "expiry": creds.expiry.isoformat() if creds.expiry else None,
        }
        keyring.set_password(
            GooglePhotosAuth.KEYRING_SERVICE,
            GooglePhotosAuth.KEYRING_USERNAME,
            json.dumps(creds_data),
        )

    @staticmethod
    def _load_credentials() -> Credentials:
        """Load credentials from keyring."""
        try:
            creds_json = keyring.get_password(
                GooglePhotosAuth.KEYRING_SERVICE, GooglePhotosAuth.KEYRING_USERNAME
            )
            if not creds_json:
                return None

            creds_data = json.loads(creds_json)
            creds = Credentials(
                token=creds_data["token"],
                refresh_token=creds_data["refresh_token"],
                token_uri=creds_data["token_uri"],
                client_id=creds_data["client_id"],
                client_secret=creds_data["client_secret"],
                scopes=creds_data["scopes"],
            )
            if creds_data["expiry"]:
                creds.expiry = datetime.fromisoformat(creds_data["expiry"])
            return creds
        except (keyring.errors.KeyringError, json.JSONDecodeError) as e:
            photos_logger.error("Error loading credentials: %s", e)
            return None

    @staticmethod
    def has_valid_credentials() -> bool:
        """Check if valid credentials exist."""
        try:
            creds = GooglePhotosAuth._load_credentials()
            return creds is not None and creds.valid
        except (keyring.errors.KeyringError, json.JSONDecodeError):
            return False

    @staticmethod
    def clear_credentials() -> None:
        """Clear stored credentials."""
        try:
            keyring.delete_password(
                GooglePhotosAuth.KEYRING_SERVICE, GooglePhotosAuth.KEYRING_USERNAME
            )
        except keyring.errors.PasswordDeleteError:
            # Password might not exist
            pass

    @staticmethod
    def get_credentials():
        """Gets valid user credentials from secure storage or initiates OAuth2 flow."""
        creds = GooglePhotosAuth._load_credentials()

        # If credentials are invalid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secret.json", GooglePhotosAuth.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials securely
            GooglePhotosAuth._save_credentials(creds)

        return creds


class PhotosAPI:
    """Handles Google Photos API requests."""

    def __init__(self, credentials):
        """Initialize the Photos API handler with credentials."""
        self.credentials = credentials
        self.base_url = (
            f"{GooglePhotosAuth.PHOTOS_LIBRARY_API}/{GooglePhotosAuth.API_VERSION}"
        )

    def make_request(self, endpoint, method="GET", data=None, params=None):
        """Make an authenticated request to the Photos API."""
        headers = {
            "Authorization": f"Bearer {self.credentials.token}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/{endpoint}"
        photos_logger.info("Making %s request to %s", method, url)
        photos_logger.debug("Request data: %s", data)

        response = None
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)

            photos_logger.debug("Response status code: %s", response.status_code)
            response.raise_for_status()

            response_data = response.json()
            photos_logger.debug("Response data: %s", response_data)
            return response_data

        except requests.exceptions.RequestException as e:
            photos_logger.error("API request failed: %s", str(e))
            if hasattr(e.response, "text"):
                photos_logger.error("Error response: %s", e.response.text)
            raise
