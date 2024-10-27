"""A module for generating melodies using a genetic algorithm with fitness evaluation from FitnessGenerator."""

from abc import ABC, abstractmethod
import random
from typing import List
import logging
from midiutil.MidiFile import MIDIFile

# Create and configure loggers
genetic_logger = logging.getLogger("pixel_harmony.genetic")
genetic_logger.setLevel(logging.INFO)  # Set to INFO for genetic algorithm operations

# Create formatters and handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# File handler for all logs
file_handler = logging.FileHandler("pixel_harmony.log")
file_handler.setFormatter(formatter)

# Console handler for genetic operations
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Add handlers to loggers
genetic_logger.addHandler(file_handler)
genetic_logger.addHandler(console_handler)

# Set up logging
genetic_logger = logging.getLogger(__name__)


class BaseFitnessFunction(ABC):
    """Abstract base class for fitness functions."""

    @abstractmethod
    def fitness(self, melody: List[int]) -> float:
        """
        Evaluate the fitness of a melody.

        Args:
            melody: List of MIDI note numbers

        Returns:
            float: Fitness score
        """


class DefaultFitnessFunction(BaseFitnessFunction):
    """Default fitness function implementation."""

    def fitness(self, melody: List[int]) -> float:
        """Default fitness function that prefers notes in common ranges."""
        score = 0.0
        for note in melody:
            if 60 <= note <= 72:  # Common range
                score += 1.0
        return score


class Generator:
    """A class to generate melodies using a genetic algorithm with sophisticated fitness evaluation."""

    # Scale definitions
    C_MAJOR = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
    C_MINOR = [60, 62, 63, 65, 67, 68, 70, 72]  # C natural minor scale
    C_PENTATONIC = [60, 62, 64, 67, 69, 72]  # C major pentatonic scale
    C_MINOR_PENTATONIC = [60, 63, 65, 67, 70, 72]  # C minor pentatonic scale

    # Common chord progressions in C major
    COMMON_PROGRESSIONS = [
        [60, 64, 67],  # C major (I)
        [67, 71, 74],  # G major (V)
        [65, 69, 72],  # F major (IV)
        [62, 65, 69],  # D minor (ii)
        [65, 69, 72],  # E minor (iii)
        [65, 69, 72],  # A minor (vi)
    ]

    # Typical West African rhythmic patterns (as relative note lengths)
    RHYTHMIC_PATTERNS = [
        [2, 1, 1, 2, 2],  # Common 8-beat pattern
        [3, 3, 2],  # Typical triplet pattern
        [2, 2, 1, 1, 2],  # Syncopated pattern
    ]

    def __init__(
        self,
        key=None,
        mode=None,
        tempo=120,
        time_signature=(4, 4),
        fitness_function: BaseFitnessFunction = None,
    ):
        """Initialize the Generator with musical parameters."""
        self.key = key
        self.mode = mode
        self.tempo = tempo
        self.time_signature = time_signature
        self.scale = self.C_MAJOR
        self.fitness_function = fitness_function or DefaultFitnessFunction()

    def _evaluate_fitness(self, melody: List[int]) -> float:
        """Evaluate the fitness of a melody using the current fitness function."""
        genetic_logger.debug("Evaluating melody fitness")
        return self.fitness_function.fitness(melody)

    def _fallback_fitness(self, melody):
        """Fallback fitness function in case the generated one fails."""
        genetic_logger.debug("Using fallback fitness for melody: %s", melody)
        score = 0
        # Simple pentatonic scale adherence check
        for note in melody:
            if note in self.C_PENTATONIC:
                score += 1
        return score / len(melody) * 100

    def create_melody(
        self, length, population_size=100, generations=1000, mutation_rate=0.1
    ):
        """Generate a melody using the genetic algorithm with generated fitness function."""
        genetic_logger.debug(
            "Creating melody: length=%d, population_size=%d", length, population_size
        )

        try:
            # Initialize population
            population = self._initialize_population(length, population_size)
            genetic_logger.debug("Initialized population of size %d", len(population))

            generations_without_improvement = 0
            best_fitness = float("-inf")

            for gen in range(generations):
                try:
                    # Evaluate and sort population
                    population = sorted(
                        population, key=self._evaluate_fitness, reverse=True
                    )
                    current_best_fitness = self._evaluate_fitness(population[0])

                    if gen % 10 == 0:
                        genetic_logger.debug(
                            "Generation %d: Best fitness = %f",
                            gen,
                            current_best_fitness,
                        )

                    # Track improvement
                    if current_best_fitness > best_fitness:
                        best_fitness = current_best_fitness
                        generations_without_improvement = 0
                    else:
                        generations_without_improvement += 1

                    # Create new population
                    new_population = self._evolve_population(
                        population, population_size, mutation_rate
                    )
                    population = new_population

                    if generations_without_improvement > 100:
                        genetic_logger.debug(
                            "Early stopping due to lack of improvement"
                        )
                        break

                except (ValueError, TypeError, IndexError) as e:
                    genetic_logger.error("Error in generation %d: %s", gen, e)
                    break

            best_melody = max(population, key=self._evaluate_fitness)
            genetic_logger.debug("Final best melody: %s", best_melody)
            return best_melody

        except (ValueError, TypeError, IndexError, RuntimeError) as e:
            genetic_logger.error("Error in create_melody: %s", e)
            return self._create_random_melody(length)

    def _evolve_population(self, population, population_size, mutation_rate):
        """Evolve the population through selection, crossover, and mutation."""
        genetic_logger.debug("Evolving population")
        try:
            new_population = population[:2]  # Keep best 2

            while len(new_population) < population_size:
                if random.random() < 0.7:  # 70% crossover
                    parent1 = self._tournament_select(population)
                    parent2 = self._tournament_select(population)
                    child = self._crossover(parent1, parent2)
                else:  # 30% random new melody
                    child = self._create_random_melody(len(population[0]))

                child = self._mutate(child, mutation_rate)
                new_population.append(child)

            return new_population
        except (ValueError, TypeError, IndexError) as e:
            genetic_logger.error("Error in population evolution: %s", e)
            raise

    def _tournament_select(self, population, tournament_size=3):
        """Select individual using tournament selection."""
        genetic_logger.debug("Tournament selection with size %d", tournament_size)
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=self._evaluate_fitness)

    def _create_random_melody(self, length):
        """Create a random melody with musical constraints."""
        genetic_logger.debug("Creating random melody of length %d", length)
        melody = []
        for i in range(length):
            if i == 0:
                melody.append(random.choice([60, 67]))  # C or G
            elif i == length - 1:
                melody.append(60)  # C
            else:
                melody.append(random.choice(self.scale))
        return melody

    def _initialize_population(self, length, population_size):
        """Initialize a random population of melodies."""
        genetic_logger.debug(
            "Initializing population: length=%d, size=%d", length, population_size
        )
        return [self._create_random_melody(length) for _ in range(population_size)]

    def _crossover(self, parent1, parent2):
        """Perform crossover between two parent melodies."""
        genetic_logger.debug("Performing crossover")
        crossover_point = random.randint(1, len(parent1) - 1)
        return parent1[:crossover_point] + parent2[crossover_point:]

    def _mutate(self, melody, mutation_rate):
        """Mutate a melody by randomly changing notes."""
        genetic_logger.debug("Mutating melody with rate %f", mutation_rate)
        return [
            random.choice(self.scale) if random.random() < mutation_rate else note
            for note in melody
        ]

    def save_midi(self, melody, filename):
        """Save the melody as a MIDI file."""
        genetic_logger.debug("Saving MIDI file: %s", filename)
        try:
            midi = MIDIFile(1)
            track = 0
            time = 0
            midi.addTrackName(track, time, "Generated Melody")
            midi.addTempo(track, time, self.tempo)

            for i, pitch in enumerate(melody):
                midi.addNote(track, 0, pitch, time + i, 1, 100)

            with open(filename, "wb") as output_file:
                midi.writeFile(output_file)
            genetic_logger.debug("Successfully saved MIDI file")
        except Exception as e:
            genetic_logger.error("Error saving MIDI file: %s", e)
            raise
