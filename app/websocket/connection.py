from fastapi import WebSocket
import json
from app.models.message import Message, MessageType, MessageRole, CommandType
from .command_handler import CommandHandler
from .context import ContextManager
from typing import Optional
import uuid

class WebSocketConnection:
    def __init__(self):
        self.command_handler = CommandHandler()
        self.context_manager = ContextManager()
        self.websocket: Optional[WebSocket] = None
        self.current_context: Optional[str] = None

    async def initialize_connection(self, websocket: WebSocket) -> None:
        """初始化WebSocket连接"""
        self.websocket = websocket
        await self.websocket.accept()
        
        # 创建新的对话上下文
        conversation_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())  # 在实际应用中，这应该从认证系统获取
        self.current_context = conversation_id
        self.context_manager.create_context(conversation_id, user_id, "游客")
        
        await self.send_welcome_message()

    async def send_welcome_message(self) -> None:
        """发送欢迎消息"""
        welcome_msg = Message(
            type=MessageType.SYSTEM,
            role=MessageRole.SYSTEM,
            content="欢迎加入聊天室！输入 /help 查看可用命令",
            sender="System"
        )
        await self.send_message(welcome_msg)

    async def send_message(self, message: Message) -> None:
        """发送消息并保存到上下文"""
        if self.websocket and self.current_context:
            await self.websocket.send_text(message.to_json())
            context = self.context_manager.get_context(self.current_context)
            if context:
                context.add_message(message)

    async def handle_chat_loop(self) -> None:
        """处理持续的聊天对话"""
        try:
            while True:
                data = await self.websocket.receive_text()
                await self.process_message(data)
        except Exception as e:
            await self.handle_error(str(e))

    async def process_message(self, data: str) -> None:
        """处理接收到的消息"""
        try:
            message_data = json.loads(data)
            content = message_data["content"]
            sender = message_data["sender"]

            if content.startswith('/'):
                await self.handle_command_message(content, sender)
            else:
                await self.handle_chat_message(content, sender)
                
        except json.JSONDecodeError:
            await self.handle_error("消息格式错误")

    async def handle_command_message(self, content: str, sender: str) -> None:
        """处理命令消息"""
        parts = content[1:].split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        message = Message.create_command(
            command=command,
            sender=sender,
            new_name=" ".join(args) if command == "rename" else None
        )
        
        # 保存命令消息到上下文
        if self.current_context:
            context = self.context_manager.get_context(self.current_context)
            if context:
                context.add_message(message)
        
        await self.command_handler.handle_command(self.websocket, message)

    async def handle_chat_message(self, content: str, sender: str) -> None:
        """处理聊天消息"""
        message = Message(
            type=MessageType.CHAT,
            role=MessageRole.USER,
            content=content,
            sender=sender
        )
        await self.send_message(message)

    async def handle_error(self, error_message: str) -> None:
        """处理错误"""
        if self.websocket:
            error_msg = Message.create_error(error_message)
            await self.send_message(error_msg)

    async def cleanup(self) -> None:
        """清理��接"""
        if self.current_context:
            self.context_manager.close_context(self.current_context)
            self.current_context = None
            
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass
            finally:
                self.websocket = None

    async def handle_connection(self, websocket: WebSocket) -> None:
        """主要的连接处理函数"""
        try:
            await self.initialize_connection(websocket)
            await self.handle_chat_loop()
        except Exception as e:
            await self.handle_error(f"发生错误: {str(e)}")
        finally:
            await self.cleanup()