import os

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ.get("TOKEN_GH")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Get project directory based on current file as global variable
PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
