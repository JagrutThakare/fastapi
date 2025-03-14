from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class PromptNode(BaseModel):
    inputs: Dict[str, Any]  # Allow any input structure
    class_type: str
    _meta: Dict[str, str]

class ComfyUIPrompt(BaseModel):
    prompt: Dict[str, PromptNode]
    client_id: str
    server_address: str

class HistoryResponse(BaseModel):
    all_prompts: Dict[str, Dict]

class ProgressResponse(BaseModel):
    status: str
    message: str

class ImageResponse(BaseModel):
    filename: str
    image_data: bytes



from pydantic import BaseModel
from typing import Optional, List, Dict

class RequestData(BaseModel):
    trend: Optional[str] = None
    brand_name: Optional[str] = None
    post_type: Optional[str] = None
    event_desc: Optional[str] = None
    product_desc: Optional[str] = None
    achievement: Optional[str] = None
    job_desc: Optional[str] = None
    font: Optional[str] = None
    colors: Optional[str] = None
    festival_name: Optional[str] = None
    message: Optional[str] = None
    theme: Optional[str] = None
    platform: Optional[str] = None
    logo_position: Optional[str] = None
    aspect_ratio: Optional[str] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    overlay_text: Optional[Dict[str, str]] = None

class Article(BaseModel):
    title: str
    link: str
    published: str
    source: str

class NewsResponse(BaseModel):
    feed_title: str
    articles: List[Article]

class CaptionRequest(BaseModel):
    positive_prompt: str
    negative_prompt: str


