from unittest.mock import MagicMock, patch
import pytest
import json
from datetime import datetime, timedelta
import keyring
from google.oauth2.credentials import Credentials
import requests

from pixelharmony.photos.google_photos import GooglePhotosAuth, PhotosAPI


@pytest.fixture
def mock_credentials():
    creds = MagicMock(spec=Credentials)
    creds.token = "test_token"
    creds.refresh_token = "test_refresh_token"
    creds.token_uri = "https://oauth2.googleapis.com/token"
    creds.client_id = "test_client_id"
    creds.client_secret = "test_client_secret"
    creds.scopes = ["test_scope"]
    creds.expiry = datetime.now() + timedelta(hours=1)
    creds.valid = True
    return creds


@pytest.fixture
def mock_expired_credentials():
    creds = MagicMock(spec=Credentials)
    creds.valid = False
    creds.expired = True
    creds.refresh_token = "test_refresh_token"
    return creds


class TestGooglePhotosAuth:
    def test_save_credentials(self, mock_credentials):
        with patch("keyring.set_password") as mock_set_password:
            GooglePhotosAuth._save_credentials(mock_credentials)

            expected_creds_data = {
                "token": "test_token",
                "refresh_token": "test_refresh_token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "scopes": ["test_scope"],
                "expiry": mock_credentials.expiry.isoformat(),
            }

            mock_set_password.assert_called_once_with(
                GooglePhotosAuth.KEYRING_SERVICE,
                GooglePhotosAuth.KEYRING_USERNAME,
                json.dumps(expected_creds_data),
            )

    def test_load_credentials_success(self, mock_credentials):
        creds_data = {
            "token": "test_token",
            "refresh_token": "test_refresh_token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "scopes": ["test_scope"],
            "expiry": datetime.now().isoformat(),
        }

        with patch("keyring.get_password", return_value=json.dumps(creds_data)):
            loaded_creds = GooglePhotosAuth._load_credentials()
            assert loaded_creds.token == "test_token"
            assert loaded_creds.refresh_token == "test_refresh_token"
            assert loaded_creds.token_uri == "https://oauth2.googleapis.com/token"
            assert loaded_creds.client_id == "test_client_id"
            assert loaded_creds.client_secret == "test_client_secret"
            assert loaded_creds.scopes == ["test_scope"]

    def test_load_credentials_failure(self):
        with patch("keyring.get_password", side_effect=keyring.errors.KeyringError):
            assert GooglePhotosAuth._load_credentials() is None

    def test_has_valid_credentials(self, mock_credentials):
        with patch(
            "pixelharmony.photos.google_photos.GooglePhotosAuth._load_credentials",
            return_value=mock_credentials,
        ):
            assert GooglePhotosAuth.has_valid_credentials() is True

    def test_clear_credentials(self):
        with patch("keyring.delete_password") as mock_delete:
            GooglePhotosAuth.clear_credentials()
            mock_delete.assert_called_once_with(
                GooglePhotosAuth.KEYRING_SERVICE, GooglePhotosAuth.KEYRING_USERNAME
            )

    def test_get_credentials_refresh(self, mock_expired_credentials):
        with patch(
            "pixelharmony.photos.google_photos.GooglePhotosAuth._load_credentials",
            return_value=mock_expired_credentials,
        ) as mock_load:
            with patch(
                "pixelharmony.photos.google_photos.GooglePhotosAuth._save_credentials"
            ) as mock_save:
                with patch.object(mock_expired_credentials, "refresh") as mock_refresh:
                    creds = GooglePhotosAuth.get_credentials()

                    mock_load.assert_called_once()
                    mock_refresh.assert_called_once()
                    mock_save.assert_called_once()
                    assert creds == mock_expired_credentials


class TestPhotosAPI:
    def test_make_request_get(self, mock_credentials):
        api = PhotosAPI(mock_credentials)
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.status_code = 200

        with patch("requests.get", return_value=mock_response) as mock_get:
            result = api.make_request("test_endpoint", method="GET")

            mock_get.assert_called_once_with(
                f"{GooglePhotosAuth.PHOTOS_LIBRARY_API}/{GooglePhotosAuth.API_VERSION}/test_endpoint",
                headers={
                    "Authorization": "Bearer test_token",
                    "Content-Type": "application/json",
                },
                params=None,
                timeout=10,
            )
            assert result == {"test": "data"}

    def test_make_request_post(self, mock_credentials):
        api = PhotosAPI(mock_credentials)
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.status_code = 200
        test_data = {"key": "value"}

        with patch("requests.post", return_value=mock_response) as mock_post:
            result = api.make_request("test_endpoint", method="POST", data=test_data)

            mock_post.assert_called_once_with(
                f"{GooglePhotosAuth.PHOTOS_LIBRARY_API}/{GooglePhotosAuth.API_VERSION}/test_endpoint",
                headers={
                    "Authorization": "Bearer test_token",
                    "Content-Type": "application/json",
                },
                json=test_data,
                timeout=10,
            )
            assert result == {"test": "data"}

    def test_make_request_error(self, mock_credentials):
        api = PhotosAPI(mock_credentials)
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.RequestException()
        )

        with patch("requests.get", return_value=mock_response):
            with pytest.raises(requests.exceptions.RequestException):
                api.make_request("test_endpoint")
