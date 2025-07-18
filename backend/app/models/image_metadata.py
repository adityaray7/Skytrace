from pydantic import BaseModel
from typing import Optional

class ImageMetadata(BaseModel):
    id: str
    timestamp: float
    cloud_cover: float
    thumbnail_url: str
    source: str
