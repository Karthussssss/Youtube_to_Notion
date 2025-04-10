import sys
import os
from dotenv import load_dotenv

from src.pipeline import YouTubeToNotionPipeline
from src.config import AVAILABLE_MODELS


def setup_environment():
    """Set up the environment for the application."""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ["NOTION_API_KEY", "NOTION_DATABASE_ID", "OPENAI_API_KEY"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with these variables and try again.")
        sys.exit(1)
    
    # Create temp directory if it doesn't exist
    os.makedirs("temp", exist_ok=True)


def get_youtube_url():
    """Prompt the user for a YouTube URL."""
    print("\nYouTube to Notion Pipeline")
    print("==========================")
    return input("\nEnter a YouTube URL: ")


def select_model():
    """Prompt the user to select an AI model for summarization."""
    print("\nSelect AI Model for Summarization:")
    print("----------------------------------")
    
    models = {
        "1": {"name": "GPT-4o", "id": "gpt-4o", "description": "OpenAI's most capable model (balanced quality/speed)"},
        "2": {"name": "GPT-4o-mini", "id": "gpt-4o-mini", "description": "Faster, more affordable GPT model (default)"},
        "3": {"name": "O1", "id": "o1", "description": "OpenAI's advanced vision-language model (highest quality)"},
        "4": {"name": "O3-mini", "id": "o3-mini", "description": "Fast, efficient version of O1 (good balance)"}
    }
    
    # Display options
    for key, model in models.items():
        print(f"{key}. {model['name']} - {model['description']}")
    
    # Default to GPT-4o-mini
    print("\nPress Enter to use the default (GPT-4o-mini)")
    
    # Get user choice
    choice = input("\nSelect model (1-4): ").strip()
    
    # Use default if no input
    if not choice:
        choice = "2"  # Default to GPT-4o-mini
    
    # Validate choice and return model
    if choice in models:
        selected_model = models[choice]
        print(f"\nSelected: {selected_model['name']}")
        return selected_model["id"]
    else:
        print("\nInvalid selection. Using default model (GPT-4o-mini).")
        return "gpt-4o-mini"


def main():
    """Main entry point for the application."""
    # Set up environment
    setup_environment()
    
    # Select AI model
    model = select_model()
    
    # Prompt user for YouTube URL
    url = get_youtube_url()
    
    if not url.strip():
        print("\nError: No URL provided.")
        sys.exit(1)
    
    # Create and run the pipeline
    pipeline = YouTubeToNotionPipeline(model=model)
    
    try:
        print(f"\nProcessing: {url}")
        # Process the URL
        result = pipeline.process(url)
        
        # Print success message
        print("\nSuccess! Video processed and added to Notion.")
        print(f"Title: {result.get('title', 'Unknown')}")
        print(f"Notion URL: {result.get('notion_url', 'Unknown')}")
        
    except Exception as e:
        error_message = str(e)
        print(f"\nError: {error_message}")
        
        # Provide more helpful messages for common errors
        if "No transcript available" in error_message or "TranscriptsDisabled" in error_message:
            print("\nThis video doesn't have captions or transcripts available.")
            print("The application only works with videos that have captions enabled.")
            print("Try another video that has captions or subtitles available.")
        elif "Could not find database with ID" in error_message:
            print("\nCouldn't find your Notion database. Please check:")
            print("1. Your NOTION_DATABASE_ID in the .env file is correct")
            print("2. You've shared the database with your integration")
            print("3. The database ID format includes dashes in the correct positions")
        elif "authentication" in error_message.lower() or "unauthorized" in error_message.lower():
            print("\nAPI authentication failed. Please check your API keys in the .env file.")
        
        sys.exit(1)


if __name__ == "__main__":
    main() 