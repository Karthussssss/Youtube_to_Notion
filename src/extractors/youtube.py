import os
import re
import json
from typing import Optional, Dict, Any

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import yt_dlp

from src.config import (
    DEFAULT_LANGUAGE
)


class YouTubeExtractor:
    """Class for extracting content from YouTube videos."""
    
    def __init__(self):
        self.video_id = None
        self.video_info = None
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        """Extract the YouTube video ID from a URL."""
        # Regular expression to match YouTube video ID
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # Standard YouTube URLs
            r"(?:embed\/)([0-9A-Za-z_-]{11})",  # Embedded URLs
            r"(?:shorts\/)([0-9A-Za-z_-]{11})"  # Shorts URLs
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video metadata using yt-dlp."""
        self.video_id = self.extract_video_id(url)
        
        try:
            # Configure yt-dlp to extract metadata only
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'format': 'best',
                'extract_flat': True,
            }
            
            # Use yt-dlp to fetch video metadata
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Map relevant metadata to our content structure
                return {
                    'id': self.video_id,
                    'title': info.get('title', ''),
                    'author': info.get('uploader', ''),
                    'channel': info.get('channel', ''),
                    'length': info.get('duration', 0),
                    'publish_date': info.get('upload_date', ''),
                    'views': info.get('view_count', 0),
                    'description': info.get('description', ''),
                    'url': url
                }
        except Exception as e:
            print(f"Warning: Could not fetch video metadata: {e}")
            # Fallback to basic info if yt-dlp fails
            return {
                'id': self.video_id,
                'title': f"YouTube Summary - {self.video_id}",
                'url': url
            }
    
    def fetch_transcript(self) -> Optional[str]:
        """Fetch transcript using youtube-transcript-api."""
        if not self.video_id:
            raise ValueError("No video ID available. Call get_video_info first.")
        
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(
                self.video_id, 
                languages=[DEFAULT_LANGUAGE]
            )
            
            # Concatenate all text segments
            full_text = " ".join([segment["text"] for segment in transcript_list])
            return full_text
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"Error: Transcript not available: {e}")
            raise ValueError(f"No transcript available for this video. Only videos with available captions are supported.")
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            raise ValueError(f"Failed to fetch transcript: {e}")
    
    def get_content(self, url: str) -> Dict[str, Any]:
        """Main method to extract content from a YouTube video."""
        video_info = self.get_video_info(url)
        
        # Get transcript from YouTube API
        transcript = self.fetch_transcript()
        
        # Since we now only use transcript API, we'll raise an error if no transcript
        if not transcript:
            raise ValueError("No transcript available for this video. Only videos with available captions are supported.")
        
        video_info['transcript'] = transcript
        return video_info 