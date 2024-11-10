"""Main module for the Pixel Harmony package with interactive audio device selection."""

import logging
import sys
import os
import time
from abc import ABC, abstractmethod
import json
import keyring
import requests
import numpy as np
import sounddevice as sd
import streamlit as st
from pixelharmony.generator import Generator
from pixelharmony.photos.google_photos import PhotosAPI, GooglePhotosAuth


class BasePlayer(ABC):
    """Abstract base class for audio players."""

    @abstractmethod
    def play_note(self, midi_note, duration=0.5):
        """Play a single note."""

    @abstractmethod
    def play_melody(self, melody, note_duration=0.5):
        """Play a sequence of MIDI notes."""


class MockPlayer(BasePlayer):
    """Mock player for testing environments."""

    def play_note(self, midi_note, duration=0.5):
        """Mock playing a note by printing."""
        print(f"Mock playing note: {midi_note} for {duration}s")

    def play_melody(self, melody, note_duration=0.5):
        """Mock playing a melody by printing."""
        print(f"Mock playing melody: {melody}")


class AudioPlayer(BasePlayer):
    """Real audio player using sounddevice."""

    def __init__(self, sample_rate=44100, device=None):
        """Initialize audio player with given sample rate and device."""
        self.sample_rate = sample_rate
        self.device = device
        self._initialize_audio()

    @staticmethod
    def list_devices():
        """List all available audio devices and return them."""
        devices = sd.query_devices()
        print("\nAvailable audio devices:")
        for i, device in enumerate(devices):
            # Show only output devices
            if device["max_output_channels"] > 0:
                print(
                    f"{i}: {device['name']} (Outputs: {device['max_output_channels']})"
                )
        return devices

    @staticmethod
    def test_device(device_id):
        """Test an audio device with a simple beep."""
        try:
            duration = 0.5
            t = np.linspace(0, duration, int(44100 * duration), False)
            test_tone = np.sin(2 * np.pi * 440 * t) * 0.3
            sd.play(test_tone, 44100, device=device_id)
            sd.wait()
            return True
        except sd.PortAudioError as e:
            print(f"PortAudio error testing device {device_id}: {e}")
            return False

    def _initialize_audio(self):
        """Try to initialize audio system."""
        try:
            self.audio_available = True
        except (ImportError, OSError):
            print("Warning: Audio system not available")
            self.audio_available = False

    def generate_sine_wave(self, frequency, duration):
        """Generate a sine wave at the given frequency and duration."""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        return np.sin(2 * np.pi * frequency * t)

    def midi_to_freq(self, midi_note):
        """Convert MIDI note number to frequency."""
        return 440 * (2 ** ((midi_note - 69) / 12))

    def play_note(self, midi_note, duration=0.5):
        """Play a note using a sine wave."""
        try:
            frequency = self.midi_to_freq(midi_note)
            samples = self.generate_sine_wave(frequency, duration)
            # Apply envelope
            envelope = np.exp(-3 * np.linspace(0, 1, len(samples)))
            samples *= envelope
        except sd.PortAudioError as e:
            print(f"PortAudio error playing note: {e}")

    def play_melody(self, melody, note_duration=0.5):
        """Play melody if audio is available."""
        print("\nPlaying melody...")
        for i, note in enumerate(melody):
            print(f"Playing note {i+1}/{len(melody)}: MIDI {note}")
            self.play_note(note, note_duration)
            time.sleep(0.1)


def select_audio_device():
    """Interactive function to select and test audio device."""
    devices = AudioPlayer.list_devices()

    while True:
        try:
            device_id = input(
                "\nEnter the number of the audio device to use (or 'q' to quit): "
            )
            if device_id.lower() == "q":
                return None

            device_id = int(device_id)
            if 0 <= device_id < len(devices):
                print(f"\nTesting device {device_id}...")
                if AudioPlayer.test_device(device_id):
                    proceed = (
                        input("Did you hear the test tone? (y/n): ").lower().strip()
                    )
                    if proceed == "y":
                        return device_id
                print("Let's try another device.")
            else:
                print("Invalid device number.")
        except ValueError:
            print("Please enter a valid number.")


def create_player(testing=False):
    """Create appropriate player."""
    if testing:
        return MockPlayer()

    try:
        # First select audio device
        print("Let's select an audio output device...")
        device_id = select_audio_device()
        if device_id is None:
            print("No audio device selected, using mock player")
            return MockPlayer()

        # Create audio player with selected device
        player = AudioPlayer(device=device_id)
        return player
    except (sd.PortAudioError, ValueError) as e:
        print(f"Warning: Audio system not available ({e}), using mock player")
        return MockPlayer()


def configure_logging():
    """Configure logging for different components of the application."""

    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler for all logs
    file_handler = logging.FileHandler("pixel_harmony.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)  # Capture all logs in file

    # Console handler for different levels
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)  # Show INFO and above in console

    # Configure API logger
    api_logger = logging.getLogger("pixel_harmony.api")
    api_logger.setLevel(logging.DEBUG)
    api_logger.addHandler(file_handler)
    api_logger.addHandler(console_handler)

    # Configure genetic algorithm logger
    genetic_logger = logging.getLogger("pixel_harmony.genetic")
    genetic_logger.setLevel(logging.DEBUG)
    genetic_logger.addHandler(file_handler)
    genetic_logger.addHandler(console_handler)

    # Prevent logs from propagating to root logger
    api_logger.propagate = False
    genetic_logger.propagate = False


def main(testing=False):
    """
    Main function to generate and play a melody.

    Args:
        testing (bool): If True, use mock player instead of real audio.

    Returns:
        tuple: (exit_code, melody) where exit_code is 0 for success and melody is the generated notes.
    """
    try:
        # Generate melody
        generator = Generator()
        print("Generating melody using genetic algorithm...")
        melody = generator.create_melody(
            length=16, population_size=50, generations=100, mutation_rate=0.1
        )

        output_file = "melody.mid"
        generator.save_midi(melody, output_file)
        print(f"Melody saved to {output_file}")

        # Create appropriate player
        player = create_player(testing)

        # Play or mock-play the melody
        player.play_melody(melody)

        # Ask about keeping the file
        keep_file = input("\nKeep MIDI file? (y/n): ").lower().strip() == "y"
        if not keep_file and os.path.exists(output_file):
            os.remove(output_file)
            print("MIDI file deleted")

        return 0, melody

    except (OSError, ValueError) as e:
        print(f"An error occurred: {e}")
        return 1, None


class PhotosStreamlitUI:
    """Streamlit UI component for Google Photos integration."""

    def __init__(self):
        """Initialize the Photos UI component."""
        self.authenticated = False
        self.photos_api = None
        # Configure logging

        # Create formatters
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # File handler for all logs
        file_handler = logging.FileHandler("pixel_harmony.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # Capture all logs in file

        # Console handler for different levels
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)  # Show INFO and above in console

        self.photos_logger = logging.getLogger("pixel_harmony.photos")
        self.photos_logger.setLevel(logging.INFO)
        self.photos_logger.addHandler(file_handler)
        self.photos_logger.addHandler(console_handler)
        self._check_authentication()

    def _check_authentication(self):
        """Check if user is already authenticated."""
        try:
            if GooglePhotosAuth.has_valid_credentials():
                creds = GooglePhotosAuth.get_credentials()
                self.photos_api = PhotosAPI(creds)
                self.authenticated = True
                self.photos_logger.info("Successfully authenticated with Google Photos")
            else:
                self.authenticated = False
        except (keyring.errors.KeyringError, json.JSONDecodeError) as e:
            self.photos_logger.error("Error checking authentication: %s", e)
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
                except (
                    keyring.errors.KeyringError,
                    json.JSONDecodeError,
                    requests.exceptions.RequestException,
                ) as e:
                    self.photos_logger.error("Error during authentication: %s", e)
                    st.error("Failed to connect to Google Photos. Please try again.")
        else:
            st.success("Connected to Google Photos")
            if st.button("Disconnect"):
                try:
                    GooglePhotosAuth.clear_credentials()
                    self.authenticated = False
                    self.photos_api = None
                    st.rerun()
                except keyring.errors.KeyringError as e:
                    self.photos_logger.error("Error during disconnect: %s", e)
                    st.error("Failed to disconnect. Please try again.")

    def list_all_albums(self):
        """List all albums including shared ones."""
        if not self.authenticated:
            self.photos_logger.warning(
                "Attempted to list albums while not authenticated"
            )
            return None

        try:
            self.photos_logger.info("Fetching all albums")
            all_albums = []

            # Fetch owned albums
            owned_response = self.photos_api.make_request("albums", method="GET")
            if "albums" in owned_response:
                for album in owned_response["albums"]:
                    album["isShared"] = False
                all_albums.extend(owned_response["albums"])

            # Fetch shared albums
            shared_response = self.photos_api.make_request("sharedAlbums", method="GET")
            if "sharedAlbums" in shared_response:
                for album in shared_response["sharedAlbums"]:
                    album["isShared"] = True
                    # Store shareToken for later use
                    album["shareToken"] = album.get("shareToken", "")
                all_albums.extend(shared_response["sharedAlbums"])

            self.photos_logger.info("Found total of %d albums", len(all_albums))
            return all_albums

        except requests.exceptions.RequestException as e:
            self.photos_logger.error("Error listing albums: %s", str(e))
            st.error(f"Failed to fetch albums: {str(e)}")
            return None

    def get_photos_from_album(self, album_id, is_shared=False, share_token=None):
        """Get photos from an album."""
        if not self.authenticated:
            return None

        try:
            self.photos_logger.info(
                "Fetching photos from album %s (shared: %s)", album_id, is_shared
            )

            if is_shared:
                if not share_token:
                    self.photos_logger.error(
                        "Share token is required for shared albums"
                    )
                    return None

                # For shared albums, use the shareToken directly
                response = self.photos_api.make_request(
                    "mediaItems:search",
                    method="POST",
                    data={
                        "albumId": album_id,
                        "pageSize": 100,
                        "shareToken": share_token,
                    },
                )
            else:
                response = self.photos_api.make_request(
                    "mediaItems:search",
                    method="POST",
                    data={"albumId": album_id, "pageSize": 100},
                )

            photos = response.get("mediaItems", [])
            self.photos_logger.info("Found %d photos in album", len(photos))
            return photos

        except requests.exceptions.RequestException as e:
            self.photos_logger.error("Error getting photos from album: %s", str(e))
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
