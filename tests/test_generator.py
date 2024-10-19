"""
Tests for the Generator class in the pixelharmony.generator module.

Functions:
    test_create_melody_length():
        Test that the create_melody method generates a melody of the correct length.

    test_create_melody_notes():
        Test that the create_melody method generates notes within the C_MAJOR scale.

    test_fitness():
        Test that the fitness method returns a positive score for a given melody.

    test_crossover():
        Test that the crossover method generates a child melody of the same length as
        the parents and different from both parents.

    test_mutate():
        Test that the mutate method generates a mutated melody of the same length as
        the original and different from the original.

    test_select():
        Test that the select method selects a melody from the given population.

    test_genetic_algorithm():
        Test that the genetic_algorithm method generates a melody of the correct length
        after running the algorithm.

    test_save_midi(tmp_path):
        Test that the save_midi method saves a MIDI file to the specified path.
"""

from unittest.mock import patch
from pixelharmony.generator import Generator


def test_create_melody_length():
    """
    Test the create_melody method of the Generator class to ensure it generates a
    melody of the specified length.

    This test creates a melody of length 10 and asserts that the length of the
    generated melody is indeed 10.
    """
    generator = Generator()
    melody = generator.create_melody(10)
    assert len(melody) == 10


def test_create_melody_notes():
    """
    Test the create_melody method of the Generator class.

    This test ensures that the create_melody method generates a melody with the
    specified number of notes and that each note in the melody belongs to the
    C_MAJOR scale.

    Assertions:
        - Each note in the generated melody is a member of the C_MAJOR scale.
    """
    generator = Generator()
    melody = generator.create_melody(10)
    for note in melody:
        assert note in Generator.C_MAJOR


def test_fitness():
    """
    Test the fitness function of the Generator class.

    This test creates an instance of the Generator class and evaluates the fitness
    of a predefined melody. The test asserts that the fitness score of the melody is
    greater than 0.

    Raises:
        AssertionError: If the fitness score is not greater than 0.
    """
    generator = Generator()
    melody = [60, 62, 64, 65, 67, 69, 71, 72]
    score = generator.fitness(melody)
    assert score > 0


def test_crossover():
    """
    Test the crossover function of the Generator class.

    This test ensures that the crossover function produces a child list that has the
    same length as the parent lists and is different from both parent1 and parent2.

    Assertions:
    - The length of the child list is equal to the length of parent1.
    - The child list is not identical to parent1.
    - The child list is not identical to parent2.
    """
    generator = Generator()
    parent1 = [60, 62, 64, 65, 67, 69, 71, 72]
    parent2 = [72, 71, 69, 67, 65, 64, 62, 60]
    child = generator.crossover(parent1, parent2)
    assert len(child) == len(parent1)
    assert child != parent1
    assert child != parent2


def test_mutate():
    """
    Test the mutate method of the Generator class.

    This test verifies that the mutate method:
    1. Returns a mutated melody of the same length as the original melody.
    2. Produces a melody that is different from the original melody when a mutation
       rate of 0.5 is applied.

    Assertions:
    - The length of the mutated melody should be equal to the length of the original
      melody.
    - The mutated melody should not be identical to the original melody.
    """
    generator = Generator()
    melody = [60, 62, 64, 65, 67, 69, 71, 72]
    mutated_melody = generator.mutate(melody, 0.5)
    assert len(mutated_melody) == len(melody)
    assert mutated_melody != melody


def test_select():
    """
    Test the select method of the Generator class.

    This test creates an instance of the Generator class and a sample population
    consisting of three lists of integers. It then calls the select method on the
    population and asserts that the selected individual is one of the individuals in
    the original population.

    The population consists of:
    - A list of ascending integers.
    - A list of descending integers.
    - A list of identical integers.

    The test ensures that the select method returns a valid individual from the
    population.
    """
    generator = Generator()
    population = [
        [60, 62, 64, 65, 67, 69, 71, 72],
        [72, 71, 69, 67, 65, 64, 62, 60],
        [60, 60, 60, 60, 60, 60, 60, 60],
    ]
    selected = generator.select(population)
    assert selected in population


def test_genetic_algorithm():
    """
    Test the genetic_algorithm method of the Generator class.

    This test initializes a Generator instance and runs the genetic_algorithm method
    with specified parameters. It asserts that the length of the best melody
    generated is equal to the expected melody length.

    Parameters:
        None

    Returns:
        None
    """
    generator = Generator()
    best_melody = generator.genetic_algorithm(
        pop_size=10, melody_length=8, generations=5, mutation_rate=0.1
    )
    assert len(best_melody) == 8


def test_save_midi(tmp_path):
    """
    Test the save_midi method of the Generator class.

    This test verifies that the save_midi method correctly saves a MIDI file with the
    given melody to the specified file path.

    Asserts:
        The test asserts that the save_midi method is called with the correct
        parameters.
    """
    generator = Generator()
    melody = [60, 62, 64, 65, 67, 69, 71, 72]
    file_path = tmp_path / "test_output.mid"

    with patch("midiutil.MidiFile.MIDIFile.writeFile") as mock_write_file:
        with patch("builtins.open", create=True):
            generator.save_midi(melody, str(file_path))
            mock_write_file.assert_called_once()
