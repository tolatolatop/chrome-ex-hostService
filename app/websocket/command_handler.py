from app.models.message import Message, MessageType, CommandType, MessageRole
from typing import Dict, Any, Callable, Awaitable
from fastapi import WebSocket

class CommandHandler:
    def __init__(self):
        self.commands: Dict[CommandType, Callable[[WebSocket, Message], Awaitable[None]]] = {
            CommandType.HELP: self.handle_help,
            CommandType.CLEAR: self.handle_clear,
            CommandType.RENAME: self.handle_rename,
            CommandType.STATUS: self.handle_status,
            CommandType.UNKNOWN: self.handle_unknown
        }

    async def handle_command(self, websocket: WebSocket, message: Message):
        """处理命令消息"""
        if message.command in self.commands:
            await self.commands[message.command](websocket, message)
        else:
            await self.handle_unknown(websocket, message)

    async def handle_help(self, websocket: WebSocket, message: Message):
        """处理帮助命令"""
        help_text = """可用命令：
        /help - 显示此帮助信息
        /clear - 清除聊天记录
        /rename <新名字> - 修改用户名
        /status - 显示系统状态
        """
        response = Message.create_response(help_text)
        await websocket.send_text(response.to_json())

    async def handle_clear(self, websocket: WebSocket, message: Message):
        """处理清除命令"""
        response = Message.create_response("聊天记录已清除")
        await websocket.send_text(response.to_json())

    async def handle_rename(self, websocket: WebSocket, message: Message):
        """处理重命名命令"""
        new_name = message.data.get("new_name", "")
        if new_name:
            response = Message.create_response(f"用户名已更改为: {new_name}")
        else:
            response = Message.create_error("请指定新的用户名")
        await websocket.send_text(response.to_json())

    async def handle_status(self, websocket: WebSocket, message: Message):
        """处理状态命令"""
        status_data = {
            "status": "running",
            "uptime": "1h 30m",
            "users_online": 1
        }
        response = Message.create_response("系统状态", status_data)
        await websocket.send_text(response.to_json())

    async def handle_unknown(self, websocket: WebSocket, message: Message):
        """处理未知命令"""
        response = Message.create_error(f"未知命令: {message.content}")
        await websocket.send_text(response.to_json()) 