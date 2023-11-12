import os

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ.get('TOKEN_GH')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
