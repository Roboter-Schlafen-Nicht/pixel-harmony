# PixelHarmony

Transform your visual memories into musical experiences.

## About

PixelHarmony is an innovative application that bridges the gap between visual and auditory art forms. By leveraging the power of artificial intelligence and genetic algorithms, PixelHarmony converts your personal photos into unique, emotionally resonant melodies.

## Key Features

- **Google Photos Integration**: Seamlessly access and select images from your Google Photos library.
- **AI-Powered Image Analysis**: Utilizes advanced image recognition to interpret the content, mood, and composition of your photos.
- **Intelligent Music Generation**: Employs genetic algorithms to create melodies that reflect the essence of your images.
- **Customizable Output**: Fine-tune the generated music to match your preferences.
- **Interactive GUI**: User-friendly interface for an engaging experience from image selection to music playback.

## How It Works

1. **Select**: Choose a meaningful photo from your Google Photos collection.
2. **Analyze**: Our AI examines the image, identifying key elements and emotional tones.
3. **Compose**: A genetic algorithm crafts a melody based on the image analysis.
4. **Refine**: Adjust musical parameters to personalize your audio experience.
5. **Enjoy**: Listen to your photo transformed into a unique musical piece.

## Setup

### Prerequisites

- Python 3.8 or higher
- Conda package manager

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pixel-harmony.git
   cd PixelHarmony
   ```

2. Create a Conda environment:
   ```
   conda create --name pixelharmony python=3.8
   conda activate pixelharmony
   ```

3. Install the required packages:
   ```
   conda install -c conda-forge pygame
   conda install -c conda-forge nltk
   conda install -c conda-forge pytest
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client midiutil anthropic
   ```

4. Set up NLTK data:
   ```
   python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
   ```

5. Set up your Google Cloud Project and obtain the necessary credentials for Google Photos API. Place your `client_secret.json` file in the project root directory.

6. Set your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

### Setting up PEP 8 Enforcement

To ensure code quality and consistency, we use Flake8, Black, and pre-commit hooks. Set them up as follows:

1. Install the required tools:
   ```
   pip install flake8 black pre-commit
   ```

2. Set up pre-commit hooks:
   ```
   pre-commit install
   ```

Now, before each commit, your code will be automatically checked and formatted to comply with PEP 8 standards.

## Usage

To run PixelHarmony:

```
python main.py
```

Follow the on-screen prompts to select an image and generate music.

## Testing

We use pytest for testing. To run the tests:

1. Ensure you're in the project root directory and your Conda environment is activated.

2. Run the tests:
   ```
   pytest
   ```

To add new tests, create files with the prefix `test_` in the `tests/` directory.

## Contributing

Contributions to PixelHarmony are welcome! Please refer to our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Anthropic for Claude API
- Google for Google Photos API
- The open-source community for the various libraries used in this project
