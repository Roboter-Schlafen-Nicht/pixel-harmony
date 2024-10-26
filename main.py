""" Main module for the Pixel Harmony package. """

from pixelharmony.generator import Generator


def main():
    """
    Main function to generate a melody and save it as a MIDI file.

    This function creates an instance of the Generator class, uses it to create
    a melody with a length of 16, and then saves the generated melody to a file
    named "melody.mid".

    Returns:
        int: Always returns 0.
    """
    generator = Generator()
    melody = generator.create_melody(16)
    generator.save_midi(melody, "melody.mid")
    return 0


if __name__ == "__main__":
    exit(main())
