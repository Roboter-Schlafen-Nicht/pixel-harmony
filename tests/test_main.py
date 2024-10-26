"""Tests for the main module functionality."""

import pytest
from unittest.mock import patch, MagicMock
from main import main, AudioPlayer, create_player, MockPlayer


def test_mock_player():
    """Test mock player functionality."""
    player = MockPlayer()
    melody = [60, 62, 64, 65]

    # Should not raise any exceptions
    player.play_note(60)
    player.play_melody(melody)


@patch("main.AudioPlayer")
def test_create_player_with_audio_error(mock_audio):
    """Test player creation when audio is unavailable."""
    mock_audio.side_effect = OSError("PortAudio library not found")
    player = create_player(testing=False)
    assert isinstance(player, MockPlayer)


@patch("main.Generator")
def test_main_function(mock_generator):
    """Test main function with mocked Generator."""
    # Mock the generator to return a predictable melody
    mock_instance = MagicMock()
    mock_instance.create_melody.return_value = [60, 62, 64, 65]
    mock_generator.return_value = mock_instance

    # Run main in testing mode
    exit_code, melody = main(testing=True)

    assert exit_code == 0
    assert melody == [60, 62, 64, 65]
    mock_instance.create_melody.assert_called_once()


def test_main_with_error():
    """Test main function error handling."""
    with patch("main.Generator") as mock_generator:
        mock_generator.side_effect = Exception("Test error")
        exit_code, melody = main(testing=True)
        assert exit_code == 1
        assert melody is None


@pytest.mark.skipif(
    True,  # Skip audio device tests in CI environment
    reason="Audio device tests not supported in CI environment",
)
class TestAudioPlayer:
    """Tests for AudioPlayer that require audio hardware."""

    def test_audio_player_initialization(self):
        """Test AudioPlayer initialization."""
        player = AudioPlayer()
        assert player.sample_rate == 44100

    def test_play_note(self):
        """Test playing a single note."""
        player = AudioPlayer()
        player.play_note(60, duration=0.1)  # Very short duration for testing

    def test_play_melody(self):
        """Test playing a melody."""
        player = AudioPlayer()
        player.play_melody([60, 62, 64], note_duration=0.1)
