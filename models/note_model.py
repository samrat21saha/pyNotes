from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Note(BaseModel):
    title: str
    desc: str
    important: bool = False

    user_id: Optional[str] = None

    created_at: datetime
    updated_at: datetime