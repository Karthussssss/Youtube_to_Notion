import textwrap
import os
import time
from typing import List, Dict, Any, Optional

from src.config import (
    OPENAI_API_KEY,
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    MAX_SUMMARY_LENGTH,
    MIN_SUMMARY_LENGTH
)


class Summarizer:
    """Class for summarizing text content using OpenAI models."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the summarizer with the specified model.
        
        Args:
            model: The OpenAI model to use for summarization. If None, uses default model.
        """
        self.model_id = model if model and model in AVAILABLE_MODELS else DEFAULT_MODEL
        self.model_info = AVAILABLE_MODELS.get(self.model_id, AVAILABLE_MODELS[DEFAULT_MODEL])
    
    def _chunk_text(self, text: str, max_chunk_size: int = 4000) -> List[str]:
        """Split text into chunks of a maximum size."""
        return textwrap.wrap(
            text, 
            width=max_chunk_size, 
            break_long_words=False, 
            break_on_hyphens=False
        )
        
    def _get_prompt_template(self) -> Dict[str, str]:
        """Get the prompt template for summarization."""
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
        
        user_prompt = (
            "Please summarize the following YouTube video transcript. Use the exact Markdown structure provided, "
            "ensuring that each section is clearly labeled:\n\n"
            "## Overview\n"
            "## Innovative Ideas / Key Insights\n"
            "### [Insight Title]\n"
            "- Bullet points as necessary\n"
            "## Detailed Information\n"
            "## Summary\n\n"
            "{text}"
        )
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    def summarize_with_openai(self, text: str, max_retries: int = 3, retry_delay: float = 2.0) -> str:
        """Summarize text using OpenAI's API with retry mechanism.
        
        Args:
            text: The text to summarize
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds, doubles after each retry
            
        Returns:
            Summarized text
            
        Raises:
            ValueError: If OpenAI API key is not found
            Exception: If all retry attempts fail
        """
        try:
            import openai
            from openai import RateLimitError, APIError, APIConnectionError, Timeout
            
            if not OPENAI_API_KEY:
                raise ValueError("OpenAI API key not found. Check your .env file.")
            
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            prompts = self._get_prompt_template()
            
            # Set up message structure outside retry loop
            messages = [
                {"role": "system", "content": prompts["system"]},
                {"role": "user", "content": prompts["user"].format(text=text)}
            ]
            
            # Retry logic for handling rate limits and transient errors
            attempt = 0
            current_delay = retry_delay
            last_error = None
            
            while attempt < max_retries:
                try:
                    # Call the OpenAI API with the chat completions endpoint
                    response = client.chat.completions.create(
                        model=self.model_id,
                        messages=messages,
                        max_tokens=MAX_SUMMARY_LENGTH,
                        temperature=0.3,  # Lower temperature for more focused output
                    )
                    
                    return response.choices[0].message.content.strip()
                    
                except (RateLimitError, APIError, APIConnectionError, Timeout) as e:
                    attempt += 1
                    last_error = e
                    
                    if attempt < max_retries:
                        print(f"OpenAI API error: {e}. Retrying in {current_delay:.1f} seconds... (Attempt {attempt}/{max_retries})")
                        time.sleep(current_delay)
                        current_delay *= 2  # Exponential backoff
                    else:
                        print(f"Maximum retry attempts reached. Last error: {e}")
                        raise
                
                except Exception as e:
                    # Don't retry for other exceptions
                    print(f"Unexpected error using OpenAI API: {e}")
                    raise
            
            # If we've exhausted retries
            raise last_error
            
        except ImportError:
            raise ImportError("OpenAI package is required. Please install it with: pip install openai")
    
    def summarize(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to summarize content."""
        if 'transcript' not in content or not content['transcript']:
            raise ValueError("No transcript available for summarization.")
        
        text = content['transcript']
        
        # Handle very long transcripts by summarizing in chunks if needed
        if len(text) > 25000:  # If transcript is extremely long (>25K chars)
            print(f"Transcript is very long ({len(text)} chars). Processing in chunks...")
            chunks = self._chunk_text(text, max_chunk_size=25000)
            
            # Summarize each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                print(f"Summarizing chunk {i+1}/{len(chunks)}...")
                chunk_summary = self.summarize_with_openai(chunk)
                chunk_summaries.append(chunk_summary)
            
            # Combine chunk summaries and create a final summary
            if len(chunk_summaries) > 1:
                combined_summary = "\n\n".join(chunk_summaries)
                # Create a meta-summary for very long content
                summary = self.summarize_with_openai(
                    f"This is a collection of summaries from different parts of a long transcript. "
                    f"Please create a cohesive summary that combines all these sections:\n\n{combined_summary}"
                )
            else:
                summary = chunk_summaries[0]
        else:
            # For normal length transcripts, summarize directly
            summary = self.summarize_with_openai(text)
        
        # Add the summary to the content dictionary
        content['summary'] = summary
        return content 