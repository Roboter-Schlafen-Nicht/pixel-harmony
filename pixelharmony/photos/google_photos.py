"""Module for handling Google Photos OAuth integration with Streamlit UI."""

import os
import json
from datetime import datetime
import keyring
from pathlib import Path
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests
import logging

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
                creds._expiry = datetime.fromisoformat(creds_data["expiry"])
            return creds
        except Exception as e:
            photos_logger.error(f"Error loading credentials: {e}")
            return None

    @staticmethod
    def has_valid_credentials() -> bool:
        """Check if valid credentials exist."""
        try:
            creds = GooglePhotosAuth._load_credentials()
            return creds is not None and creds.valid
        except Exception:
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

    def _make_request(self, endpoint, method="GET", data=None, params=None):
        """Make an authenticated request to the Photos API."""
        headers = {
            "Authorization": f"Bearer {self.credentials.token}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/{endpoint}"
        photos_logger.info(f"Making {method} request to {url}")
        photos_logger.debug(f"Request data: {data}")

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)

            photos_logger.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()

            response_data = response.json()
            photos_logger.debug(f"Response data: {response_data}")
            return response_data

        except requests.exceptions.RequestException as e:
            photos_logger.error(f"API request failed: {str(e)}")
            if hasattr(e.response, "text"):
                photos_logger.error(f"Error response: {e.response.text}")
            raise


class PhotosStreamlitUI:
    """Streamlit UI component for Google Photos integration."""

    def __init__(self):
        """Initialize the Photos UI component."""
        self.authenticated = False
        self.photos_api = None
        self._check_authentication()

    def _check_authentication(self):
        """Check if user is already authenticated."""
        try:
            if GooglePhotosAuth.has_valid_credentials():
                creds = GooglePhotosAuth.get_credentials()
                self.photos_api = PhotosAPI(creds)
                self.authenticated = True
                photos_logger.info("Successfully authenticated with Google Photos")
            else:
                self.authenticated = False
        except Exception as e:
            photos_logger.error(f"Error checking authentication: {e}")
            self.authenticated = False

    def render(self):
        """Render the Google Photos UI component."""
        st.header("Google Photos Integration")

        if not self.authenticated:
            st.warning("Not connected to Google Photos")
            if st.button("Connect to Google Photos"):
                try:
                    # Clear existing credentials to force new authentication
                    GooglePhotosAuth.clear_credentials()

                    with st.spinner("Connecting to Google Photos..."):
                        creds = GooglePhotosAuth.get_credentials()
                        self.photos_api = PhotosAPI(creds)
                        self.authenticated = True
                    st.success("Successfully connected to Google Photos!")
                    st.rerun()
                except Exception as e:
                    photos_logger.error(f"Error during authentication: {e}")
                    st.error("Failed to connect to Google Photos. Please try again.")
        else:
            st.success("Connected to Google Photos")
            if st.button("Disconnect"):
                try:
                    GooglePhotosAuth.clear_credentials()
                    self.authenticated = False
                    self.photos_api = None
                    st.rerun()
                except Exception as e:
                    photos_logger.error(f"Error during disconnect: {e}")
                    st.error("Failed to disconnect. Please try again.")

    def list_all_albums(self):
        """List all albums including shared ones."""
        if not self.authenticated:
            photos_logger.warning("Attempted to list albums while not authenticated")
            return None

        try:
            photos_logger.info("Fetching all albums")
            all_albums = []

            # Fetch owned albums
            owned_response = self.photos_api._make_request("albums", method="GET")
            if "albums" in owned_response:
                for album in owned_response["albums"]:
                    album["isShared"] = False
                all_albums.extend(owned_response["albums"])

            # Fetch shared albums
            shared_response = self.photos_api._make_request(
                "sharedAlbums", method="GET"
            )
            if "sharedAlbums" in shared_response:
                for album in shared_response["sharedAlbums"]:
                    album["isShared"] = True
                    # Store shareToken for later use
                    album["shareToken"] = album.get("shareToken", "")
                all_albums.extend(shared_response["sharedAlbums"])

            photos_logger.info(f"Found total of {len(all_albums)} albums")
            return all_albums

        except Exception as e:
            photos_logger.error(f"Error listing albums: {str(e)}")
            st.error(f"Failed to fetch albums: {str(e)}")
            return None

    def get_photos_from_album(self, album_id, is_shared=False, share_token=None):
        """Get photos from an album."""
        if not self.authenticated:
            return None

        try:
            photos_logger.info(
                f"Fetching photos from album {album_id} (shared: {is_shared})"
            )

            if is_shared:
                if not share_token:
                    photos_logger.error("Share token is required for shared albums")
                    return None

                # For shared albums, use the shareToken directly
                response = self.photos_api._make_request(
                    "mediaItems:search",
                    method="POST",
                    data={
                        "albumId": album_id,
                        "pageSize": 100,
                        "shareToken": share_token,
                    },
                )
            else:
                response = self.photos_api._make_request(
                    "mediaItems:search",
                    method="POST",
                    data={"albumId": album_id, "pageSize": 100},
                )

            photos = response.get("mediaItems", [])
            photos_logger.info(f"Found {len(photos)} photos in album")
            return photos

        except Exception as e:
            photos_logger.error(f"Error getting photos from album: {str(e)}")
            st.error(f"Failed to fetch photos: {str(e)}")
            return None


def initialize_photos_page():
    """Initialize the photos page in the Streamlit app."""
    st.set_page_config(page_title="Pixel Harmony - Photos", layout="wide")

    photos_ui = PhotosStreamlitUI()
    photos_ui.render()

    if photos_ui.authenticated:
        with st.spinner("Loading albums..."):
            albums = photos_ui.list_all_albums()

        if albums:
            st.subheader("Your Albums")
            selected_album = st.selectbox(
                "Select an album",
                options=albums,
                format_func=lambda x: f"{x.get('title', 'Untitled Album')} {'(Shared)' if x.get('isShared') else ''}",
            )

            if selected_album:
                with st.spinner("Loading photos..."):
                    photos = photos_ui.get_photos_from_album(
                        selected_album["id"],
                        is_shared=selected_album.get("isShared", False),
                        share_token=selected_album.get("shareToken"),
                    )

                if photos:
                    st.subheader(f"Photos in {selected_album['title']}")
                    cols = st.columns(3)
                    for idx, photo in enumerate(photos):
                        with cols[idx % 3]:
                            if "baseUrl" in photo:
                                st.image(
                                    photo["baseUrl"],
                                    caption=photo.get("filename", ""),
                                    use_container_width=True,
                                )
                                if st.button(
                                    f"Generate Melody from {photo.get('filename', 'Photo')}",
                                    key=photo["id"],
                                ):
                                    st.session_state["selected_photo"] = photo
                                    st.info(
                                        "Melody generation will be implemented in the next phase"
                                    )
                else:
                    st.warning("No photos found in this album")
        else:
            st.warning(
                "No albums found in your Google Photos account. Please make sure you have at least one album."
            )


if __name__ == "__main__":
    initialize_photos_page()
