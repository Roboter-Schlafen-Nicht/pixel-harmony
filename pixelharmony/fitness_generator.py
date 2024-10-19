"""This module contains the FitnessGenerator class, which is used to generate fitness
functions for evaluating melodies based on characteristics of West African music.

Classes:
    FitnessGenerator: A class to generate fitness functions for melodies, focusing on
    rhythmic patterns, pentatonic scales.

Usage Example:
    generator = FitnessGenerator()
    fitness_function_code = generator.generate_fitness()
"""

import dotenv
import anthropic


class FitnessGenerator:
    """
    A class used to generate fitness functions for melodies based on West African musical
    characteristics.

    Methods
    -------
    __init__():
        Initializes the FitnessGenerator by loading environment variables and setting up
        the Anthropics client.

    generate_fitness():
        Generates a Python function named 'fitness' that evaluates a melody represented
        as a list of MIDI note numbers. The generated function focuses on characteristics
        of West African music, such as rhythmic patterns, pentatonic scales, cyclical
        structures, call and response, and speech-like melodic contours.
    """

    def __init__(self):
        dotenv.load_dotenv()
        self.client = anthropic.Anthropic()

    def generate_fitness(self):
        """
        Generates a fitness function for evaluating melodies based on characteristics of
        West African music.

        The generated function, named 'fitness', evaluates a melody represented as a list
        of MIDI note numbers. The evaluation focuses on rhythmic patterns, syncopation,
        use of pentatonic scales, cyclical structures, call and response elements, and
        speech-like melodic contours.

        Returns:
            str: The Python code for the 'fitness' function as a string.
        """
        prompt = """Create a Python function named 'fitness' that evaluates a melody
            represented as a list of MIDI note numbers, focusing on characteristics of
            West African music.

            Function Signature: def fitness(melody: List[int]) -> float

            Description of desired musical qualities:
            Create a fitness function for a melody that embodies key elements of West
            African music. The melody should emphasize rhythmic patterns and syncopation.
            It should favor the use of pentatonic scales, which are common in many West
            African musical traditions. The melody should have a cyclical structure, with
            repetitive patterns that evolve slightly over time. Include elements of call
            and response, where a phrase is stated and then answered. The melody should
            also have a strong relationship to speech patterns, with variations in pitch
            that might mimic tonal languages.

            Requirements:
            1. The function should return a float value, where higher values indicate
               better fitness.
            2. Use musical terms and concepts relevant to West African music.
            3. Consider aspects like rhythmic patterns, use of pentatonic scales, cyclical
               structures, call and response, and speech-like melodic contours.
            4. You can use helper functions if needed, but define them within the main
               function.
            5. Avoid using external libraries.

            Example melody: [60, 62, 64, 67, 69, 72, 74, 76]

            Please provide only the Python code, without any explanations."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=10240,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content
