import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from app.main import app
from app.models.message import Message, MessageType, MessageRole, CommandType
from app.commands.fetch_command import FetchCommandData
import json
from datetime import datetime

client = TestClient(app)

def test_message_model():
    """测试消息模型的创建和序列化"""
    # 测试普通聊天消息
    message = Message(
        type=MessageType.CHAT,
        role=MessageRole.USER,
        content="测试消息",
        sender="测试用户"
    )
    
    # 测试消息属性
    assert message.type == MessageType.CHAT
    assert message.role == MessageRole.USER
    assert message.content == "测试消息"
    assert message.sender == "测试用户"
    assert isinstance(message.timestamp, datetime)
    
    # 测试JSON序列化
    json_data = message.to_json()
    parsed_data = json.loads(json_data)
    
    assert parsed_data["type"] == MessageType.CHAT
    assert parsed_data["role"] == MessageRole.USER
    assert parsed_data["content"] == "测试消息"
    assert parsed_data["sender"] == "测试用户"
    assert "timestamp" in parsed_data

def test_message_factory_methods():
    """测试消息工厂方法"""
    # 测试命令消息创建
    cmd_msg = Message.create_command("help", "测试用户")
    assert cmd_msg.type == MessageType.COMMAND
    assert cmd_msg.role == MessageRole.USER
    assert cmd_msg.command == CommandType.HELP

    # 测试响应消息创建
    resp_msg = Message.create_response("测试响应")
    assert resp_msg.type == MessageType.RESPONSE
    assert resp_msg.role == MessageRole.SYSTEM
    assert resp_msg.sender == "system"

    # 测试错误消息创建
    error_msg = Message.create_error("测试错误")
    assert error_msg.type == MessageType.ERROR
    assert error_msg.role == MessageRole.SYSTEM
    assert error_msg.sender == "System"

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
        assert welcome_data["role"] == "system"
        assert welcome_data["content"] == "欢迎加入聊天室！输入 /help 查看可用命令"
        assert welcome_data["sender"] == "System"

        # 测试发送聊天消息
        test_message = {
            "type": "chat",
            "role": "user",
            "content": "你好，世界！",
            "sender": "测试用户"
        }
        websocket.send_json(test_message)
        
        # 测试接收回复
        response = websocket.receive_json()
        assert response["type"] == "chat"
        assert response["role"] == "user"
        assert response["content"] == "你好，世界！"
        assert response["sender"] == "测试用户"

@pytest.mark.asyncio
async def test_command_handling():
    """测试命令处理"""
    with client.websocket_connect("/ws") as websocket:
        # 跳过欢迎消息
        websocket.receive_json()
        
        # 测试帮助命令
        help_message = {
            "type": "chat",
            "role": "user",
            "content": "/help",
            "sender": "测试用户"
        }
        websocket.send_json(help_message)
        
        response = websocket.receive_json()
        assert response["type"] == "response"
        assert response["role"] == "system"
        assert "可用命令" in response["content"]
        
        # 测试重命名命令
        rename_message = {
            "type": "chat",
            "role": "user",
            "content": "/rename 新用户",
            "sender": "测试用户"
        }
        websocket.send_json(rename_message)
        
        response = websocket.receive_json()
        assert response["type"] == "response"
        assert response["role"] == "system"
        assert "用户名已更改为: 新用户" in response["content"]

def test_invalid_message_format():
    """测试发送无效消息格式"""
    with client.websocket_connect("/ws") as websocket:
        # 跳过欢迎消息
        websocket.receive_json()
        
        # 发送无效的JSON数据
        websocket.send_text("invalid json data")
        
        # 测试错误响应
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["role"] == "system"
        assert response["content"] == "消息格式错误"
        assert response["sender"] == "System"

@pytest.mark.asyncio
async def test_unknown_command():
    """测试未知命令"""
    with client.websocket_connect("/ws") as websocket:
        # 跳过欢迎消息
        websocket.receive_json()
        
        # 发送未知命令
        unknown_cmd = {
            "type": "chat",
            "role": "user",
            "content": "/unknown_command",
            "sender": "测试用户"
        }
        websocket.send_json(unknown_cmd)
        
        # 测试错误响应
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["role"] == "system"
        assert "未知命令" in response["content"]

@pytest.mark.asyncio
async def test_fetch_command():
    """测试fetch命令"""
    with client.websocket_connect("/ws") as websocket:
        # 跳过欢迎消息
        websocket.receive_json()
        
        # 测试fetch命令
        fetch_message = {
            "type": "chat",
            "role": "user",
            "content": "/fetch test_data",
            "sender": "测试用户"
        }
        websocket.send_json(fetch_message)
        
        # 测试接收fetch响应
        response = websocket.receive_json()
        assert response["type"] == "command"
        assert response["role"] == "system"
        data = FetchCommandData(**response["data"])
        assert data.url == "https://example.com"
        assert data.method == "GET"

        websocket.send_text(Message.create_fetch_response({"content": "test_data"}).to_json())

        # 验证返回的数据结构
        response = websocket.receive_json()
        assert response["type"] == "response"
        assert response["role"] == "system"
        data = response["data"]
        assert isinstance(data, dict)
        assert data["content"] == "test_data"
