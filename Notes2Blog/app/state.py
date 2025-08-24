from typing import TypedDict, Optional, List, Dict, Any

class State(TypedDict, total=False):
    image_path: str
    image_b64: str
    raw_text: str
    theme: str
    outline: List[str]
    blog_markdown: str
    react_code: str
    feedback: str
    validated: bool
    logs: List[str]
    errors: Optional[str]
    retry_count: int
    # Metadata fields
    title: str
    summary: str
    tags: List[str]
    slug: str
    reading_time: int
