import logging
import re
import string
import time
from typing import Dict, Any, Optional, Callable

from src.extractors.youtube import YouTubeExtractor
from src.summarizers.summarizer import Summarizer
from src.notion.manager import NotionManager
from src.config import DEFAULT_MODEL, AVAILABLE_MODELS, DEFAULT_LANGUAGE


class YouTubeToNotionPipeline:
    """Main pipeline class that orchestrates the entire process."""
    
    def __init__(self, model: Optional[str] = None, language: Optional[str] = None, progress_callback: Optional[Callable[[str, float], None]] = None):
        """Initialize the pipeline with all necessary components.
        
        Args:
            model: The AI model to use for summarization. If None, uses default model.
            language: The language code for transcript extraction. If None, uses default language.
            progress_callback: Optional callback function to report progress (message, percentage)
        """
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Progress tracking
        self.progress_callback = progress_callback
        
        # Use provided model or default
        self.model = model if model and model in AVAILABLE_MODELS else DEFAULT_MODEL
        self.logger.info(f"Using model: {self.model}")
        
        # Set language for transcript
        self.language = language or DEFAULT_LANGUAGE
        
        # Initialize components
        self.youtube_extractor = YouTubeExtractor()
        self.summarizer = Summarizer(model=self.model)
        self.notion_manager = NotionManager()
    
    def _report_progress(self, message: str, percentage: float) -> None:
        """Report progress through callback if available and log it."""
        self.logger.info(f"Progress ({percentage:.0f}%): {message}")
        if self.progress_callback:
            self.progress_callback(message, percentage)
    
    def _validate_url(self, url: str) -> None:
        """Validate that the URL is a proper YouTube URL."""
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")
        
        if not any(domain in url for domain in ['youtube.com', 'youtu.be']):
            raise ValueError("URL must be a valid YouTube URL")
    
    def _capitalize_title(self, title: str) -> str:
        """Properly capitalize a title using title case."""
        if not title:
            return title
            
        # Words that should not be capitalized in titles (unless first or last word)
        lowercase_words = {
            'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 
            'to', 'from', 'by', 'in', 'of', 'with', 'as'
        }
        
        # Split the title into words
        words = title.split()
        if not words:
            return title
            
        # Capitalize first and last words
        if words:
            words[0] = words[0].capitalize()
        if len(words) > 1:
            words[-1] = words[-1].capitalize()
            
        # Handle the rest of the words
        for i in range(1, len(words) - 1):
            word = words[i]
            # Check if the word is in our lowercase list
            if word.lower() in lowercase_words and not word[0] in string.punctuation:
                words[i] = word.lower()
            else:
                words[i] = word.capitalize()
                
        # Join words back together
        capitalized_title = ' '.join(words)
        
        # Handle ellipsis
        if title.endswith('...'):
            capitalized_title = capitalized_title.rstrip('.')
            capitalized_title += '...'
            
        return capitalized_title
    
    def _extract_title_from_summary(self, summary: str) -> Optional[str]:
        """Extract the video title from the summary text if possible."""
        # Look for patterns like 'Summary of "X"' or 'X Video Summary' or similar patterns
        patterns = [
            r'Summary of ["\'](.+?)["\']',         # Summary of "Title"
            r'# (.+?) Summary',                     # # Title Summary
            r'# Summary of ["\'](.+?)["\']',        # # Summary of "Title"
            r'^(.+?) Video Summary',                # Title Video Summary
            r'["\'](.+?)["\'] Video',               # "Title" Video
            r'overview of ["\'](.+?)["\']',         # overview of "Title"
            r'overview of the ["\'](.+?)["\']',     # overview of the "Title"
            r'from ["\'](.+?)["\']',                # from "Title"
            r'titled ["\'](.+?)["\']',              # titled "Title"
            r'called ["\'](.+?)["\']',              # called "Title"
        ]
        
        # First look in the overview section if it exists
        overview_match = re.search(r'## Overview\s+(.+?)(?=##|\Z)', summary, re.DOTALL)
        if overview_match:
            overview_text = overview_match.group(1).strip()
            
            # Look for video title patterns in the overview
            for pattern in patterns:
                match = re.search(pattern, overview_text, re.IGNORECASE)
                if match:
                    return self._capitalize_title(match.group(1).strip())
            
            # If no pattern match, use the first sentence which often contains the title
            # But clean it up to make a better title
            sentences = re.split(r'(?<=[.!?])\s+', overview_text)
            if sentences:
                first_sentence = sentences[0].strip()
                # Extract quoted text if present
                quoted_match = re.search(r'["\'](.+?)["\']', first_sentence)
                if quoted_match:
                    return self._capitalize_title(quoted_match.group(1).strip())
                
                # Clean up common phrases that make titles too verbose
                cleaned_sentence = first_sentence
                phrases_to_remove = [
                    r'^This video (discusses|explores|presents|is about|covers|focuses on|examines|talks about|provides|offers)',
                    r'^In this video,?\s+',
                    r'^The video (discusses|explores|presents|is about|covers|focuses on|examines|talks about|provides|offers)',
                    r'^The speaker (discusses|explores|presents|talks about|covers|focuses on|examines|provides|offers)',
                ]
                
                for phrase in phrases_to_remove:
                    cleaned_sentence = re.sub(phrase, '', cleaned_sentence, flags=re.IGNORECASE).strip()
                
                # If sentence starts with a verb now, it might not make a good title
                words = cleaned_sentence.split()
                if len(words) > 3:
                    # Use first 5-7 words for a concise title
                    title = ' '.join(words[:min(7, len(words))]) + ('' if len(words) <= 7 else '...')
                    return self._capitalize_title(title)
                else:
                    # If sentence is already short or we removed too much, use it as is
                    return self._capitalize_title(cleaned_sentence)
        
        # If no overview section or no title found in overview, 
        # search the entire summary with our patterns
        for pattern in patterns:
            match = re.search(pattern, summary, re.IGNORECASE)
            if match:
                return self._capitalize_title(match.group(1).strip())
        
        # If we still can't find a title, extract from first h2 heading
        heading_match = re.search(r'## (.*?)(?=\n|$)', summary)
        if heading_match and heading_match.group(1).lower() != 'overview':
            return self._capitalize_title(heading_match.group(1).strip())
        
        return None
    
    def process(self, url: str) -> Dict[str, Any]:
        """Process a YouTube URL through the entire pipeline."""
        start_time = time.time()
        try:
            # Validate URL
            self._validate_url(url)
            self._report_progress(f"Processing YouTube URL: {url}", 5)
            
            # Step 1: Extract content from YouTube
            self._report_progress("Fetching video metadata and transcript...", 10)
            content = self.youtube_extractor.get_content(url, self.language)
            
            if not content.get('transcript'):
                raise ValueError("Failed to extract transcript from the video")
            
            transcript_length = len(content.get('transcript', ''))
            self._report_progress(
                f"Extracted transcript ({transcript_length} characters). "
                f"Video duration: {content.get('duration_str', 'unknown')}",
                30
            )
            
            # Step 2: Summarize the content
            self._report_progress(f"Generating summary with {self.model}... (this may take a while for longer videos)", 40)
            content = self.summarizer.summarize(content)
            
            if not content.get('summary'):
                raise ValueError("Failed to generate summary")
            
            summary_length = len(content.get('summary', ''))
            self._report_progress(
                f"Summary generated ({summary_length} characters)",
                70
            )
            
            # If the title from YouTube metadata isn't a generic one, use it directly
            # Otherwise, try to extract a better title from the summary
            youtube_title = content.get('title', '')
            if youtube_title and not youtube_title.startswith("YouTube Summary - "):
                # Use the actual video title from YouTube (via pytube)
                self.logger.info(f"Using YouTube title: {youtube_title}")
                # Ensure the title is properly capitalized if needed
                if not any(char.isupper() for char in youtube_title[1:]):
                    content['title'] = self._capitalize_title(youtube_title)
            elif extracted_title := self._extract_title_from_summary(content['summary']):
                # Fallback to extracting from summary
                self.logger.info(f"Found title in summary: {extracted_title}")
                content['title'] = extracted_title
            
            # Step 3: Add to Notion database
            self._report_progress("Adding to Notion database...", 80)
            result = self.notion_manager.add_to_database(content)
            
            elapsed_time = time.time() - start_time
            self._report_progress(
                f"Successfully processed video: {content.get('title')} in {elapsed_time:.1f} seconds", 
                100
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in pipeline: {str(e)}")
            raise 