# YouTube to Notion Pipeline

A modular Python application that takes a YouTube link, extracts content via transcripts, generates a well-structured markdown-formatted summary using OpenAI models, and adds it to a Notion database.

## Features

- Extracts YouTube video transcripts using available captions
- Fetches accurate video metadata (title, author, duration, etc.) directly from YouTube
- Supports multiple OpenAI models for summarization:
  - GPT-4o and GPT-4o-mini
  - O1 and O3-mini
- Generates consistent, structured summaries using a template with Overview, Key Insights, Detailed Information, and Summary sections
- Properly formats markdown including bold text and headings that display beautifully in Notion
- Integrates with Notion to store video summaries and metadata in a database
- Modular design with object-oriented programming principles
- **NEW: Batch processing** - Process multiple YouTube videos at once
- **NEW: Command-line arguments** for flexible usage

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/youtube-to-notion.git
   cd youtube-to-notion
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file by copying the example:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file with your API keys and configuration.

## Setting Up Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations) and create a new integration
2. Copy the "Internal Integration Token" to your `.env` file as `NOTION_API_KEY`
3. Create a database in Notion with the following properties:
   - Name/Title (title type)
   - Video URL (url type)
   - Author/Channel (rich text type - optional)
   - Duration/Length (number or rich text type - optional)
   - Views (number type - optional)
   - Published Date (date or rich text type - optional)
4. Share your database with the integration by clicking "Share" and adding your integration
5. Copy the database ID from the URL (the part after the workspace name and before the question mark) to your `.env` file as `NOTION_DATABASE_ID`

## Setting Up OpenAI API

1. Create an OpenAI account or sign in at [OpenAI](https://platform.openai.com/)
2. Generate an API key in your account
3. Copy the API key to your `.env` file as `OPENAI_API_KEY`

## Usage

### Interactive Mode

Run the application without arguments to use the interactive mode:

```
python main.py
```

The application will:
1. Prompt you to select an OpenAI model for summarization
2. Ask you to enter a YouTube URL
3. Extract the video transcript
4. Fetch metadata like title, author, etc.
5. Generate a well-structured summary using the selected OpenAI model
6. Add the summary and metadata to your Notion database
7. Provide a link to the created Notion page

### Command Line Arguments

You can also use command line arguments for more flexible usage:

```
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --model "gpt-4o-mini"
```

Available arguments:
- `--url`: YouTube URL to process
- `--model`: AI model to use (gpt-4o, gpt-4o-mini, o1, o3-mini)
- `--input-file`: Path to a file containing YouTube URLs (one per line)
- `--batch`: Process multiple YouTube URLs in batch mode

### Batch Processing

Process multiple videos at once by providing a file with one URL per line:

```
python main.py --input-file urls.txt --model "gpt-4o-mini"
```

Note: Only videos with available captions are supported. The application will try to use the available transcripts for the video.

## Available AI Models

- **GPT-4o**: OpenAI's most capable model, offering a good balance of quality and speed
- **GPT-4o-mini**: Faster, more affordable OpenAI model (default)
- **O1**: OpenAI's advanced vision-language model for highest quality summaries
- **O3-mini**: Fast, efficient version of O1 with a good balance of quality and speed

## Project Structure

```
youtube-to-notion/
├── main.py                  # Entry point and command-line interface
├── requirements.txt         # Project dependencies
├── .env.example             # Example environment variables
├── README.md                # This file
├── temp/                    # Temporary files directory
├── docs/                    # Documentation
│   └── review.md            # Project review and analysis
├── src/                     # Source code
│   ├── __init__.py
│   ├── pipeline.py          # Main orchestration class
│   ├── config/              # Configuration
│   │   └── __init__.py      # Configuration settings
│   ├── extractors/          # Content extraction modules
│   │   ├── __init__.py
│   │   └── youtube.py       # YouTube metadata and transcript extraction
│   ├── summarizers/         # Text summarization modules
│   │   ├── __init__.py
│   │   └── summarizer.py    # OpenAI text summarization with structured format
│   ├── notion/              # Notion integration
│   │   ├── __init__.py
│   │   ├── manager.py       # Notion database operations
│   │   └── markdown_converter.py  # Markdown to Notion blocks converter
│   └── utils/               # Utility functions
│       └── __init__.py
```

## Dependencies

- youtube-transcript-api: For extracting YouTube transcripts
- yt-dlp: For fetching accurate video metadata
- openai: For OpenAI API integration
- notion-client: For Notion API integration
- python-dotenv: For environment variable management

## Limitations

- This application only works with YouTube videos that have captions available. It does not support videos without transcripts.
- YouTube may occasionally block metadata requests. The app falls back to extracting key information from the summary in such cases.

## Future Enhancements

- Support for additional video platforms
- Web interface for easier interaction
- Caching to avoid redundant processing
- Support for additional AI model providers

## License

MIT 