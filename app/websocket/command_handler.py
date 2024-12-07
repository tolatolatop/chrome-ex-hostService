from app.models.message import Message, MessageType, CommandType, MessageRole
from app.exceptions import NoContextError, NoUserContextError
from .context import ContextManager
from typing import Dict, Any, Callable, Awaitable, Optional
from fastapi import WebSocket
from datetime import datetime

class CommandHandler:
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
        self.commands: Dict[CommandType, Callable[[WebSocket, Message, str], Awaitable[None]]] = {
            CommandType.HELP: self.handle_help,
            CommandType.CLEAR: self.handle_clear,
            CommandType.RENAME: self.handle_rename,
            CommandType.STATUS: self.handle_status,
            CommandType.HISTORY: self.handle_history,
            CommandType.UNKNOWN: self.handle_unknown
        }

    def get_context(self, conversation_id: str):
        """获取上下文，如果不存在则抛出异常"""
        context = self.context_manager.get_context(conversation_id)
        if not context:
            raise NoContextError(f"无法找到聊天上下文: {conversation_id}")
        return context

    def get_user_context(self, conversation_id: str):
        """获取用户上下文，如果不存在则抛出异常"""
        context = self.get_context(conversation_id)
        if not context.user_context:
            raise NoUserContextError(f"无法找到用户上下文: {conversation_id}")
        return context.user_context

    async def handle_command(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        """处理命令消息"""
        try:
            handler = self.commands.get(message.command, self.handle_unknown)
            await handler(websocket, message, conversation_id)
        except (NoContextError, NoUserContextError) as e:
            response = Message.create_error(str(e))
            await websocket.send_text(response.to_json())

    async def handle_help(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        """处理帮助命令"""
        help_text = """可用命令：
        /help - 显示此帮助信息
        /clear - 清除聊天记录
        /rename <新名字> - 修改用户名
        /status - 显示系统状态
        /history <数量> - 显示历史消息
        """
        response = Message.create_response(help_text)
        await websocket.send_text(response.to_json())

    async def handle_clear(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        """处理清除命令"""
        context = self.get_context(conversation_id)
        context.clear_history()
        response = Message.create_response("聊天记录已清除")
        await websocket.send_text(response.to_json())

    async def handle_rename(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        """处理重命名命令"""
        user_context = self.get_user_context(conversation_id)
        new_name = message.data.get("new_name", "")
        
        if not new_name:
            response = Message.create_error("请指定新的用户名")
        else:
            self.context_manager.update_username(user_context.user_id, new_name)
            response = Message.create_response(f"用户名已更改为: {new_name}")
        
        await websocket.send_text(response.to_json())

    async def handle_status(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        """处理状态命令"""
        context = self.get_context(conversation_id)
        user_context = self.get_user_context(conversation_id)
        current_time = datetime.now()
        
        status_data = {
            "conversation_id": context.conversation_id,
            "started_at": context.started_at.isoformat(),
            "duration": str(current_time - context.started_at),
            "message_count": user_context.message_count,
            "username": user_context.username,
            "last_active": user_context.last_active.isoformat()
        }
        
        response = Message.create_response("系统状态", data=status_data)
        await websocket.send_text(response.to_json())

    async def handle_history(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        """处理历史记录命令"""
        try:
            count = int(message.data.get("count", "5"))
        except ValueError:
            count = 5

        context = self.get_context(conversation_id)
        messages = context.get_last_n_messages(count)
        history_text = "\n".join([
            f"[{msg.timestamp.strftime('%H:%M:%S')}] {msg.sender}: {msg.content}"
            for msg in messages
        ])
        
        response = Message.create_response(
            f"最近 {len(messages)} 条消息:\n{history_text}" if messages else "没有历史消息"
        )
        await websocket.send_text(response.to_json())

    async def handle_unknown(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        """处理未知命令"""
        response = Message.create_error(f"未知命令: {message.content}")
        await websocket.send_text(response.to_json()) 