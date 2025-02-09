from fastapi import WebSocket
import json
from typing import Optional, Dict, Set, Any, Callable
import uuid
from app.exceptions import ChatError


class WebSocketConnection:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_contexts: Dict[str, Dict] = {}
        # 初始化消息处理器映射
        self._message_handlers: Dict[str, Callable] = {
            "private_message": self._handle_private_message,
            "broadcast": self._handle_broadcast_message,
            "message": self._handle_normal_message,
        }

    async def connect(self, websocket: WebSocket) -> str:
        """建立新的websocket连接，返回连接的唯一标识符"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        self.connection_contexts[connection_id] = {}
        return connection_id

    def disconnect(self, connection_id: str):
        """断开指定的websocket连接"""
        if connection_id in self.active_connections:
            self.active_connections.pop(connection_id)
            self.connection_contexts.pop(connection_id)

    async def send_message(self, connection_id: str, message: str):
        """向指定的websocket连接发送消息"""
        if connection_id not in self.active_connections:
            raise ChatError(f"Connection {connection_id} not found")
        await self.active_connections[connection_id].send_text(message)

    async def broadcast(self, message: str, exclude: Optional[Set[str]] = None):
        """向所有websocket连接广播消息，可以选择排除特定的连接"""
        exclude = exclude or set()
        for connection_id, connection in self.active_connections.items():
            if connection_id not in exclude:
                await connection.send_text(message)

    def set_context(self, connection_id: str, key: str, value: any):
        """为指定的websocket连接设置上下文值"""
        if connection_id not in self.connection_contexts:
            raise ChatError(f"Connection {connection_id} not found")
        self.connection_contexts[connection_id][key] = value

    def get_context(self, connection_id: str, key: str, default: any = None) -> any:
        """获取指定websocket连接的上下文值"""
        if connection_id not in self.connection_contexts:
            raise ChatError(f"Connection {connection_id} not found")
        return self.connection_contexts[connection_id].get(key, default)

    def get_all_connections(self) -> Set[str]:
        """获取所有活动连接的ID"""
        return set(self.active_connections.keys())

    def is_connected(self, connection_id: str) -> bool:
        """检查指定的连接是否存在且活动"""
        return connection_id in self.active_connections

    async def _handle_private_message(self, connection_id: str, message_data: Dict[str, Any]) -> None:
        """处理私聊消息"""
        if "target" not in message_data:
            raise ChatError("Private message must have a target")

        target_id = message_data["target"]
        content = message_data.get("content", "")

        if not self.is_connected(target_id):
            raise ChatError(f"Target connection {target_id} not found")

        await self.send_message(target_id, json.dumps({
            "type": "private_message",
            "from": connection_id,
            "content": content
        }))

    async def _handle_broadcast_message(self, connection_id: str, message_data: Dict[str, Any]) -> None:
        """处理广播消息"""
        content = message_data.get("content", "")
        await self.broadcast(json.dumps({
            "type": "broadcast",
            "from": connection_id,
            "content": content
        }), exclude={connection_id})

    async def _handle_normal_message(self, connection_id: str, message_data: Dict[str, Any]) -> None:
        """处理普通消息"""
        content = message_data.get("content", "")
        await self.broadcast(json.dumps({
            "type": "message",
            "from": connection_id,
            "content": content
        }), exclude={connection_id})

    async def _handle_raw_message(self, connection_id: str, data: str) -> None:
        """处理原始文本消息"""
        await self.broadcast(data, exclude={connection_id})

    async def handle_message(self, connection_id: str, data: str) -> None:
        """处理接收到的WebSocket消息

        Args:
            connection_id: 发送消息的连接ID
            data: 接收到的原始消息数据
        """
        try:
            message_data = json.loads(data)
            if not isinstance(message_data, dict):
                await self._handle_raw_message(connection_id, data)
                return

            message_type = message_data.get("type", "message")
            handler = self._message_handlers.get(message_type)

            if handler:
                await handler(connection_id, message_data)
            else:
                # 如果没有找到对应的处理器，使用普通消息处理器
                await self._handle_normal_message(connection_id, message_data)

        except json.JSONDecodeError:
            await self._handle_raw_message(connection_id, data)
        except ChatError as e:
            # 发送错误消息给发送者
            await self.send_message(connection_id, json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def handle_connection(self, websocket: WebSocket):
        """处理WebSocket连接的完整生命周期"""
        connection_id = await self.connect(websocket)
        try:
            # 发送连接成功消息，包含连接ID
            await self.send_message(connection_id, json.dumps({
                "type": "connection_established",
                "connection_id": connection_id
            }))

            # 广播新用户加入消息
            await self.broadcast(json.dumps({
                "type": "user_joined",
                "connection_id": connection_id
            }), exclude={connection_id})

            while True:
                # 接收消息
                data = await websocket.receive_text()
                await self.handle_message(connection_id, data)

        except Exception as e:
            # 发送错误消息给客户端
            try:
                await self.send_message(connection_id, json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
            except:
                pass
        finally:
            # 广播用户离开消息
            try:
                await self.broadcast(json.dumps({
                    "type": "user_left",
                    "connection_id": connection_id
                }), exclude={connection_id})
            except:
                pass
            # 断开连接
            self.disconnect(connection_id)
