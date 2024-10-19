"""A module for generating melodies using a genetic algorithm.

Classes:
    Generator: A class to generate melodies using a genetic algorithm."""

import random
from midiutil.MidiFile import MIDIFile


class Generator:
    """
    A class to generate melodies using a genetic algorithm.

    Attributes:
        C_MAJOR (list): MIDI note numbers for the C major scale.
        C_MINOR (list): MIDI note numbers for the C minor scale.
        G_MAJOR (list): MIDI note numbers for the G major scale.
        G_MINOR (list): MIDI note numbers for the G minor scale.
        D_MAJOR (list): MIDI note numbers for the D major scale.
        D_MINOR (list): MIDI note numbers for the D minor scale.
        A_MAJOR (list): MIDI note numbers for the A major scale.
        A_MINOR (list): MIDI note numbers for the A minor scale.
        E_MAJOR (list): MIDI note numbers for the E major scale.
        E_MINOR (list): MIDI note numbers for the E minor scale.
        B_MAJOR (list): MIDI note numbers for the B major scale.
        B_MINOR (list): MIDI note numbers for the B minor scale.
        F_MAJOR (list): MIDI note numbers for the F major scale.
        F_MINOR (list): MIDI note numbers for the F minor scale.
        SHARP_KEYS (list): List of major scales with sharps.
        FLAT_KEYS (list): List of major scales with flats.
        SHARP_MINOR_KEYS (list): List of minor scales with sharps.
        FLAT_MINOR_KEYS (list): List of minor scales with flats.
        MAJOR_KEYS (list): List of all major scales.
        MINOR_KEYS (list): List of all minor scales.

    Methods:
        __init__(self, key=None, mode=None, tempo=120, time_signature=(4, 4)):
            Initializes the Generator with the given key, mode, tempo, and time
            signature.

        create_melody(self, length):
            Creates a random melody of the given length using the C major scale.

        fitness(self, melody):
            Evaluates the fitness of a melody based on note repetition and interval
            size.

        crossover(self, parent1, parent2):
            Performs crossover between two parent melodies to produce a child melody.

        mutate(self, melody, mutation_rate):
            Mutates a melody based on the given mutation rate.

        select(self, population, k=3):
            Selects the best melody from a random sample of the population.

        genetic_algorithm(self, pop_size, melody_length, generations, mutation_rate):
            Runs the genetic algorithm to evolve melodies over a number of generations.

        save_midi(self, melody, filename):
            Saves a melody as a MIDI file with the given filename.
    """

    C_MAJOR = [60, 62, 64, 65, 67, 69, 71, 72]
    C_MINOR = [60, 62, 63, 65, 67, 68, 70, 72]
    G_MAJOR = [72, 74, 76, 77, 79, 81, 83, 84]
    G_MINOR = [72, 74, 75, 77, 79, 80, 82, 84]
    D_MAJOR = [57, 59, 61, 62, 64, 66, 68, 69]
    D_MINOR = [57, 59, 60, 62, 64, 65, 67, 69]
    A_MAJOR = [54, 56, 58, 59, 61, 63, 65, 66]
    A_MINOR = [54, 56, 57, 59, 61, 62, 64, 66]
    E_MAJOR = [51, 53, 55, 56, 58, 60, 62, 63]
    E_MINOR = [51, 53, 54, 56, 58, 59, 61, 63]
    B_MAJOR = [48, 50, 52, 53, 55, 57, 59, 60]
    B_MINOR = [48, 50, 51, 53, 55, 56, 58, 60]
    F_MAJOR = [45, 47, 49, 50, 52, 54, 56, 57]
    F_MINOR = [45, 47, 48, 50, 52, 53, 55, 57]
    SHARP_KEYS = [G_MAJOR, D_MAJOR, A_MAJOR, E_MAJOR, B_MAJOR]
    FLAT_KEYS = [C_MAJOR, F_MAJOR]
    SHARP_MINOR_KEYS = [G_MINOR, D_MINOR, A_MINOR, E_MINOR, B_MINOR]
    FLAT_MINOR_KEYS = [C_MINOR, F_MINOR]
    MAJOR_KEYS = SHARP_KEYS + FLAT_KEYS
    MINOR_KEYS = SHARP_MINOR_KEYS + FLAT_MINOR_KEYS

    def __init__(self, key=None, mode=None, tempo=120, time_signature=(4, 4)):
        self.key = key
        self.mode = mode
        self.tempo = tempo
        self.time_signature = time_signature

    def create_melody(self, length):
        """
        Generates a melody of a specified length using random notes from the C major
        scale.

        Args:
            length (int): The number of notes in the generated melody.

        Returns:
            list: A list of randomly chosen notes from the C major scale.
        """
        return [random.choice(Generator.C_MAJOR) for _ in range(length)]

    def fitness(self, melody):
        """
        Evaluate the fitness of a given melody.

        This function calculates a fitness score for a melody based on two criteria:
        1. Reward for not repeating the same note consecutively.
        2. Reward for having small intervals between consecutive notes (intervals of 4
        or less).

        Args:
            melody (list of int): A list of integers representing the melody notes.

        Returns:
            int: The fitness score of the melody.
        """
        # This is a simple fitness function. You might want to make this more
        # sophisticated.
        score = 0
        for i in range(len(melody) - 1):
            # Reward for not repeating the same note
            if melody[i] != melody[i + 1]:
                score += 1
            # Reward for small intervals
            if abs(melody[i] - melody[i + 1]) <= 4:
                score += 1
        return score

    def crossover(self, parent1, parent2):
        """
        Perform a crossover operation between two parent sequences to produce a child
        sequence.

        Args:
            parent1 (list): The first parent sequence.
            parent2 (list): The second parent sequence.

        Returns:
            list: A child sequence created by combining parts of the two parent
            sequences.
        """
        point = random.randint(1, len(parent1) - 1)
        child = parent1[:point] + parent2[point:]
        return child

    def mutate(self, melody, mutation_rate):
        """
        Mutates a given melody by randomly changing some of its notes based on a
        mutation rate.

        Args:
            melody (list): A list of notes representing the melody to be mutated.
            mutation_rate (float): A probability value between 0 and 1 that determines
            the likelihood of each note being mutated.

        Returns:
            list: A new list representing the mutated melody.
        """
        return [
            (
                random.choice(Generator.C_MAJOR)
                if random.random() < mutation_rate
                else note
            )
            for note in melody
        ]

    def select(self, population, k=3):
        """
        Selects the best individual from a randomly chosen subset of the population.

        Args:
            population (list): The population from which to select individuals.
            k (int, optional): The number of individuals to randomly sample from the
            population. Defaults to 3.

        Returns:
            The individual with the highest fitness from the sampled subset.
        """
        return max(random.sample(population, k), key=self.fitness)

    def genetic_algorithm(self, pop_size, melody_length, generations, mutation_rate):
        """
        Executes a genetic algorithm to evolve a population of melodies.

        Args:
            pop_size (int): The size of the population.
            melody_length (int): The length of each melody.
            generations (int): The number of generations to run the algorithm.
            mutation_rate (float): The probability of mutation for each melody.

        Returns:
            list: The best melody found after the specified number of generations.
        """
        population = [self.create_melody(melody_length) for _ in range(pop_size)]

        for gen in range(generations):
            population = sorted(population, key=self.fitness, reverse=True)

            new_population = population[:2]  # Keep the two best melodies

            while len(new_population) < pop_size:
                parent1 = self.select(population)
                parent2 = self.select(population)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child, mutation_rate)
                new_population.append(child)

            population = new_population

            print(f"Generation {gen}: Best fitness = {self.fitness(population[0])}")

        return population[0]

    def save_midi(self, melody, filename):
        """
        Saves a melody as a MIDI file.

        Args:
            melody (list of int): A list of MIDI pitch values representing the melody.
            filename (str): The name of the file to save the MIDI data to.

        Example:
            melody = [60, 62, 64, 65, 67, 69, 71, 72]
            save_midi(melody, "output.mid")
        """
        midi = MIDIFile(1)
        track = 0
        time = 0
        midi.addTrackName(track, time, "Sample Track")
        midi.addTempo(track, time, 120)

        for i, pitch in enumerate(melody):
            midi.addNote(track, 0, pitch, time + i, 1, 100)

        with open(filename, "wb") as output_file:
            midi.writeFile(output_file)
