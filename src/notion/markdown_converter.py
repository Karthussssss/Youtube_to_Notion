import re
from typing import List, Dict, Any


def convert_markdown_to_notion_blocks(markdown_text: str) -> List[Dict[str, Any]]:
    """
    Convert markdown text to Notion API block format.
    This is a simplified conversion that handles common markdown elements.
    """
    blocks = []
    lines = markdown_text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Headers
        header_match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            content = header_match.group(2)
            
            # Process any inline formatting in the header
            rich_text = process_inline_formatting(content)
            
            header_type = f"heading_{level}"
            blocks.append({
                "object": "block",
                "type": header_type,
                header_type: {
                    "rich_text": rich_text
                }
            })
            i += 1
            continue
        
        # Bulleted list
        if line.startswith('- ') or line.startswith('* '):
            content = line[2:]
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": process_inline_formatting(content)
                }
            })
            i += 1
            continue
        
        # Numbered list
        numbered_match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if numbered_match:
            content = numbered_match.group(2)
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": process_inline_formatting(content)
                }
            })
            i += 1
            continue
        
        # Blockquote
        if line.startswith('>'):
            content = line[1:].strip()
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": process_inline_formatting(content)
                }
            })
            i += 1
            continue
        
        # Code block
        if line.startswith('```'):
            code_language = line[3:].strip()
            code_content = []
            i += 1
            
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_content.append(lines[i])
                i += 1
            
            if i < len(lines):  # Skip the closing ```
                i += 1
                
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": '\n'.join(code_content)}}],
                    "language": code_language if code_language else "plain text"
                }
            })
            continue
        
        # Divider
        if line == '---' or line == '___' or line == '***':
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
            i += 1
            continue
        
        # Regular paragraph (default)
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": process_inline_formatting(line)
            }
        })
        i += 1
    
    return blocks


def process_inline_formatting(text: str) -> List[Dict[str, Any]]:
    """
    Process inline formatting like bold, italic, etc. and convert to Notion rich text format.
    """
    # Split text by bold markers
    result = []
    
    # Process bold text (both ** and __ formats)
    pattern = r'(\*\*|__)(.*?)(\1)'
    
    # Track our position in the original text
    last_end = 0
    
    for match in re.finditer(pattern, text):
        # Add any text before this match
        if match.start() > last_end:
            result.append({
                "type": "text", 
                "text": {"content": text[last_end:match.start()]}
            })
        
        # Add the bold text
        result.append({
            "type": "text",
            "text": {"content": match.group(2)},
            "annotations": {"bold": True}
        })
        
        last_end = match.end()
    
    # Add any remaining text after the last match
    if last_end < len(text):
        result.append({
            "type": "text", 
            "text": {"content": text[last_end:]}
        })
    
    # If no formatting was found, return the original text
    if not result:
        result.append({"type": "text", "text": {"content": text}})
    
    return result 