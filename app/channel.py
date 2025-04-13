import asyncio
from typing import Dict, List
from threading import Lock
from uuid import uuid4
from pydantic import BaseModel


class Message(BaseModel):
    user_id: str
    data: dict


class RequestMessage(Message):
    request_id: str


class ResponseMessage(Message):
    request_id: str


class Channel:
    lock = Lock()

    def __init__(self):
        self.channels: Dict[str, List[asyncio.Queue]] = {}

    def create_channel(self, key: str) -> asyncio.Queue:
        with self.lock:
            if key not in self.channels:
                self.channels[key] = asyncio.Queue()
        return self.channels[key]

    def destory_channel(self, key: str):
        with self.lock:
            if key in self.channels:
                del self.channels[key]

    async def send_request(self, user_id: str, data: dict) -> str:
        request_id = str(uuid4())
        message = RequestMessage(
            user_id=user_id, data=data, request_id=request_id)
        key = user_id
        if key not in self.channels:
            raise ValueError(f"Channel {key} not created")
        self.channels[key].put_nowait(message)
        return request_id

    async def send_response(self, user_id: str, request_id: str, data: dict):
        message = ResponseMessage(
            user_id=user_id, data=data, request_id=request_id)
        key = f"{user_id}:{request_id}"
        channel = self.create_channel(key)
        channel.put_nowait(message)

    async def receive_request(self, user_id: str) -> RequestMessage:
        key = user_id
        channel = self.create_channel(key)
        return await channel.get()

    async def receive_response(self, user_id: str, request_id: str, timeout: int = 10) -> ResponseMessage:
        key = f"{user_id}:{request_id}"
        channel = self.create_channel(key)
        try:
            return await asyncio.wait_for(channel.get(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Timeout waiting for response from {user_id} for request {request_id}"
            )

    async def single_request(self, user_id: str, data: dict, timeout: int = 10) -> ResponseMessage:
        request_id = await self.send_request(user_id, data)
        try:
            response = await self.receive_response(user_id, request_id, timeout)
            return response
        finally:
            self.destory_channel(f"{user_id}:{request_id}")


channel = Channel()
