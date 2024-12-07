import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from app.main import app
from app.models.message import Message, MessageType
import json
from datetime import datetime

client = TestClient(app)

def test_message_model():
    """测试消息模型的创建和序列化"""
    message = Message(
        type=MessageType.CHAT,
        content="测试消息",
        sender="测试用户"
    )
    
    # 测试消息属性
    assert message.type == MessageType.CHAT
    assert message.content == "测试消息"
    assert message.sender == "测试用户"
    assert isinstance(message.timestamp, datetime)
    
    # 测试JSON序列化
    json_data = message.to_json()
    parsed_data = json.loads(json_data)
    
    assert parsed_data["type"] == MessageType.CHAT
    assert parsed_data["content"] == "测试消息"
    assert parsed_data["sender"] == "测试用户"
    assert "timestamp" in parsed_data

def test_get_html_endpoint():
    """测试HTML页面端点"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "WebSocket 聊天示例" in response.text

@pytest.mark.asyncio
async def test_websocket_connection():
    """测试WebSocket连接和消息发送"""
    with client.websocket_connect("/ws") as websocket:
        # 测试接收欢迎消息
        welcome_data = websocket.receive_json()
        assert welcome_data["type"] == "system"
        assert welcome_data["content"] == "欢迎加入聊天室！"
        assert welcome_data["sender"] == "System"

        # 测试发送聊天消息
        test_message = {
            "type": "chat",
            "content": "你好，世界！",
            "sender": "测试用户"
        }
        websocket.send_json(test_message)
        
        # 测试接收回复
        response = websocket.receive_json()
        assert response["type"] == "chat"
        assert response["content"] == "你好，世界！"
        assert response["sender"] == "测试用户"

def test_invalid_message_format():
    """测试发送无效消息格式"""
    with client.websocket_connect("/ws") as websocket:
        # 跳过欢迎消息
        websocket.receive_json()
        
        # 发送无效的JSON数据
        websocket.send_text("invalid json data")
        
