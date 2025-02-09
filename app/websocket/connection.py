from fastapi import WebSocket
import json
from typing import Optional, Dict, Set
import uuid
from app.exceptions import ChatError


class WebSocketConnection:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_contexts: Dict[str, Dict] = {}

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
