from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    username: str
    password: str
    created_at: datetime
