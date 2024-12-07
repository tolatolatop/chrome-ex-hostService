from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse
from app.templates.chat import html
from app.websocket.connection import WebSocketConnection

router = APIRouter()
ws_connection = WebSocketConnection()

@router.get("/")
async def get():
    return HTMLResponse(html)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_connection.handle_connection(websocket)