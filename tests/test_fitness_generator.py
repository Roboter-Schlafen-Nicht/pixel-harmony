from pixelharmony.fitness_generator import GeneratedFitnessFunction


def test_generated_fitness_function_high_range():
    prompt_response = "The melody should be in a high range."
    fitness_function = GeneratedFitnessFunction(prompt_response)
    melody = [68, 70, 72, 74, 76, 78]
    score = fitness_function.fitness(melody)
    assert score > 0


def test_generated_fitness_function_low_range():
    prompt_response = "The melody should be in a low range."
    fitness_function = GeneratedFitnessFunction(prompt_response)
    melody = [50, 52, 54, 56, 58, 60]
    score = fitness_function.fitness(melody)
    assert score > 0


def test_generated_fitness_function_stepwise_motion():
    prompt_response = "Strong emphasis on stepwise motion."
    fitness_function = GeneratedFitnessFunction(prompt_response)
    melody = [60, 61, 62, 63, 64, 65]
    score = fitness_function.fitness(melody)
    assert score > 0


def test_generated_fitness_function_strong_cadences():
    prompt_response = "Strong cadences are preferred."
    fitness_function = GeneratedFitnessFunction(prompt_response)
    melody = [60, 62, 64, 65, 67, 60]
    score = fitness_function.fitness(melody)
    assert score > 0


def test_generated_fitness_function_longer_phrases():
    prompt_response = "The melody should have longer phrases."
    fitness_function = GeneratedFitnessFunction(prompt_response)
    melody = [60, 62, 64, 65, 67, 69, 71, 72]
    score = fitness_function.fitness(melody)
    assert score > 0


def test_generated_fitness_function_short_motifs():
    prompt_response = "The melody should have short motifs."
    fitness_function = GeneratedFitnessFunction(prompt_response)
    melody = [60, 62, 64, 65]
    score = fitness_function.fitness(melody)
    assert score > 0
