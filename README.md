# YouTube to Notion Pipeline

A modular Python application that takes a YouTube link, extracts content via transcripts, generates a well-structured markdown-formatted summary using GPT-4o-mini, and adds it to a Notion database.

## Features

- Extracts YouTube video transcripts using available captions
- Fetches accurate video metadata (title, author, duration, etc.) directly from YouTube
- Uses OpenAI GPT-4o-mini for smart, well-formatted content summarization
- Generates consistent, structured summaries using a template with Overview, Key Insights, Detailed Information, and Summary sections
- Properly formats markdown including bold text and headings that display beautifully in Notion
- Integrates with Notion to store video summaries and metadata in a database
- Modular design with object-oriented programming principles

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

## Setting Up OpenAI

1. Create an OpenAI account or sign in at [OpenAI](https://platform.openai.com/)
2. Generate an API key in your account
3. Copy the API key to your `.env` file as `OPENAI_API_KEY`

## Usage

Run the application and it will prompt you to enter a YouTube URL:

```
python main.py
```

The application will:
1. Extract the video transcript
2. Fetch metadata like title, author, etc.
3. Generate a well-structured summary using OpenAI
4. Add the summary and metadata to your Notion database
5. Provide a link to the created Notion page

Note: Only videos with available captions are supported. The application will not work for videos without captions or transcripts.

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
- openai: For OpenAI API integration (GPT-4o-mini)
- notion-client: For Notion API integration
- python-dotenv: For environment variable management

## Limitations

- This application only works with YouTube videos that have captions available. It does not support videos without transcripts.
- YouTube may occasionally block metadata requests. The app falls back to extracting key information from the summary in such cases.

## Future Enhancements

- Batch processing of multiple YouTube videos
- Support for additional video platforms
- Web interface for easier interaction
- Caching to avoid redundant processing

## License

MIT 