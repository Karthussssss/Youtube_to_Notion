import sys
import os
import argparse
from dotenv import load_dotenv

from src.pipeline import YouTubeToNotionPipeline
from src.config import AVAILABLE_MODELS, DEFAULT_LANGUAGE


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


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="YouTube to Notion Pipeline")
    parser.add_argument("--url", type=str, help="YouTube URL to process")
    parser.add_argument("--model", type=str, choices=list(AVAILABLE_MODELS.keys()), 
                        help="AI model to use for summarization")
    parser.add_argument("--input-file", type=str, 
                        help="Path to a file containing YouTube URLs (one per line)")
    parser.add_argument("--batch", action="store_true", 
                        help="Process multiple YouTube URLs in batch mode")
    parser.add_argument("--language", type=str, 
                        help="Language code for transcript (e.g., en, es, fr, auto)")
    return parser.parse_args()


def read_urls_from_file(file_path):
    """Read YouTube URLs from a file."""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
        return urls
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def process_url(url, model, language=None, pipeline=None):
    """Process a single YouTube URL."""
    if not pipeline:
        pipeline = YouTubeToNotionPipeline(model=model, language=language)
        
    try:
        print(f"\nProcessing: {url}")
        result = pipeline.process(url)
        
        print("\n✅ Success! Video processed and added to Notion.")
        print(f"Title: {result.get('title', 'Unknown')}")
        print(f"Notion URL: {result.get('notion_url', 'Unknown')}")
        return True, result
        
    except Exception as e:
        error_message = str(e)
        print(f"\n❌ Error: {error_message}")
        
        # Provide more helpful messages for common errors
        if "No transcript available" in error_message or "TranscriptsDisabled" in error_message:
            print("\nThis video doesn't have captions or transcripts available.")
            print("The application only works with videos that have captions enabled.")
        elif "Could not extract video ID" in error_message:
            print("\nInvalid YouTube URL format.")
        
        return False, {"error": error_message, "url": url}


def main():
    """Main entry point for the application."""
    # Set up environment
    setup_environment()
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Get model (from args or user input)
    model = args.model if args.model else select_model()
    
    # Get language (from args or use default)
    language = args.language if args.language else DEFAULT_LANGUAGE
    
    # Initialize pipeline once for batch processing
    pipeline = YouTubeToNotionPipeline(model=model, language=language)
    
    # Determine the mode and get URLs
    if args.input_file:
        # Batch processing from file
        urls = read_urls_from_file(args.input_file)
        if not urls:
            print("Error: No valid URLs found in the input file.")
            sys.exit(1)
            
        print(f"\nBatch processing {len(urls)} YouTube URLs...")
        
        # Process all URLs
        results = {
            "success": [],
            "failures": []
        }
        
        for i, url in enumerate(urls):
            print(f"\n[{i+1}/{len(urls)}] Processing URL: {url}")
            success, result = process_url(url, model, language, pipeline)
            if success:
                results["success"].append(result)
            else:
                results["failures"].append(result)
        
        # Show summary of results
        print("\n=== Batch Processing Summary ===")
        print(f"Total URLs processed: {len(urls)}")
        print(f"Successful: {len(results['success'])}")
        print(f"Failed: {len(results['failures'])}")
        
        if results["failures"]:
            print("\nFailed URLs:")
            for failure in results["failures"]:
                print(f"- {failure['url']}: {failure['error']}")
        
    elif args.url:
        # Single URL from command line
        process_url(args.url, model, language, pipeline)
    else:
        # Interactive mode
        url = get_youtube_url()
        
        if not url.strip():
            print("\nError: No URL provided.")
            sys.exit(1)
        
        process_url(url, model, language, pipeline)


if __name__ == "__main__":
    main() 