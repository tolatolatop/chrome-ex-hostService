import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
import asyncio
from typing import List, Dict, Any, AsyncGenerator
import aiohttp


@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)


# @pytest.fixture(autouse=True)
# def reset_connections():
#     """在每个测试前重置连接状态"""
#     ws_connection.active_connections.clear()
#     ws_connection.connection_contexts.clear()


@pytest.mark.asyncio
async def test_websocket_connection_flow(test_client):
    # 测试完整的连接生命周期
    with test_client.websocket_connect("/ws") as websocket:
        # 验证连接建立消息
        response = websocket.receive_text()
        data = json.loads(response)
        assert data["type"] == "connection_established"
        connection_id = data["connection_id"]

        # 验证用户加入广播
        with test_client.websocket_connect("/ws") as websocket2:
            response = websocket2.receive_text()
            data2 = json.loads(response)
            connection_id2 = data2["connection_id"]

            # 第一个连接应该收到第二个用户的加入通知
            response = websocket.receive_text()
            join_data = json.loads(response)
            assert join_data == {
                "type": "user_joined",
                "connection_id": connection_id2
            }

        # 第二个连接断开后，第一个应收到离开通知
        response = websocket.receive_text()
        leave_data = json.loads(response)
        assert leave_data == {
            "type": "user_left",
            "connection_id": connection_id2
        }


@pytest.mark.asyncio
async def test_message_handling(test_client):
    # 测试消息处理流程
    with test_client.websocket_connect("/ws") as client1:
        # 获取client1的连接ID
        response = client1.receive_text()
        client1_id = json.loads(response)["connection_id"]

        with test_client.websocket_connect("/ws") as client2:
            response = client2.receive_text()
            client2_id = json.loads(response)["connection_id"]
            client1.receive_text()  # 跳过client2加入消息

            # 测试普通消息
            client1.send_text(json.dumps({
                "type": "message",
                "content": "Hello all"
            }))

            # 验证client2收到消息
            response = client2.receive_text()
            data = json.loads(response)
            assert data == {
                "type": "message",
                "from": client1_id,
                "content": "Hello all"
            }

            # 测试私聊消息
            client2.send_text(json.dumps({
                "type": "private_message",
                "target": client1_id,
                "content": "Secret"
            }))

            # 验证client1收到私聊
            response = client1.receive_text()
            private_data = json.loads(response)
            assert private_data == {
                "type": "private_message",
                "from": client2_id,
                "content": "Secret"
            }

            # 测试广播消息
            client1.send_text(json.dumps({
                "type": "broadcast",
                "content": "Broadcast!"
            }))

            # client2应收到广播
            response = client2.receive_text()
            broadcast_data = json.loads(response)
            assert broadcast_data == {
                "type": "broadcast",
                "from": client1_id,
                "content": "Broadcast!"
            }


@pytest.mark.asyncio
async def test_error_handling(test_client):
    # 测试错误处理场景
    with test_client.websocket_connect("/ws") as client:
        client.receive_text()  # 跳过连接消息

        # 测试发送无效JSON
        print("\n=== 测试发送无效JSON ===")
        client.send_text("invalid json")
        response = client.receive_text()
        error_data = json.loads(response)
        assert error_data["type"] == "error"
        assert error_data["message"] == "Invalid JSON format"

        # 测试发送非字典JSON
        print("\n=== 测试发送非字典JSON ===")
        client.send_text(json.dumps(["array", "not", "object"]))
        response = client.receive_text()
        error_data = json.loads(response)
        assert error_data["type"] == "error"
        assert error_data["message"] == "Message must be a JSON object"

        # 测试发送未知消息类型
        print("\n=== 测试发送未知消息类型 ===")
        client.send_text(json.dumps({
            "type": "unknown_type",
            "content": "test"
        }))
        response = client.receive_text()
        error_data = json.loads(response)
        assert error_data["type"] == "error"
        assert "Unsupported message type" in error_data["message"]

        # 测试发送无效的私聊目标
        print("\n=== 测试发送无效的私聊目标 ===")
        client.send_text(json.dumps({
            "type": "private_message",
            "target": "invalid_id",
            "content": "test"
        }))
        response = client.receive_text()
        error_data = json.loads(response)
        assert error_data["type"] == "error"
        assert "Target connection" in error_data["message"]

        # 测试发送缺少必要字段的私聊消息
        print("\n=== 测试发送缺少目标的私聊消息 ===")
        client.send_text(json.dumps({
            "type": "private_message",
            "content": "test"
        }))
        response = client.receive_text()
        error_data = json.loads(response)
        assert error_data["type"] == "error"
        assert "must have a target" in error_data["message"]


@pytest.mark.asyncio
async def test_concurrent_connections(test_client):
    # 测试并发连接处理
    async def connect_and_send(client):
        with test_client.websocket_connect("/ws") as ws:
            # 获取连接ID
            response = ws.receive_text()
            conn_id = json.loads(response)["connection_id"]

            # 发送测试消息
            ws.send_text(json.dumps({
                "type": "message",
                "content": "test"
            }))
            return conn_id

    # 创建多个并发连接
    tasks = [connect_and_send(test_client) for _ in range(3)]
    results = await asyncio.gather(*tasks)

    # 验证所有连接ID唯一
    assert len(set(results)) == 3


@pytest.mark.asyncio
async def test_chat_completions_basic(test_client):
    """测试基本的非流式对话功能"""
    response = test_client.post("/v1/chat/completions", json={
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "stream": False
    })

    assert response.status_code == 200
    data = response.json()

    # 验证响应格式
    assert "id" in data
    assert data["model"] == "gpt-3.5-turbo"
    assert isinstance(data["created"], int)
    assert len(data["choices"]) == 1
    assert "message" in data["choices"][0]
    assert "role" in data["choices"][0]["message"]
    assert "content" in data["choices"][0]["message"]
    assert "finish_reason" in data["choices"][0]
    assert "usage" in data

    # 验证usage字段
    assert "prompt_tokens" in data["usage"]
    assert "completion_tokens" in data["usage"]
    assert "total_tokens" in data["usage"]


@pytest.mark.asyncio
async def test_chat_completions_stream(test_client):
    """测试流式对话功能"""
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8000/v1/chat/completions",
                                json={
                "messages": [{"role": "user", "content": "你好"}],
                "stream": True
                                    }
        ) as response:
            assert response.status == 200

            # 收集所有的流式响应
            chunks: List[Dict[str, Any]] = []
            content = ""

            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    if line == 'data: [DONE]':
                        break

                    data = json.loads(line[6:])  # 去掉 "data: " 前缀
                    chunks.append(data)

                    # 收集内容
                    if "content" in data["choices"][0]["delta"]:
                        content += data["choices"][0]["delta"]["content"]

            # 验证流式响应
            assert len(chunks) > 0
            assert content  # 确保有内容生成

            # 验证第一个chunk包含role
            assert "role" in chunks[0]["choices"][0]["delta"]
            assert chunks[0]["choices"][0]["delta"]["role"] == "assistant"

            # 验证最后一个chunk包含finish_reason
            assert chunks[-1]["choices"][0]["finish_reason"] == "stop"


@pytest.mark.asyncio
async def test_chat_completions_parameters(test_client):
    """测试对话参数设置"""
    response = test_client.post("/v1/chat/completions", json={
        "messages": [
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好"}
        ],
        "model": "gpt-4",
        "temperature": 0.5,
        "max_tokens": 100,
        "stream": False
    })

    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "gpt-4"  # 验证模型参数是否正确传递


@pytest.mark.asyncio
async def test_chat_completions_validation(test_client):
    """测试请求参数验证"""
    # 测试空消息列表
    response = test_client.post("/v1/chat/completions", json={
        "messages": [],
        "stream": False
    })
    assert response.status_code == 422

    # 测试无效的temperature值
    response = test_client.post("/v1/chat/completions", json={
        "messages": [{"role": "user", "content": "你好"}],
        "temperature": 3.0,
        "stream": False
    })
    assert response.status_code == 422

    # 测试无效的role值
    response = test_client.post("/v1/chat/completions", json={
        "messages": [{"role": "invalid_role", "content": "你好"}],
        "stream": False
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_completions_conversation(test_client):
    """测试多轮对话"""
    messages = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！我是一个AI助手。"},
        {"role": "user", "content": "今天天气真好"}
    ]

    response = test_client.post("/v1/chat/completions", json={
        "messages": messages,
        "stream": False
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data["choices"]) == 1
    assert "content" in data["choices"][0]["message"]


@pytest.mark.asyncio
async def test_chat_completions_error_handling(test_client):
    """测试错误处理"""
    # 测试无效的JSON
    response = test_client.post(
        "/v1/chat/completions",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422

    # 测试缺少必要字段
    response = test_client.post("/v1/chat/completions", json={
        "stream": False
    })
    assert response.status_code == 422

    # 测试无效的消息格式
    response = test_client.post("/v1/chat/completions", json={
        "messages": [{"invalid_field": "test"}],
        "stream": False
    })
    assert response.status_code == 422
