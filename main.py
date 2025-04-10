import sys
import os
from dotenv import load_dotenv

from src.pipeline import YouTubeToNotionPipeline


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


def main():
    """Main entry point for the application."""
    # Set up environment
    setup_environment()
    
    # Prompt user for YouTube URL
    url = get_youtube_url()
    
    if not url.strip():
        print("\nError: No URL provided.")
        sys.exit(1)
    
    # Create and run the pipeline
    pipeline = YouTubeToNotionPipeline()
    
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