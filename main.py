""" Main module for the Pixel Harmony package with audio device selection. """

import os
import time
import numpy as np
import sounddevice as sd
from pixelharmony.generator import Generator


class AudioPlayer:
    """A class to handle audio playback using sounddevice with device selection."""

    def __init__(self, sample_rate=44100, device=None):
        """Initialize audio player with given sample rate and device."""
        self.sample_rate = sample_rate
        self.device = device

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
            # Generate a simple test tone
            duration = 0.5
            t = np.linspace(0, duration, int(44100 * duration), False)
            test_tone = np.sin(2 * np.pi * 440 * t) * 0.3

            # Try to play it
            sd.play(test_tone, 44100, device=device_id)
            sd.wait()
            return True
        except Exception as e:
            print(f"Error testing device {device_id}: {e}")
            return False

    def generate_sine_wave(self, frequency, duration):
        """Generate a sine wave at the given frequency and duration."""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        return np.sin(2 * np.pi * frequency * t)

    def midi_to_freq(self, midi_note):
        """Convert MIDI note number to frequency."""
        return 440 * (2 ** ((midi_note - 69) / 12))

    def play_note(self, midi_note, duration=0.5):
        """Play a single note using a sine wave."""
        try:
            frequency = self.midi_to_freq(midi_note)
            samples = self.generate_sine_wave(frequency, duration)
            # Apply envelope
            envelope = np.exp(-3 * np.linspace(0, 1, len(samples)))
            samples = samples * envelope * 0.3
            # Play the note
            sd.play(samples, self.sample_rate, device=self.device)
            sd.wait()
        except sd.PortAudioError as e:
            print(f"Audio playback error: {e}")

    def play_melody(self, melody, note_duration=0.5):
        """Play a sequence of MIDI notes."""
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


def main():
    """Main function to generate and play a melody with device selection."""
    try:
        # First, select audio device
        print("Let's select an audio output device...")
        device_id = select_audio_device()
        if device_id is None:
            print("Audio device selection cancelled.")
            return 1

        # Generate melody
        generator = Generator()
        print("\nGenerating melody using genetic algorithm...")
        melody = generator.create_melody(
            length=16, population_size=50, generations=1000, mutation_rate=0.1
        )

        output_file = "melody.mid"
        generator.save_midi(melody, output_file)
        print(f"Melody saved to {output_file}")

        # Play the melody with selected device
        player = AudioPlayer(device=device_id)
        player.play_melody(melody)

        # Optional: Keep MIDI file?
        keep_file = input("\nKeep MIDI file? (y/n): ").lower().strip() == "y"
        if not keep_file and os.path.exists(output_file):
            os.remove(output_file)
            print("MIDI file deleted")

        return 0

    except Exception as e:
        print(f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
