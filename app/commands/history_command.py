from .base import BaseCommand
from fastapi import WebSocket
from app.models.message import Message, CommandType

class HistoryCommand(BaseCommand):
    command_name = CommandType.HISTORY

    @property
    def help_text(self) -> str:
        return "/history <数量> - 显示历史消息"

    async def execute(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        try:
            count = int(message.data.get("count", "5"))
        except ValueError:
            count = 5

        context = self.context_manager.get_context(conversation_id)
        if not context:
            await self.send_error(websocket, "无法找到聊天上下文")
            return

        messages = context.get_last_n_messages(count)
        history_text = "\n".join([
            f"[{msg.timestamp.strftime('%H:%M:%S')}] {msg.sender}: {msg.content}"
            for msg in messages
        ])
        
        await self.send_response(
            websocket,
            f"最近 {len(messages)} 条消息:\n{history_text}" if messages else "没有历史消息"
        ) 