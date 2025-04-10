from typing import Dict, Any, Optional

from notion_client import Client

from src.config import NOTION_API_KEY, NOTION_DATABASE_ID
from src.notion.markdown_converter import convert_markdown_to_notion_blocks


class NotionManager:
    """Class for managing Notion database operations."""
    
    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        self.api_key = api_key or NOTION_API_KEY
        self.database_id = database_id or NOTION_DATABASE_ID
        
        if not self.api_key:
            raise ValueError("Notion API key not found. Check your .env file.")
        if not self.database_id:
            raise ValueError("Notion database ID not found. Check your .env file.")
        
        self.client = Client(auth=self.api_key)
    
    def get_database_schema(self) -> Dict[str, Any]:
        """Get the schema of the Notion database."""
        try:
            database = self.client.databases.retrieve(self.database_id)
            return database['properties']
        except Exception as e:
            print(f"Error retrieving database schema: {e}")
            return {}
    
    def _create_page_properties(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create property dictionary for Notion page."""
        properties = {}
        
        # Get database schema to adapt to its structure
        schema = self.get_database_schema()
        
        # Map content to Notion properties based on schema
        for property_name, property_info in schema.items():
            property_type = property_info['type']
            
            if property_name == "Name" or property_name == "Title":
                # Handle title property
                if property_type == 'title':
                    properties[property_name] = {
                        'title': [{'text': {'content': content.get('title', '')}}]
                    }
            
            elif property_name == "URL" or property_name == "Video URL":
                # Handle URL property
                if property_type == 'url':
                    properties[property_name] = {'url': content.get('url', '')}
            
            elif property_name == "Summary" or property_name == "Content":
                # Handle text content property
                if property_type == 'rich_text':
                    # For properties, just include a brief summary
                    summary_preview = content.get('summary', '')[:100] + "..."
                    properties[property_name] = {
                        'rich_text': [{'text': {'content': summary_preview}}]
                    }
            
            elif (property_name == "Channel" or property_name == "Author") and property_type == 'rich_text':
                # Handle channel/author property from pytube
                author = content.get('author', content.get('channel', ''))
                if author:
                    properties[property_name] = {
                        'rich_text': [{'text': {'content': author}}]
                    }
            
            elif property_name == "Duration" or property_name == "Length":
                # Handle duration property from pytube
                if property_type == 'number':
                    duration = content.get('length', content.get('duration', 0))
                    properties[property_name] = {'number': duration}
                elif property_type == 'rich_text':
                    # Format duration as MM:SS
                    seconds = content.get('length', content.get('duration', 0))
                    if seconds:
                        minutes, secs = divmod(int(seconds), 60)
                        hours, minutes = divmod(minutes, 60)
                        if hours > 0:
                            duration_str = f"{hours}:{minutes:02d}:{secs:02d}"
                        else:
                            duration_str = f"{minutes:01d}:{secs:02d}"
                        properties[property_name] = {
                            'rich_text': [{'text': {'content': duration_str}}]
                        }
            
            elif property_name == "Views" and property_type == 'number':
                # Handle views property from pytube
                views = content.get('views', 0)
                properties[property_name] = {'number': views}
            
            elif property_name == "Published Date" or property_name == "Publish Date":
                # Handle publish date property from pytube
                publish_date = content.get('publish_date')
                if publish_date and property_type == 'date':
                    properties[property_name] = {'date': {'start': publish_date}}
                elif publish_date and property_type == 'rich_text':
                    properties[property_name] = {
                        'rich_text': [{'text': {'content': publish_date}}]
                    }
        
        return properties
    
    def add_to_database(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new page to the Notion database."""
        if 'summary' not in content or not content['summary']:
            raise ValueError("No summary available to add to Notion.")
        
        try:
            # Create properties for the new page
            properties = self._create_page_properties(content)
            
            # Convert the markdown summary to Notion blocks
            summary_blocks = convert_markdown_to_notion_blocks(content.get('summary', ''))
            
            # Add a header block for the summary section
            header_block = {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Video Summary"
                            }
                        }
                    ]
                }
            }
            
            # Combine all blocks
            blocks = [header_block] + summary_blocks
            
            # Create a new page in the database with the summary in the content
            new_page = self.client.pages.create(
                parent={'database_id': self.database_id},
                properties=properties,
                children=blocks
            )
            
            content['notion_page_id'] = new_page['id']
            content['notion_url'] = new_page['url']
            
            return content
            
        except Exception as e:
            print(f"Error adding to Notion database: {e}")
            return content 