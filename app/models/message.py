from pydantic import BaseModel
from enum import Enum
import json
from datetime import datetime
from typing import Optional, Dict, Any

class MessageRole(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class MessageType(str, Enum):
    CHAT = "chat"           # 普通聊天消息
    COMMAND = "command"     # 命令消息
    RESPONSE = "response"   # 命令响应
    ERROR = "error"         # 错误消息
    SYSTEM = "system"       # 系统消息

class CommandType(str, Enum):
    HELP = "help"          # 显示帮助信息
    CLEAR = "clear"        # 清除聊天记录
    RENAME = "rename"      # 重命名用户
    STATUS = "status"      # 显示系统状态
    HISTORY = "history"    # 显示历史消息
    UNKNOWN = "unknown"    # 未知命令

class Message(BaseModel):
    type: MessageType
    role: MessageRole
    content: str
    sender: str
    timestamp: datetime = datetime.now()
    command: Optional[CommandType] = None
    data: Optional[Dict[str, Any]] = None

    def to_json(self):
        return json.dumps({
            "type": self.type,
            "role": self.role,
            "content": self.content,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
            "command": self.command,
            "data": self.data
        })

    @classmethod
    def create_command(cls, command: str, sender: str, **kwargs) -> 'Message':
        """创建命令消息"""
        try:
            cmd_type = CommandType(command.lower())
        except ValueError:
            cmd_type = CommandType.UNKNOWN

        return cls(
            type=MessageType.COMMAND,
            role=MessageRole.USER,
            content=command,
            sender=sender,
            command=cmd_type,
            data=kwargs
        )

    @classmethod
    def create_response(cls, content: str, data: Optional[Dict[str, Any]] = None) -> 'Message':
        """创建响应消息"""
        return cls(
            type=MessageType.RESPONSE,
            role=MessageRole.AGENT,
            content=content,
            sender="Agent",
            data=data
        )

    @classmethod
    def create_error(cls, content: str) -> 'Message':
        """创建错误消息"""
        return cls(
            type=MessageType.ERROR,
            role=MessageRole.SYSTEM,
            content=content,
            sender="System"
        )
