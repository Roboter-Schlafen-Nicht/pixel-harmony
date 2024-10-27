"""This module contains the FitnessGenerator class with proper response handling."""

import logging
from typing import List
from abc import ABC, abstractmethod
import anthropic
import dotenv

# Configure logger
fitness_logger = logging.getLogger("pixel_harmony.api")
fitness_logger.setLevel(logging.DEBUG)


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
        if not melody:
            return score

        # Basic scoring criteria
        for i, note in enumerate(melody):
            # Reward notes in comfortable vocal range
            if 60 <= note <= 72:
                score += 1.0

            # Reward stepwise motion
            if i > 0:
                interval = abs(note - melody[i - 1])
                if interval <= 2:
                    score += 0.5
                elif interval <= 4:
                    score += 0.3

        # Reward good start and end notes
        if melody[0] in [60, 67]:  # Start with tonic or dominant
            score += 2.0
        if melody[-1] == 60:  # End with tonic
            score += 2.0

        return score


class GeneratedFitnessFunction(BaseFitnessFunction):
    """Dynamic fitness function generated based on musical characteristics."""

    def __init__(self, prompt_response: str):
        """
        Initialize with the response from the prompt.

        Args:
            prompt_response: The response containing fitness logic description
        """
        self.description = prompt_response
        self.criteria = self._parse_prompt_response()

    def _parse_prompt_response(self) -> dict:
        """
        Parse the prompt response to set up fitness evaluation parameters.

        Returns:
            dict: Dictionary containing parsed evaluation criteria
        """
        criteria = {
            "preferred_range": (60, 72),  # Default comfortable vocal range
            "stepwise_motion_weight": 0.5,
            "cadence_weight": 2.0,
            "phrase_length": 4,
            "prefer_consonant_intervals": True,
        }

        # Parse the description to customize criteria
        desc_lower = self.description.lower()

        # Adjust range based on description
        if "high range" in desc_lower:
            criteria["preferred_range"] = (67, 79)
        elif "low range" in desc_lower:
            criteria["preferred_range"] = (48, 60)

        # Adjust weights based on description
        if "strong emphasis on stepwise motion" in desc_lower:
            criteria["stepwise_motion_weight"] = 0.8
        if "strong cadences" in desc_lower:
            criteria["cadence_weight"] = 3.0

        # Adjust phrase analysis
        if "longer phrases" in desc_lower:
            criteria["phrase_length"] = 8
        elif "short motifs" in desc_lower:
            criteria["phrase_length"] = 2

        return criteria

    def fitness(self, melody: List[int]) -> float:
        """
        Evaluate melody fitness based on the generated criteria.

        Args:
            melody: List of MIDI note numbers

        Returns:
            float: Fitness score
        """
        if not melody:
            return 0.0

        score = 0.0

        # Range evaluation
        min_range, max_range = self.criteria["preferred_range"]
        score += sum(1.0 for note in melody if min_range <= note <= max_range)

        # Melodic motion
        for i in range(len(melody) - 1):
            interval = abs(melody[i] - melody[i + 1])
            if interval <= 2:
                score += self.criteria["stepwise_motion_weight"]
            elif interval <= 4:
                score += self.criteria["stepwise_motion_weight"] * 0.5

        # Phrase analysis
        phrase_length = self.criteria["phrase_length"]
        for i in range(0, len(melody) - phrase_length + 1, phrase_length):
            phrase = melody[i : i + phrase_length]
            if self._is_good_phrase(phrase):
                score += 1.0

        # Cadence evaluation
        if len(melody) >= 2:
            final_interval = abs(melody[-2] - melody[-1])
            if final_interval in [1, 2, 5]:  # Common cadential intervals
                score += self.criteria["cadence_weight"]

        return score

    def _is_good_phrase(self, phrase: List[int]) -> bool:
        """
        Evaluate if a phrase has good musical characteristics.

        Args:
            phrase: List of MIDI notes representing a musical phrase

        Returns:
            bool: True if the phrase has good characteristics
        """
        if not phrase:
            return False

        # Check for melodic arch
        has_arch = max(phrase) != phrase[0] and max(phrase) != phrase[-1]

        # Check for rhythmic pattern (using note intervals as proxy)
        intervals = [abs(phrase[i] - phrase[i - 1]) for i in range(1, len(phrase))]
        has_pattern = len(set(intervals)) < len(intervals)  # Some repetition

        return has_arch or has_pattern


class FitnessGenerator:
    """Class to generate fitness functions based on musical criteria."""

    def __init__(self):
        """Initialize the FitnessGenerator."""
        try:
            dotenv.load_dotenv()
            self.client = anthropic.Anthropic()
            fitness_logger.info("FitnessGenerator initialized successfully")
        except (anthropic.APIConnectionError, anthropic.APIError) as e:
            fitness_logger.error("Error initializing FitnessGenerator: %s", e)
            raise

    def generate_fitness(self) -> BaseFitnessFunction:
        """
        Generate a fitness function based on musical criteria.

        Returns:
            BaseFitnessFunction: A fitness function object
        """
        try:
            # Get response from Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                messages=[{"role": "user", "content": self._get_fitness_prompt()}],
            )

            # Create and return fitness function
            return GeneratedFitnessFunction(response.content)

        except (
            anthropic.APIConnectionError,
            anthropic.APIError,
            ValueError,
            TypeError,
        ) as e:
            fitness_logger.error("Unexpected error: %s", e)
            return DefaultFitnessFunction()

    def _get_fitness_prompt(self) -> str:
        """Get the prompt for generating fitness criteria."""
        return """Describe how to evaluate a melody represented as a list of MIDI
        note numbers, focusing on these aspects:

        1. Preferred note range and melodic motion
        2. Phrase structure and length
        3. Cadence preferences
        4. Overall melodic shape

        Format your response as a clear description of how each aspect should be
        evaluated, including any specific musical patterns or characteristics to
        prefer or avoid.

        Example aspects to consider:
        - Comfortable vocal ranges
        - Stepwise vs. leap motion
        - Structural points for cadences
        - Melodic arch and contour
        """
