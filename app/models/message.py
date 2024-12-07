from pydantic import BaseModel
from enum import Enum
import json
from datetime import datetime

class MessageType(str, Enum):
    CHAT = "chat"
    SYSTEM = "system"
    ERROR = "error"

class Message(BaseModel):
    type: MessageType
    content: str
    sender: str
    timestamp: datetime = datetime.now()

    def to_json(self):
        return json.dumps({
            "type": self.type,
            "content": self.content,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat()
        })
