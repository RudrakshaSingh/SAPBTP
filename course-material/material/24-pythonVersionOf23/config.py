"""Configuration: API key, model name, and the shared Gemini client."""

import os

from dotenv import load_dotenv
from google import genai

# Read key/model settings from the .env file next to this script.
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY (or GOOGLE_API_KEY) is not configured. "
        "Set it in the .env file before starting the app."
    )

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# One client is created at startup and reused by every request.
client = genai.Client(api_key=API_KEY)
