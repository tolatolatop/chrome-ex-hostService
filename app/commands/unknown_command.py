from .base import BaseCommand
from fastapi import WebSocket
from app.models.message import Message, CommandType

class UnknownCommand(BaseCommand):
    command_name = CommandType.UNKNOWN

    async def execute(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        await self.send_error(websocket, f"未知命令: {message.content}") 