from pydantic import BaseModel
from typing import Optional, List, Dict


class JobRequest(BaseModel):
    user_id: str
    topic: str
    type: str
    posts: List[Dict]

class ContentRequest(BaseModel):
    topic: str
    method: Optional[str] = "one time"
    days: Optional[int] = None