from fastapi import APIRouter, WebSocket, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from app.templates.chat import html
from app.websocket.connection import WebSocketConnection
from typing import List, Optional, Dict, Any
import json
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime

router = APIRouter()
ws_connection = WebSocketConnection()


class Message(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色：system/user/assistant")
    content: str = Field(..., description="消息内容")
    name: Optional[str] = Field(None, description="可选的消息发送者名称")


class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[Message] = Field(..., description="消息历史")
    stream: bool = Field(False, description="是否使用流式响应")
    model: str = Field("gpt-3.5-turbo", description="使用的模型名称")
    temperature: float = Field(0.7, description="温度参数", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, description="最大生成token数")


class ChatResponse(BaseModel):
    """非流式聊天响应模型"""
    id: str = Field(..., description="响应ID")
    model: str = Field(..., description="使用的模型")
    created: int = Field(..., description="创建时间戳")
    choices: List[Dict[str, Any]] = Field(..., description="响应选项")
    usage: Dict[str, int] = Field(..., description="token使用统计")


class ChatStreamResponse(BaseModel):
    """流式聊天响应模型"""
    id: str = Field(..., description="响应ID")
    model: str = Field(..., description="使用的模型")
    created: int = Field(..., description="创建时间戳")
    choices: List[Dict[str, Any]] = Field(..., description="当前chunk的选项")


async def fake_chat_stream():
    """模拟流式聊天响应"""
    response_id = "chat-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    chunks = ["我", "是", "一个", "模拟", "的", "流式", "响应", "。"]

    for i, chunk in enumerate(chunks):
        response = ChatStreamResponse(
            id=response_id,
            model="gpt-3.5-turbo",
            created=int(datetime.now().timestamp()),
            choices=[{
                "index": 0,
                "delta": {
                    "role": "assistant" if i == 0 else None,
                    "content": chunk
                },
                "finish_reason": "stop" if i == len(chunks) - 1 else None
            }]
        )
        yield f"data: {response.json()}\n\n"
        await asyncio.sleep(0.2)

    yield "data: [DONE]\n\n"


@router.get("/")
async def get():
    return HTMLResponse(html)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_connection.handle_connection(websocket)


@router.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """ChatGPT风格的对话接口"""
    if request.stream:
        # 流式响应
        return StreamingResponse(
            fake_chat_stream(),
            media_type="text/event-stream"
        )
    else:
        # 非流式响应
        await asyncio.sleep(1)  # 模拟处理延迟
        return ChatResponse(
            id=f"chat-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            model=request.model,
            created=int(datetime.now().timestamp()),
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "这是一个模拟的非流式响应。"
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        )
