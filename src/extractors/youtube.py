import os
import re
import json
from typing import Optional, Dict, Any, List

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
                
                # Format the duration as a string (HH:MM:SS)
                duration_secs = info.get('duration', 0)
                minutes, seconds = divmod(duration_secs, 60)
                hours, minutes = divmod(minutes, 60)
                
                if hours > 0:
                    duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    duration_str = f"{minutes:02d}:{seconds:02d}"
                
                # Map relevant metadata to our content structure
                return {
                    'id': self.video_id,
                    'title': info.get('title', ''),
                    'author': info.get('uploader', ''),
                    'channel': info.get('channel', ''),
                    'length': info.get('duration', 0),
                    'duration_str': duration_str,
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
    
    def get_available_transcript_languages(self) -> List[Dict[str, str]]:
        """Get list of available transcript languages for a video."""
        if not self.video_id:
            raise ValueError("No video ID available. Call get_video_info first.")
        
        try:
            # Get transcript list
            transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)
            
            # Get available languages
            languages = []
            
            # Add manually created transcripts
            for transcript in transcript_list._manually_created_transcripts.values():
                languages.append({
                    'language_code': transcript.language_code,
                    'language': transcript.language,
                    'type': 'manual',
                    'is_translatable': transcript.is_translatable
                })
                
            # Add auto-generated transcripts
            for transcript in transcript_list._generated_transcripts.values():
                languages.append({
                    'language_code': transcript.language_code,
                    'language': transcript.language,
                    'type': 'auto',
                    'is_translatable': transcript.is_translatable
                })
                
            return languages
            
        except (TranscriptsDisabled, NoTranscriptFound):
            return []
        except Exception as e:
            print(f"Error getting transcript languages: {e}")
            return []
    
    def fetch_transcript(self, language_code: str = None) -> Optional[str]:
        """Fetch transcript using youtube-transcript-api.
        
        Args:
            language_code: The language code for the transcript. If None, uses default language.
                           Can be a list of language codes in order of preference.
        """
        if not self.video_id:
            raise ValueError("No video ID available. Call get_video_info first.")
        
        # Use provided language or default
        languages = [language_code] if language_code else [DEFAULT_LANGUAGE]
        
        try:
            # Try to get transcript with specified language
            transcript_list = YouTubeTranscriptApi.get_transcript(
                self.video_id, 
                languages=languages
            )
            
            # Concatenate all text segments
            full_text = " ".join([segment["text"] for segment in transcript_list])
            return full_text
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"Error: Transcript not available in specified language: {e}")
            
            # Try to get available languages
            available_languages = self.get_available_transcript_languages()
            if available_languages:
                print(f"Available languages: {', '.join([lang['language'] for lang in available_languages])}")
                
                # Try to get transcript in any available language
                try:
                    # Get manually created transcripts first
                    manual_languages = [lang['language_code'] for lang in available_languages if lang['type'] == 'manual']
                    if manual_languages:
                        transcript_list = YouTubeTranscriptApi.get_transcript(
                            self.video_id,
                            languages=manual_languages
                        )
                        print(f"Found transcript in language: {manual_languages[0]}")
                        full_text = " ".join([segment["text"] for segment in transcript_list])
                        return full_text
                    
                    # Try auto-generated if no manual transcript
                    auto_languages = [lang['language_code'] for lang in available_languages if lang['type'] == 'auto']
                    if auto_languages:
                        transcript_list = YouTubeTranscriptApi.get_transcript(
                            self.video_id,
                            languages=auto_languages
                        )
                        print(f"Found transcript in language: {auto_languages[0]}")
                        full_text = " ".join([segment["text"] for segment in transcript_list])
                        return full_text
                
                except Exception:
                    # If all else fails, try the default fetcher
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(self.video_id)
                        full_text = " ".join([segment["text"] for segment in transcript_list])
                        return full_text
                    except Exception:
                        pass
            
            # If we got here, no transcript is available
            raise ValueError(f"No transcript available for this video. Only videos with available captions are supported.")
            
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            raise ValueError(f"Failed to fetch transcript: {e}")
    
    def get_content(self, url: str, language_code: str = None) -> Dict[str, Any]:
        """Main method to extract content from a YouTube video.
        
        Args:
            url: The YouTube URL
            language_code: Optional language code for transcript
        """
        video_info = self.get_video_info(url)
        
        # Get transcript from YouTube API
        transcript = self.fetch_transcript(language_code)
        
        # Since we now only use transcript API, we'll raise an error if no transcript
        if not transcript:
            raise ValueError("No transcript available for this video. Only videos with available captions are supported.")
        
        video_info['transcript'] = transcript
        return video_info 