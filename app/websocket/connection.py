from fastapi import WebSocket
import json
from app.models.message import Message, MessageType, MessageRole, CommandType
from .command_handler import CommandHandler

class WebSocketConnection:
    def __init__(self):
        self.command_handler = CommandHandler()

    async def handle_connection(self, websocket: WebSocket):
        await websocket.accept()
        
        # 发送系统欢迎消息
        welcome_msg = Message(
            type=MessageType.SYSTEM,
            role=MessageRole.SYSTEM,
            content="欢迎加入聊天室！输入 /help 查看可用命令",
            sender="System"
        )
        await websocket.send_text(welcome_msg.to_json())
        
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    # 解析接收到的JSON数据
                    message_data = json.loads(data)
                    content = message_data["content"]

                    # 检查是否是命令
                    if content.startswith('/'):
                        # 解析命令
                        parts = content[1:].split()
                        command = parts[0]
                        args = parts[1:] if len(parts) > 1 else []
                        
                        # 创建命令消息
                        message = Message.create_command(
                            command=command,
                            sender=message_data["sender"],
                            new_name=" ".join(args) if command == "rename" else None
                        )
                        
                        # 处理命令
                        await self.command_handler.handle_command(websocket, message)
                    else:
                        # 处理普通聊天消息
                        message = Message(
                            type=MessageType.CHAT,
                            role=MessageRole.USER,
                            content=content,
                            sender=message_data["sender"]
                        )
                        await websocket.send_text(message.to_json())
                    
                except json.JSONDecodeError:
                    error_msg = Message.create_error("消息格式错误")
                    await websocket.send_text(error_msg.to_json())
                    
        except Exception as e:
            error_msg = Message.create_error(f"发生错误: {str(e)}")
            await websocket.send_text(error_msg.to_json())
        finally:
            await websocket.close()