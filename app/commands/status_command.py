from .base import BaseCommand
from fastapi import WebSocket
from app.models.message import Message, CommandType
from datetime import datetime

class StatusCommand(BaseCommand):
    command_name = CommandType.STATUS

    @property
    def help_text(self) -> str:
        return "/status - 显示系统状态"

    async def execute(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        context = self.context_manager.get_context(conversation_id)
        if not context or not context.user_context:
            await self.send_error(websocket, "无法找到聊天上下文")
            return

        current_time = datetime.now()
        status_data = {
            "conversation_id": context.conversation_id,
            "started_at": context.started_at.isoformat(),
            "duration": str(current_time - context.started_at),
            "message_count": context.user_context.message_count,
            "username": context.user_context.username,
            "last_active": context.user_context.last_active.isoformat()
        }
        
        await self.send_response(websocket, "系统状态", status_data) 