from fastapi import WebSocket
import json
from app.models.message import Message, MessageType, MessageRole, CommandType
from .command_handler import CommandHandler
from typing import Optional

class WebSocketConnection:
    def __init__(self):
        self.command_handler = CommandHandler()
        self.websocket: Optional[WebSocket] = None

    async def initialize_connection(self, websocket: WebSocket) -> None:
        """初始化WebSocket连接"""
        self.websocket = websocket
        await self.websocket.accept()
        await self.send_welcome_message()

    async def send_welcome_message(self) -> None:
        """发送欢迎消息"""
        welcome_msg = Message(
            type=MessageType.SYSTEM,
            role=MessageRole.SYSTEM,
            content="欢迎加入聊天室！输入 /help 查看可用命令",
            sender="System"
        )
        await self.websocket.send_text(welcome_msg.to_json())

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
            # 解析接收到的JSON数据
            message_data = json.loads(data)
            content = message_data["content"]

            # 检查是否是命令
            if content.startswith('/'):
                await self.handle_command_message(content, message_data["sender"])
            else:
                await self.handle_chat_message(content, message_data["sender"])
                
        except json.JSONDecodeError:
            await self.handle_error("消息格式错误")

    async def handle_command_message(self, content: str, sender: str) -> None:
        """处理命令消息"""
        # 解析命令
        parts = content[1:].split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # 创建命令消息
        message = Message.create_command(
            command=command,
            sender=sender,
            new_name=" ".join(args) if command == "rename" else None
        )
        
        # 处理命令
        await self.command_handler.handle_command(self.websocket, message)

    async def handle_chat_message(self, content: str, sender: str) -> None:
        """处理聊天消息"""
        message = Message(
            type=MessageType.CHAT,
            role=MessageRole.USER,
            content=content,
            sender=sender
        )
        await self.websocket.send_text(message.to_json())

    async def handle_error(self, error_message: str) -> None:
        """处理错误"""
        if self.websocket:
            error_msg = Message.create_error(error_message)
            await self.websocket.send_text(error_msg.to_json())

    async def cleanup(self) -> None:
        """清理连接"""
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass  # 忽略关闭时的错误
            finally:
                self.websocket = None

    async def handle_connection(self, websocket: WebSocket) -> None:
        """主要的连接处理函数"""
        try:
            # 1. 初始化连接
            await self.initialize_connection(websocket)
            
            # 2. 处理持续对话
            await self.handle_chat_loop()
            
        except Exception as e:
            # 3. 处理意外错误
            await self.handle_error(f"发生错误: {str(e)}")
            
        finally:
            # 4. 清理连接
            await self.cleanup()