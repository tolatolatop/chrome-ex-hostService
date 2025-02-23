from fastapi import APIRouter, WebSocket, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.responses import RedirectResponse
from app.templates.chat import html
from app.websocket.connection import WebSocketConnection
from typing import List, Optional, Dict, Any
import json
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime

router = APIRouter()


@router.get("/redirect")
async def redirect(url: str):
    return RedirectResponse(url=f"https://{url}")


key_value_db = {}


@router.post("/token")
async def token(request: Request):
    data = await request.json()
    key_value_db[data["id"]] = data["value"]
    return {"id": data["id"], "value": data["value"]}
