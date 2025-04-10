import textwrap
from typing import List, Dict, Any

from src.config import (
    OPENAI_MODEL,
    OPENAI_API_KEY,
    MAX_SUMMARY_LENGTH,
    MIN_SUMMARY_LENGTH
)


class Summarizer:
    """Class for summarizing text content using OpenAI's API."""
    
    def __init__(self, use_openai=True):
        # Always use OpenAI, parameter kept for compatibility
        self.use_openai = True
    
    def _chunk_text(self, text: str, max_chunk_size: int = 4000) -> List[str]:
        """Split text into chunks of a maximum size."""
        return textwrap.wrap(
            text, 
            width=max_chunk_size, 
            break_long_words=False, 
            break_on_hyphens=False
        )
    
    def summarize_with_openai(self, text: str) -> str:
        """Summarize text using OpenAI's API with GPT-4o-mini."""
        try:
            import openai
            
            if not OPENAI_API_KEY:
                raise ValueError("OpenAI API key not found. Check your .env file.")
            
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Create a system prompt for the summarization with markdown instructions
            system_prompt = (
                "You are an expert summarization assistant. Your task is to summarize YouTube video transcripts "
                "in a consistent, well-structured Markdown format suitable for Notion. Your response must strictly adhere "
                "to the following format:\n\n"
                "## Overview\n"
                "Provide a high-level overview of the video's content in 1-2 concise paragraphs.\n\n"
                "## Innovative Ideas / Key Insights\n"
                "### [Insight Title]\n"
                "- Supporting detail or bullet point\n"
                "*(Repeat heading with bullet points as needed)*\n\n"
                "## Detailed Information\n"
                "Include additional context, supporting details, and in-depth notes.\n\n"
                "## Summary\n"
                "Conclude with a brief final recap.\n\n"
                "Make sure your entire response uses this exact structure with clear Markdown headings "
                "and bullet points. Do not add extra text or commentary outside this structure."
            )
            
            # Create a user prompt for the summarization
            user_prompt = (
                "Please summarize the following YouTube video transcript. Use the exact Markdown structure provided, "
                "ensuring that each section is clearly labeled:\n\n"
                "## Overview\n"
                "## Innovative Ideas / Key Insights\n"
                "### [Insight Title]\n"
                "- Bullet points as necessary\n"
                "## Detailed Information\n"
                "## Summary\n\n"
                f"{text}"
            )
            
            # Call the OpenAI API with the chat completions endpoint
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=MAX_SUMMARY_LENGTH,
                temperature=0.3,  # Lower temperature for more focused output
            )
            
            return response.choices[0].message.content.strip()
            
        except ImportError:
            raise ImportError("OpenAI package is required. Please install it with: pip install openai")
        except Exception as e:
            print(f"Error using OpenAI API: {e}")
            raise
    
    def summarize(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to summarize content."""
        if 'transcript' not in content or not content['transcript']:
            raise ValueError("No transcript available for summarization.")
        
        text = content['transcript']
        
        # Always use OpenAI for summarization
        summary = self.summarize_with_openai(text)
        
        # Add the summary to the content dictionary
        content['summary'] = summary
        return content 