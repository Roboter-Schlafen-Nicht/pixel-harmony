"""Main module for the Pixel Harmony package with mock player for testing environments."""

import os
import time
from abc import ABC, abstractmethod
from pixelharmony.generator import Generator


class BasePlayer(ABC):
    """Abstract base class for audio players."""

    @abstractmethod
    def play_note(self, midi_note, duration=0.5):
        """Play a single note."""
        pass

    @abstractmethod
    def play_melody(self, melody, note_duration=0.5):
        """Play a sequence of MIDI notes."""
        pass


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
        """Initialize audio player if possible."""
        self.sample_rate = sample_rate
        self.device = device
        self._initialize_audio()

    def _initialize_audio(self):
        """Try to initialize audio system."""
        try:
            import numpy as np
            import sounddevice as sd

            self.sd = sd
            self.np = np
            self.audio_available = True
        except (ImportError, OSError):
            print("Warning: Audio system not available")
            self.audio_available = False

    def play_note(self, midi_note, duration=0.5):
        """Play a note if audio is available."""
        if not self.audio_available:
            return

        try:
            frequency = 440 * (2 ** ((midi_note - 69) / 12))
            t = self.np.linspace(0, duration, int(self.sample_rate * duration), False)
            samples = self.np.sin(2 * self.np.pi * frequency * t) * 0.3
            self.sd.play(samples, self.sample_rate, device=self.device)
            self.sd.wait()
        except Exception as e:
            print(f"Warning: Could not play note: {e}")

    def play_melody(self, melody, note_duration=0.5):
        """Play melody if audio is available."""
        if not self.audio_available:
            return

        for note in melody:
            self.play_note(note, note_duration)
            time.sleep(0.1)


def create_player(testing=False):
    """Create appropriate player."""
    if testing:
        return MockPlayer()
    try:
        player = AudioPlayer()
        # Test if audio is working
        player.play_note(60, 0.1)
        return player
    except Exception as e:
        print(f"Warning: Audio system not available ({e}), using mock player")
        return MockPlayer()


def main(testing=False):
    """
    Generate and optionally play a melody.

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

        # Clean up file unless we're testing
        if not testing and os.path.exists(output_file):
            os.remove(output_file)

        return 0, melody

    except Exception as e:
        print(f"An error occurred: {e}")
        return 1, None


if __name__ == "__main__":
    exit_code, _ = main(testing=False)
    exit(exit_code)
