from typing import Dict, Any, Optional, Union
import json

import httpx
from .base import BaseCommand
from fastapi import WebSocket
from app.models.message import Message, CommandType, MessageType
from pydantic import BaseModel

class FetchCommandData(BaseModel):
    """获取数据命令数据"""
    url: str
    method: str
    headers: Dict[str, str] = {}
    data: Optional[Union[Dict[str, Any], str]] = None

class FetchCommand(BaseCommand):
    command_name = CommandType.FETCH

    async def execute(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        data = FetchCommandData(
            url="https://example.com",
            method="GET",
        )
        await self.send_fetch_request(websocket, data)
        fetch_response = await self.handle_fetch_response(websocket)
        await self.send_response(websocket, content="", data=fetch_response.data)

    async def send_fetch_request(self, websocket: WebSocket, data: FetchCommandData) -> None:
        """发送获取数据请求"""
        fetch_command = Message.create_system_command(CommandType.FETCH, data=data.model_dump())
        await websocket.send_text(fetch_command.to_json())

    async def handle_fetch_response(self, websocket: WebSocket) -> Message:
        """处理获取数据响应"""
        data = await websocket.receive_text()
        fetch_response = Message.create_fetch_response(json.loads(data)['data'])
        return fetch_response
        
