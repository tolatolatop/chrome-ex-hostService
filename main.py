from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from enum import Enum
import json
from datetime import datetime

app = FastAPI()

# 定义消息类型枚举
class MessageType(str, Enum):
    CHAT = "chat"
    SYSTEM = "system"
    ERROR = "error"

# 定义消息模型
class Message(BaseModel):
    type: MessageType
    content: str
    sender: str
    timestamp: datetime = datetime.now()

    def to_json(self):
        return json.dumps({
            "type": self.type,
            "content": self.content,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat()
        })

# HTML 页面更新以支持新的消息格式
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket 聊天</title>
        <style>
            .system { color: gray; }
            .error { color: red; }
            .chat { color: black; }
        </style>
    </head>
    <body>
        <h1>WebSocket 聊天示例</h1>
        <div>
            <label for="username">用户名:</label>
            <input type="text" id="username" value="游客" />
        </div>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>发送</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var data = JSON.parse(event.data)
                
                message.className = data.type
                var time = new Date(data.timestamp).toLocaleTimeString()
                var content = document.createTextNode(`[${time}] ${data.sender}: ${data.content}`)
                
                message.appendChild(content)
                messages.appendChild(message)
            };
            
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                var username = document.getElementById("username")
                
                if (input.value) {
                    var message = {
                        type: "chat",
                        content: input.value,
                        sender: username.value
                    }
                    ws.send(JSON.stringify(message))
                    input.value = ''
                }
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
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