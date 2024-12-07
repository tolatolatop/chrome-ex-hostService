from .base import BaseCommand
from fastapi import WebSocket
from app.models.message import Message, CommandType

class ClearCommand(BaseCommand):
    command_name = CommandType.CLEAR

    @property
    def help_text(self) -> str:
        return "/clear - 清除聊天记录"

    async def execute(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        context = self.context_manager.get_context(conversation_id)
        if context:
            context.clear_history()
            await self.send_response(websocket, "聊天记录已清除") 