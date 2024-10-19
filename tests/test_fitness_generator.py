"""
This module contains unit tests for the FitnessGenerator class from the
pixelharmony package. The tests ensure that the FitnessGenerator class is
properly initialized and that its methods function as expected.

Fixtures:
    fitness_generator: A pytest fixture that initializes and returns an
    instance of the FitnessGenerator class.

Test Functions:
    test_fitness_generator_initialization: Tests the initialization of the
    FitnessGenerator instance.
    test_fitness_generator_init: Mocks dependencies to test the initialization
    of the FitnessGenerator class.
    test_generate_fitness: Mocks the client attribute to test the
    generate_fitness method of the FitnessGenerator instance.

Usage Example:
    pytest /home/human/github/pixel-harmony/tests/test_fitness_generator.py
"""

from unittest.mock import patch, MagicMock
import pytest
from pixelharmony.fitness_generator import FitnessGenerator


@pytest.fixture
def fitness_generator():
    """
    Fixture for creating a FitnessGenerator instance.

    This fixture initializes and returns a new instance of the FitnessGenerator
    class, which can be used in test functions to ensure consistent setup and
    teardown.

    Returns:
        FitnessGenerator: An instance of the FitnessGenerator class.
    """

    return FitnessGenerator()


def test_fitness_generator_initialization(fitness_generator):
    """
    Test the initialization of the fitness generator.

    This test ensures that the `fitness_generator` object is properly
    initialized and that its `client` attribute is not `None`.

    Args:
        fitness_generator: An instance of the FitnessGenerator class to be
        tested.

    Asserts:
        The `client` attribute of the `fitness_generator` is not `None`.
    """
    assert fitness_generator.client is not None


@patch("pixelharmony.fitness_generator.anthropic.Anthropic")
@patch("pixelharmony.fitness_generator.dotenv.load_dotenv")
def test_fitness_generator_init(mock_load_dotenv, mock_anthropic):
    """
    Test the initialization of the FitnessGenerator class.

    This test ensures that the FitnessGenerator class correctly initializes by:
    1. Calling the `load_dotenv` function once.
    2. Creating an instance of the `Anthropic` class.
    3. Setting the `client` attribute of the FitnessGenerator instance to the
    mocked `Anthropic` instance.

    Mocks:
        mock_load_dotenv: Mock for the `load_dotenv` function from the `dotenv`
        module.
        mock_anthropic: Mock for the `Anthropic` class from the `anthropic` module.
    """

    generator = FitnessGenerator()
    mock_load_dotenv.assert_called_once()
    mock_anthropic.assert_called_once()
    assert generator.client == mock_anthropic.return_value


def test_generate_fitness(fitness_generator):
    """
    Test the `generate_fitness` method of the `fitness_generator` object.

    This test mocks the `client` attribute of the `fitness_generator` to
    simulate the behavior of the `messages.create` method. It verifies that the
    `generate_fitness` method correctly generates a fitness function code and
    that the `messages.create` method is called exactly once. Additionally, it
    checks that the generated fitness function code contains the expected
    function signature.

    Args:
        fitness_generator: An instance of the fitness generator to be tested.
    """
    fitness_generator.client = MagicMock()
    fitness_generator.client.messages.create.return_value.content = (
        "def fitness(melody: List[int]) -> float:\n    return 0.0"
    )
    fitness_function_code = fitness_generator.generate_fitness()
    fitness_generator.client.messages.create.assert_called_once()
    assert "def fitness(melody: List[int]) -> float" in fitness_function_code
