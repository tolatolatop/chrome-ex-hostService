from fastapi import WebSocket
import json
from app.models.message import Message, MessageType

class WebSocketConnection:
    async def handle_connection(self, websocket: WebSocket):
        await websocket.accept()
        
        # 发送系统欢迎消息
        welcome_msg = Message(
            type=MessageType.SYSTEM,
            content="欢迎加入聊天室！",
            sender="System"
        )
        await websocket.send_text(welcome_msg.to_json())
        
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    # 解析接收到的JSON数据
                    message_data = json.loads(data)
                    message = Message(
                        type=message_data.get("type", MessageType.CHAT),
                        content=message_data["content"],
                        sender=message_data["sender"]
                    )
                    
                    # 发送确认消息
                    await websocket.send_text(message.to_json())
                    
                except json.JSONDecodeError:
                    error_msg = Message(
                        type=MessageType.ERROR,
                        content="消息格式错误",
                        sender="System"
                    )
                    await websocket.send_text(error_msg.to_json())
                    
        except Exception as e:
            error_msg = Message(
                type=MessageType.ERROR,
                content=f"发生错误: {str(e)}",
                sender="System"
            )
            await websocket.send_text(error_msg.to_json())
        finally:
            await websocket.close()