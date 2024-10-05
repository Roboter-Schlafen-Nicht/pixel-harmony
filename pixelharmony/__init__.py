import os
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Optionally, you can add a check to ensure critical environment variables are set
if "ANTHROPIC_API_KEY" not in os.environ:
    raise EnvironmentError("ANTHROPIC_API_KEY is not set in the environment variables.")

# You can add any other initialization code for your package here
