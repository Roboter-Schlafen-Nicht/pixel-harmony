import pytest
from pixelharmony.generator import Generator, DefaultFitnessFunction


def test_generator_initialization():
    generator = Generator()
    assert generator.tempo == 120
    assert generator.time_signature == (4, 4)
    assert isinstance(generator.fitness_function, DefaultFitnessFunction)


def test_create_random_melody():
    generator = Generator()
    melody = generator._create_random_melody(10)
    assert len(melody) == 10
    assert melody[0] in [60, 67]
    assert melody[-1] == 60


def test_evaluate_fitness():
    generator = Generator()
    melody = [60, 62, 64, 65, 67, 69, 71, 72]
    fitness = generator._evaluate_fitness(melody)
    assert fitness == 8.0


def test_create_melody():
    generator = Generator()
    melody = generator.create_melody(10, population_size=10, generations=10)
    assert len(melody) == 10


def test_save_midi(tmp_path):
    generator = Generator()
    melody = [60, 62, 64, 65, 67, 69, 71, 72]
    midi_file = tmp_path / "test_melody.mid"
    generator.save_midi(melody, midi_file)
    assert midi_file.exists()
