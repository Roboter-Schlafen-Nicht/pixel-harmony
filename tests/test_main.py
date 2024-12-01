"""Tests for the main module functionality."""

import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import sounddevice as sd
import os
from main import (
    main,
    AudioPlayer,
    MockPlayer,
    create_player,
    select_audio_device,
    BasePlayer,
)


@pytest.fixture
def mock_sounddevice():
    """Fixture to mock sounddevice functionality."""
    with patch("sounddevice.play") as mock_play, patch(
        "sounddevice.wait"
    ) as mock_wait, patch("sounddevice.query_devices") as mock_query:
        # Mock audio devices
        mock_query.return_value = [
            {"name": "Test Device 1", "max_output_channels": 2},
            {"name": "Test Device 2", "max_output_channels": 2},
        ]
        yield {"play": mock_play, "wait": mock_wait, "query": mock_query}


@pytest.fixture
def mock_generator():
    """Fixture for mocked Generator."""
    with patch("main.Generator") as mock_gen:  # Updated import path
        mock_instance = MagicMock()
        mock_instance.create_melody.return_value = [60, 62, 64, 65]
        mock_gen.return_value = mock_instance
        yield mock_gen


@pytest.fixture
def audio_player():
    """Fixture to provide an AudioPlayer instance."""
    return AudioPlayer(sample_rate=44100, device=0)


@pytest.fixture
def mock_player():
    """Fixture to provide a MockPlayer instance."""
    return MockPlayer()


@pytest.fixture
def test_melody():
    """Fixture to provide a test melody."""
    return [60, 62, 64, 65, 67, 69, 71, 72]


class TestMockPlayer:
    """Tests for MockPlayer functionality."""

    def test_mock_player_play_note(self, mock_player, capsys):
        """Test MockPlayer's play_note method."""
        mock_player.play_note(60, 0.5)
        captured = capsys.readouterr()
        assert "Mock playing note: 60" in captured.out

    def test_mock_player_play_melody(self, mock_player, test_melody, capsys):
        """Test MockPlayer's play_melody method."""
        mock_player.play_melody(test_melody)
        captured = capsys.readouterr()
        assert "Mock playing melody" in captured.out
        assert str(test_melody) in captured.out


class TestAudioPlayer:
    """Tests for AudioPlayer functionality."""

    def test_audio_player_initialization(self, audio_player):
        """Test AudioPlayer initialization."""
        assert audio_player.sample_rate == 44100
        assert audio_player.device == 0

    def test_midi_to_freq_conversion(self, audio_player):
        """Test MIDI note to frequency conversion."""
        assert abs(audio_player.midi_to_freq(69) - 440.0) < 0.01
        assert abs(audio_player.midi_to_freq(57) - 220.0) < 0.01

    def test_sine_wave_generation(self, audio_player):
        """Test sine wave generation."""
        frequency = 440
        duration = 0.1
        wave = audio_player.generate_sine_wave(frequency, duration)
        assert len(wave) == int(audio_player.sample_rate * duration)
        assert -1 <= max(wave) <= 1
        assert -1 <= min(wave) <= 1

    def test_list_devices(self, mock_sounddevice):
        """Test device listing functionality."""
        devices = AudioPlayer.list_devices()
        assert len(devices) == 2
        mock_sounddevice["query"].assert_called_once()

    @pytest.mark.parametrize("device_id,should_succeed", [(0, True), (99, False)])
    def test_test_device(self, mock_sounddevice, device_id, should_succeed):
        """Test device testing functionality."""
        with patch("sounddevice.play") as mock_play:
            if device_id == 99:
                mock_play.side_effect = sd.PortAudioError("Invalid device")

            result = AudioPlayer.test_device(device_id)
            assert result == should_succeed


class TestDeviceSelection:
    """Tests for device selection functionality."""

    @patch("builtins.input")
    def test_select_audio_device_success(self, mock_input, mock_sounddevice):
        """Test successful audio device selection."""
        mock_input.side_effect = ["0", "y"]
        device_id = select_audio_device()
        assert device_id == 0

    @patch("builtins.input")
    def test_select_audio_device_quit(self, mock_input, mock_sounddevice):
        """Test quitting device selection."""
        mock_input.return_value = "q"
        device_id = select_audio_device()
        assert device_id is None

    @patch("builtins.input")
    def test_select_audio_device_retry(self, mock_input, mock_sounddevice):
        """Test retrying device selection after failure."""
        mock_input.side_effect = ["0", "n", "1", "y"]
        device_id = select_audio_device()
        assert device_id == 1


class TestMainFunction:
    """Tests for main function."""

    @patch("main.create_player")  # Updated import path
    @patch("builtins.input")
    def test_main_function_testing_mode(
        self, mock_input, mock_create_player, mock_generator
    ):
        """Test main function in testing mode."""
        # Setup
        mock_player = MockPlayer()
        mock_create_player.return_value = mock_player
        mock_input.return_value = "n"  # Don't keep the file

        # Execute
        exit_code, melody = main(testing=True)

        # Assert
        assert exit_code == 0
        assert melody == [60, 62, 64, 65]
        mock_generator.return_value.create_melody.assert_called_once()

    @patch("main.create_player")  # Updated import path
    @patch("builtins.input")
    @patch("os.path.exists")
    @patch("os.remove")
    def test_main_function_file_handling(
        self, mock_remove, mock_exists, mock_input, mock_create_player, mock_generator
    ):
        """Test MIDI file handling in main function."""
        # Setup
        mock_player = MockPlayer()
        mock_create_player.return_value = mock_player
        mock_input.return_value = "n"  # Don't keep the file
        mock_exists.return_value = True  # File exists

        # Execute
        exit_code, _ = main(testing=True)

        # Assert
        assert exit_code == 0
        mock_remove.assert_called_once_with("melody.mid")


def test_create_player_testing_mode():
    """Test player creation in testing mode."""
    player = create_player(testing=True)
    assert isinstance(player, MockPlayer)


@patch("main.select_audio_device")  # Updated import path
def test_create_player_no_device_selected(mock_select):
    """Test player creation when no audio device is selected."""
    mock_select.return_value = None
    player = create_player(testing=False)
    assert isinstance(player, MockPlayer)
