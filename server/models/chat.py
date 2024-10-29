from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        d["timestamp"] = self.timestamp.isoformat()
        return d

class ChatHistory(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        } 