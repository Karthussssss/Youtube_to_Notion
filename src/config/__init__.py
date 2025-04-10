import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# API Keys and Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Model Configurations
OPENAI_MODEL = "gpt-4o-mini"  # OpenAI model for summarization
MAX_SUMMARY_LENGTH = 500  # Max tokens for summary
MIN_SUMMARY_LENGTH = 100  # Minimum tokens for summary

# App Settings
DEFAULT_LANGUAGE = "en"  # Default language for transcripts
PRESERVE_TEMP_FILES = os.getenv("PRESERVE_TEMP_FILES", "False").lower() == "true"

# Paths
TEMP_DIRECTORY = "temp"
os.makedirs(TEMP_DIRECTORY, exist_ok=True) 