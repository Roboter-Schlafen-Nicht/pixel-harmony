# Pixel Harmony
[![PixelHarmony CI](https://github.com/Roboter-Schlafen-Nicht/pixel-harmony/actions/workflows/ci.yml/badge.svg)](https://github.com/Roboter-Schlafen-Nicht/pixel-harmony/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

Transform your visual memories into musical experiences.

## About

Pixel Harmony is an innovative application that bridges the gap between visual and auditory art forms. By leveraging the power of artificial intelligence and genetic algorithms, Pixel Harmony converts your personal photos into unique, emotionally resonant melodies.

## Setup

### Prerequisites

### System Requirements

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3-pyaudio \
    portaudio19-dev \
    fluidsynth \
    fluid-soundfont-gm
```
### Python Requirements

- Python 3.8 or higher
- Conda package manager

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/Roboter-Schlafen-Nicht/pixel-harmony.git
   cd pixel-harmony
   ```

2. Create a Conda environment:
   ```
   conda create --name pixelharmony python=3.8
   conda activate pixelharmony
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up NLTK data:
   ```
   python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
   ```

5. Set up your Google Cloud Project and obtain the necessary credentials for Google Photos API. Place your `client_secret.json` file in the project root directory.

6. Create a `.env` file in the project root with the following content:
   ```
   PYTHONPATH=.:${PYTHONPATH}
   ANTHROPIC_API_KEY='your-api-key-here'
   ```

   Replace 'your-api-key-here' with your actual Anthropic API key.

7. If you're using VS Code, ensure your `settings.json` includes:
   ```json
   {
       "python.envFile": "${workspaceFolder}/.env"
   }
   ```

### Setting up PEP 8 Enforcement

To ensure code quality and consistency, we use Flake8, Black, and pre-commit hooks. Set them up as follows:

1. Install the pre-commit hooks:
   ```
   pre-commit install
   ```

Now, before each commit, your code will be automatically checked and formatted to comply with PEP 8 standards.

## Usage

To run PixelHarmony:

1. Run the application:

```bash
python main.py
```

2. Follow the interactive prompts to:
   - Select an audio output device
   - Generate a melody using genetic algorithms
   - Listen to the generated melody
   - Save or discard the MIDI file

## Development

### Code Quality

We use several tools to maintain code quality:

1. Install pre-commit hooks:
```bash
pre-commit install
```

### Testing

We use pytest for testing. To run the tests:

1. Ensure you're in the project root directory and your Conda environment is activated.

2. Run the tests:
   ```
   pytest
   ```

To add new tests, create files with the prefix `test_` in the `tests/` directory.

### Run Github actions locally

1. Ensure you're in the project root directory and your Conda environment is activated.

2. Ensure [act](https://www.freecodecamp.org/news/how-to-run-github-actions-locally/) has been installed

2. Run Default Github Actions:
   ```
   act
   ```

## Contributing

Contributions to PixelHarmony are welcome! Please refer to our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Anthropic for Claude API
- Google for Google Photos API
- The open-source community for the various libraries used in this project
