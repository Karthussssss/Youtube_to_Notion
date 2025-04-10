# Notion Database API Reference (Python)

This reference document provides examples and syntax for common Notion Database API operations using the official Python SDK.

## Table of Contents
- [Installation](#installation)
- [Basic Setup](#basic-setup)
- [Property Types](#property-types)
- [Querying Databases](#querying-databases)
  - [Basic Query](#basic-query)
  - [Filtering Records](#filtering-records)
  - [Compound Filters](#compound-filters)
  - [Pagination](#pagination)
- [Creating Records](#creating-records)
- [Updating Records](#updating-records)
- [Advanced Usage](#advanced-usage)
  - [Working with Different Property Types](#working-with-different-property-types)
- [Tips and Best Practices](#tips-and-best-practices)

## Installation

```bash
pip install notion-client
```

## Basic Setup

```python
from notion_client import Client

# Initialize the client with your API token
notion = Client(auth="your_api_key_here")

# Database ID to work with
database_id = "your_database_id_here"
```

## Property Types

Below is a reference for how different property types in Notion are structured for API requests:

| Property Type | JSON Structure for Value |
|---------------|--------------------------|
| Title | `{"title": [{"text": {"content": "Value"}}]}` |
| Rich Text | `{"rich_text": [{"text": {"content": "Value"}}]}` |
| Number | `{"number": 42}` |
| Select | `{"select": {"name": "Option Name"}}` |
| Multi-select | `{"multi_select": [{"name": "Option 1"}, {"name": "Option 2"}]}` |
| Date | `{"date": {"start": "2023-01-01", "end": "2023-01-02"}}` |
| Checkbox | `{"checkbox": true}` |
| URL | `{"url": "https://example.com"}` |
| Email | `{"email": "example@example.com"}` |
| Phone Number | `{"phone_number": "+1 234 567 8901"}` |
| People | `{"people": [{"id": "user_id_1"}, {"id": "user_id_2"}]}` |
| Formula | (read-only) |
| Relation | `{"relation": [{"id": "page_id_1"}, {"id": "page_id_2"}]}` |
| Rollup | (read-only) |
| Status | `{"status": {"name": "Status Name"}}` |
| Files | `{"files": [{"name": "example.pdf", "external": {"url": "https://example.com/example.pdf"}}]}` |
| Created Time | (read-only) |
| Created By | (read-only) |
| Last Edited Time | (read-only) |
| Last Edited By | (read-only) |

## Querying Databases

### Basic Query

To retrieve all records from a database:

```python
response = notion.databases.query(database_id=database_id)
results = response["results"]  # List of page objects
```

### Filtering Records

To query a database with filters:

```python
# Filter for records where a checkbox property is checked
response = notion.databases.query(
    database_id=database_id,
    filter={
        "property": "Task completed",
        "checkbox": {
            "equals": True
        }
    }
)
```

```python
# Filter for text fields containing specific text
response = notion.databases.query(
    database_id=database_id,
    filter={
        "property": "Name",
        "rich_text": {
            "contains": "term"
        }
    }
)
```

```python
# Filter for select property with specific value
response = notion.databases.query(
    database_id=database_id,
    filter={
        "property": "Status",
        "select": {
            "equals": "In Progress"
        }
    }
)
```

```python
# Filter for dates after a certain date
response = notion.databases.query(
    database_id=database_id,
    filter={
        "property": "Due Date",
        "date": {
            "after": "2023-01-01"
        }
    }
)
```

```python
# Filter for non-empty values
response = notion.databases.query(
    database_id=database_id,
    filter={
        "property": "Assigned To",
        "rich_text": {
            "is_not_empty": True
        }
    }
)
```

### Compound Filters

Combine multiple filters using `and` and `or`:

```python
# AND filter (all conditions must be true)
response = notion.databases.query(
    database_id=database_id,
    filter={
        "and": [
            {
                "property": "Status",
                "select": {
                    "equals": "In Progress"
                }
            },
            {
                "property": "Priority",
                "select": {
                    "equals": "High"
                }
            }
        ]
    }
)
```

```python
# OR filter (any condition can be true)
response = notion.databases.query(
    database_id=database_id,
    filter={
        "or": [
            {
                "property": "Status",
                "select": {
                    "equals": "In Progress"
                }
            },
            {
                "property": "Status",
                "select": {
                    "equals": "Not Started"
                }
            }
        ]
    }
)
```

```python
# Nested conditions (AND with an OR within it)
response = notion.databases.query(
    database_id=database_id,
    filter={
        "and": [
            {
                "property": "Priority",
                "select": {
                    "equals": "High"
                }
            },
            {
                "or": [
                    {
                        "property": "Status",
                        "select": {
                            "equals": "In Progress"
                        }
                    },
                    {
                        "property": "Status",
                        "select": {
                            "equals": "Not Started"
                        }
                    }
                ]
            }
        ]
    }
)
```

### Pagination

Notion APIs return paginated results. Here's how to handle pagination:

```python
def get_all_database_records(database_id):
    results = []
    has_more = True
    next_cursor = None
    
    while has_more:
        response = notion.databases.query(
            database_id=database_id,
            start_cursor=next_cursor
        )
        
        results.extend(response["results"])
        
        has_more = response.get("has_more", False)
        next_cursor = response.get("next_cursor")
    
    return results
```

## Creating Records

To add a new record (page) to a database:

```python
# Basic example with multiple property types
new_page = notion.pages.create(
    parent={"database_id": database_id},
    properties={
        "Name": {
            "title": [
                {
                    "text": {
                        "content": "New record title"
                    }
                }
            ]
        },
        "Description": {
            "rich_text": [
                {
                    "text": {
                        "content": "Description text here"
                    }
                }
            ]
        },
        "Category": {
            "select": {
                "name": "Work"
            }
        },
        "Priority": {
            "select": {
                "name": "High"
            }
        },
        "Complete": {
            "checkbox": False
        },
        "Due Date": {
            "date": {
                "start": "2023-12-31"
            }
        },
        "Score": {
            "number": 85
        }
    }
)
```

## Updating Records

To update an existing record in the database:

```python
# Update specific properties of an existing page
notion.pages.update(
    page_id="page_id_here",
    properties={
        "Complete": {
            "checkbox": True
        },
        "Status": {
            "select": {
                "name": "Completed"
            }
        }
    }
)
```

## Advanced Usage

### Working with Different Property Types

Here's how to format various property types for Notion API:

**Title property:**

```python
def format_title(value):
    return {
        "title": [
            {
                "text": {
                    "content": str(value)
                }
            }
        ]
    }
```

**Rich text property:**

```python
def format_rich_text(value):
    return {
        "rich_text": [
            {
                "text": {
                    "content": str(value)
                }
            }
        ]
    }
```

**Number property:**

```python
def format_number(value):
    if value is None or pd.isna(value):
        return {"number": None}
    return {"number": float(value)}
```

**Select property:**

```python
def format_select(value):
    if not value:
        return {"select": None}
    return {"select": {"name": str(value)}}
```

**Date property:**

```python
def format_date(value):
    if not value:
        return {"date": None}
    
    # If value is a string, parse it
    if isinstance(value, str):
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        date_string = dt.isoformat()
    else:
        date_string = value.isoformat()
    
    return {
        "date": {
            "start": date_string,
            "end": None
        }
    }
```

## Tips and Best Practices

1. **Error Handling**: Always wrap Notion API calls in try-except blocks to handle potential errors.

```python
try:
    response = notion.databases.query(database_id=database_id)
    # Process response
except Exception as e:
    print(f"Error querying database: {str(e)}")
```

2. **Rate Limiting**: Notion API has rate limits. Add delays between requests if you're making many calls.

3. **Batch Processing**: When updating multiple records, consider batching your requests to reduce API calls.

4. **Null Values**: Handle null/empty values properly for each property type to avoid errors.

5. **Logging**: Log API requests and responses for debugging.

6. **Backup Data**: Always create backups before performing bulk updates or deletes.

7. **Use IDs, Not Names**: When possible, use property IDs instead of names for more reliable operations.

## Example: Complete Database Operation

Here's a complete example for updating records with a specific flag:

```python
def reset_latest_batch_flags(database_id):
    """Reset all 'Is Latest Batch' flags to False for existing records."""
    updated_count = 0
    
    try:
        # Query records where Is Latest Batch is "True"
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Is Latest Batch",
                "select": {
                    "equals": "True"
                }
            }
        )
        
        # Update each record
        for page in response["results"]:
            page_id = page["id"]
            try:
                notion.pages.update(
                    page_id=page_id,
                    properties={
                        "Is Latest Batch": {"select": {"name": "False"}}
                    }
                )
                updated_count += 1
            except Exception as e:
                print(f"Error updating record {page_id}: {str(e)}")
                continue
        
        print(f"Reset {updated_count} 'Is Latest Batch' flags")
        return updated_count
        
    except Exception as e:
        print(f"Error resetting 'Is Latest Batch' flags: {str(e)}")
        return 0
```

This reference document covers the most common Notion Database API operations with Python. Refer to the [official Notion API documentation](https://developers.notion.com/reference/intro) for more detailed information. 