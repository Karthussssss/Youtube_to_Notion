import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# API Keys and Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Available AI Models
AVAILABLE_MODELS = {
    "gpt-4o": {
        "provider": "openai",
        "name": "GPT-4o",
        "max_tokens": 4096
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "name": "GPT-4o-mini",
        "max_tokens": 4096
    },
    "o1": {
        "provider": "openai",
        "name": "O1",
        "max_tokens": 4096
    },
    "o3-mini": {
        "provider": "openai",
        "name": "O3-mini",
        "max_tokens": 4096
    }
}

# Default model
DEFAULT_MODEL = "gpt-4o-mini"
OPENAI_MODEL = DEFAULT_MODEL  # Will be overridden at runtime

# Model Configurations
MAX_SUMMARY_LENGTH = 500  # Max tokens for summary
MIN_SUMMARY_LENGTH = 100  # Minimum tokens for summary

# App Settings
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")  # Default language for transcripts
PRESERVE_TEMP_FILES = os.getenv("PRESERVE_TEMP_FILES", "False").lower() == "true"

# Paths
TEMP_DIRECTORY = "temp"
os.makedirs(TEMP_DIRECTORY, exist_ok=True) 