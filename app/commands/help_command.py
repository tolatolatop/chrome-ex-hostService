from .base import BaseCommand
from fastapi import WebSocket
from app.models.message import Message, CommandType

class HelpCommand(BaseCommand):
    command_name = CommandType.HELP

    @property
    def help_text(self) -> str:
        return "/help - 显示此帮助信息"

    async def execute(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        help_text = """可用命令：
        /help - 显示此帮助信息
        /clear - 清除聊天记录
        /rename <新名字> - 修改用户名
        /status - 显示系统状态
        /history <数量> - 显示历史消息
        """
        await self.send_response(websocket, help_text) 