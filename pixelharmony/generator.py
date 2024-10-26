"""A module for generating melodies using a genetic algorithm with enhanced musical fitness evaluation."""

import random
from midiutil.MidiFile import MIDIFile


class Generator:
    """A class to generate melodies using a genetic algorithm with sophisticated fitness evaluation."""

    # Scale definitions
    C_MAJOR = [60, 62, 64, 65, 67, 69, 71, 72]
    C_MINOR = [60, 62, 63, 65, 67, 68, 70, 72]

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

    def __init__(self, key=None, mode=None, tempo=120, time_signature=(4, 4)):
        """Initialize the Generator with musical parameters."""
        self.key = key
        self.mode = mode
        self.tempo = tempo
        self.time_signature = time_signature
        self.scale = self.C_MAJOR

    def _evaluate_fitness(self, melody):
        """
        Enhanced fitness function that evaluates musical qualities of a melody.

        Evaluates:
        1. Melodic contour and shape
        2. Rhythmic interest
        3. Harmonic relationships
        4. Phrase structure
        5. Musical tension and resolution
        6. Cultural elements (West African music characteristics)
        """
        score = 0

        # 1. Melodic Contour Analysis (0-20 points)
        score += self._evaluate_contour(melody)

        # 2. Rhythmic Interest (0-20 points)
        score += self._evaluate_rhythm(melody)

        # 3. Harmonic Relationships (0-20 points)
        score += self._evaluate_harmony(melody)

        # 4. Phrase Structure (0-20 points)
        score += self._evaluate_phrasing(melody)

        # 5. Tension and Resolution (0-20 points)
        score += self._evaluate_tension_resolution(melody)

        return score

    def _evaluate_contour(self, melody):
        """Evaluate the melodic contour and shape."""
        score = 0

        # Analyze direction changes
        direction_changes = 0
        for i in range(1, len(melody) - 1):
            if (melody[i] - melody[i - 1]) * (melody[i + 1] - melody[i]) < 0:
                direction_changes += 1

        # Reward moderate number of direction changes (avoiding both static and erratic melodies)
        optimal_changes = len(melody) // 4
        score += 10 * (1 - abs(direction_changes - optimal_changes) / optimal_changes)

        # Analyze interval sizes
        for i in range(len(melody) - 1):
            interval = abs(melody[i] - melody[i + 1])
            # Reward stepwise motion with occasional leaps
            if interval <= 2:
                score += 0.5
            elif interval <= 4:
                score += 0.3
            elif interval <= 7:
                score += 0.2
            else:
                score -= 0.1

        return min(20, score)

    def _evaluate_rhythm(self, melody):
        """Evaluate rhythmic patterns and interest."""
        score = 0

        # Look for rhythmic patterns
        for pattern in self.RHYTHMIC_PATTERNS:
            pattern_length = len(pattern)
            for i in range(len(melody) - pattern_length):
                subsequence = melody[i : i + pattern_length]
                if self._matches_rhythm_pattern(subsequence, pattern):
                    score += 5

        # Reward syncopation (notes on weak beats)
        for i, note in enumerate(melody):
            if i % 2 == 1 and i < len(melody) - 1:
                if note != melody[i - 1] and note != melody[i + 1]:
                    score += 2

        return min(20, score)

    def _evaluate_harmony(self, melody):
        """Evaluate harmonic relationships and chord progressions."""
        score = 0

        # Check for notes that belong to common chords
        for i in range(len(melody)):
            for chord in self.COMMON_PROGRESSIONS:
                if melody[i] % 12 in [note % 12 for note in chord]:
                    score += 1

        # Analyze cadences (endings)
        if len(melody) >= 4:
            final_notes = melody[-4:]
            if self._is_good_cadence(final_notes):
                score += 10

        return min(20, score)

    def _evaluate_phrasing(self, melody):
        """Evaluate phrase structure and relationships."""
        score = 0

        # Look for balanced phrases (similar length sections)
        if len(melody) >= 8:
            first_half = melody[: len(melody) // 2]
            second_half = melody[len(melody) // 2 :]

            # Compare phrase lengths
            if abs(len(first_half) - len(second_half)) <= 1:
                score += 5

            # Look for motif repetition
            motif_length = 4
            for i in range(len(melody) - motif_length):
                motif = melody[i : i + motif_length]
                for j in range(i + motif_length, len(melody) - motif_length):
                    if self._similar_motifs(motif, melody[j : j + motif_length]):
                        score += 3

        return min(20, score)

    def _evaluate_tension_resolution(self, melody):
        """Evaluate musical tension and resolution."""
        score = 0

        # Reward tension in middle, resolution at end
        if len(melody) >= 4:
            # Middle section tension (non-chord tones, larger intervals)
            middle_start = len(melody) // 4
            middle_end = 3 * len(melody) // 4

            for i in range(middle_start, middle_end):
                if melody[i] not in [60, 64, 67]:  # Non-chord tones
                    score += 1

            # End resolution (return to chord tones)
            final_notes = melody[-4:]
            if final_notes[-1] in [60, 64, 67]:  # Ending on chord tone
                score += 10

        return min(20, score)

    def _matches_rhythm_pattern(self, subsequence, pattern):
        """Check if a subsequence matches a rhythmic pattern."""
        if len(subsequence) != len(pattern):
            return False

        # Compare relative note lengths
        for i in range(len(pattern) - 1):
            if abs(subsequence[i + 1] - subsequence[i]) != pattern[i]:
                return False
        return True

    def _is_good_cadence(self, notes):
        """Check if a sequence of notes forms a good cadence."""
        # Look for V-I movement in the bass
        if notes[-1] == 60 and notes[-2] in [67, 71]:  # G to C movement
            return True
        return False

    def _similar_motifs(self, motif1, motif2):
        """Check if two motifs are similar (allowing for transposition)."""
        if len(motif1) != len(motif2):
            return False

        # Compare interval patterns
        intervals1 = [motif1[i + 1] - motif1[i] for i in range(len(motif1) - 1)]
        intervals2 = [motif2[i + 1] - motif2[i] for i in range(len(motif2) - 1)]

        return intervals1 == intervals2

    def create_melody(
        self, length, population_size=100, generations=1000, mutation_rate=0.1
    ):
        """Generate a melody using the genetic algorithm with enhanced fitness."""
        # Initialize population
        population = self._initialize_population(length, population_size)

        # Track best fitness history
        # best_fitness_history = []
        generations_without_improvement = 0
        best_fitness = float("-inf")

        for gen in range(generations):
            # Evaluate and sort population
            population = sorted(population, key=self._evaluate_fitness, reverse=True)
            current_best_fitness = self._evaluate_fitness(population[0])

            # Track improvement
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1

            # Adaptive mutation rate
            if generations_without_improvement > 20:
                mutation_rate = min(0.5, mutation_rate * 1.1)  # Increase mutation rate
            else:
                mutation_rate = max(0.1, mutation_rate * 0.9)  # Decrease mutation rate

            # Create new population
            new_population = population[:2]  # Keep best 2

            while len(new_population) < population_size:
                if random.random() < 0.7:  # 70% crossover
                    parent1 = self._tournament_select(population)
                    parent2 = self._tournament_select(population)
                    child = self._crossover(parent1, parent2)
                else:  # 30% random new melody
                    child = self._create_random_melody(length)

                child = self._mutate(child, mutation_rate)
                new_population.append(child)

            population = new_population

            if gen % 10 == 0:
                print(f"Generation {gen}: Best fitness = {current_best_fitness}")

            # Early stopping if no improvement for many generations
            if generations_without_improvement > 100:
                print("Early stopping due to lack of improvement")
                break

        return max(population, key=self._evaluate_fitness)

    def _tournament_select(self, population, tournament_size=3):
        """Select individual using tournament selection."""
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=self._evaluate_fitness)

    def _create_random_melody(self, length):
        """Create a random melody with some musical constraints."""
        melody = []
        for i in range(length):
            if i == 0:
                # Start with tonic or dominant
                melody.append(random.choice([60, 67]))
            elif i == length - 1:
                # End with tonic or third
                melody.append(random.choice([60, 64]))
            else:
                melody.append(random.choice(self.scale))
        return melody

    def _initialize_population(self, length, population_size):
        """Initialize a random population of melodies."""
        return [
            [random.choice(self.scale) for _ in range(length)]
            for _ in range(population_size)
        ]

    def _crossover(self, parent1, parent2):
        """Perform crossover between two parent melodies."""
        crossover_point = random.randint(1, len(parent1) - 1)
        return parent1[:crossover_point] + parent2[crossover_point:]

    def _mutate(self, melody, mutation_rate):
        """Mutate a melody by randomly changing notes."""
        return [
            random.choice(self.scale) if random.random() < mutation_rate else note
            for note in melody
        ]

    def save_midi(self, melody, filename):
        """
        Save the melody as a MIDI file.

        Args:
            melody (list): List of MIDI note numbers.
            filename (str): Output filename.
        """
        midi = MIDIFile(1)
        track = 0
        time = 0
        midi.addTrackName(track, time, "Generated Melody")
        midi.addTempo(track, time, self.tempo)

        for i, pitch in enumerate(melody):
            midi.addNote(track, 0, pitch, time + i, 1, 100)

        with open(filename, "wb") as output_file:
            midi.writeFile(output_file)
