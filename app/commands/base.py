from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from fastapi import WebSocket
from app.models.message import Message
from app.websocket.context import ContextManager

class BaseCommand(ABC):
    """命令处理器的基类"""
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    @property
    @abstractmethod
    def command_name(self) -> str:
        """命令名称"""
        pass

    @property
    def help_text(self) -> str:
        """命令帮助文本"""
        return "没有帮助信息"

    @abstractmethod
    async def execute(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        """执行命令"""
        pass

    async def send_response(self, websocket: WebSocket, content: str, data: Optional[Dict[str, Any]] = None) -> None:
        """发送响应消息"""
        response = Message.create_response(content, data)
        await websocket.send_text(response.to_json())

    async def send_error(self, websocket: WebSocket, error_message: str) -> None:
        """发送错误误消息"""
        error = Message.create_error(error_message)
        await websocket.send_text(error.to_json()) 