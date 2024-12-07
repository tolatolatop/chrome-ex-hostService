from .base import BaseCommand
from fastapi import WebSocket
from app.models.message import Message, CommandType

class RenameCommand(BaseCommand):
    command_name = CommandType.RENAME

    @property
    def help_text(self) -> str:
        return "/rename <新名字> - 修改用户名"

    async def execute(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        context = self.context_manager.get_context(conversation_id)
        if not context or not context.user_context:
            await self.send_error(websocket, "无法找到用户上下文")
            return

        new_name = message.data.get("new_name", "")
        if not new_name:
            await self.send_error(websocket, "请指定新的用户名")
            return

        self.context_manager.update_username(context.user_context.user_id, new_name)
        await self.send_response(websocket, f"用户名已更改为: {new_name}") 