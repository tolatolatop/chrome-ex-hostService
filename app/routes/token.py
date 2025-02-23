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
import uuid

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>生成重定向链接</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .container {
                background-color: #f5f5f5;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            input[type="text"] {
                width: 100%;
                padding: 8px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
            #result {
                margin-top: 20px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>生成重定向链接</h1>
            <div>
                <label for="url">请输入目标网址：</label>
                <input type="text" id="url" placeholder="例如: www.example.com">
                <button onclick="generateRedirect()">生成链接</button>
            </div>
            <div id="result"></div>
        </div>
        
        <script>
            async function generateRedirect() {
                const url = document.getElementById('url').value;
                if (!url) {
                    alert('请输入有效的网址');
                    return;
                }
                
                const token = Math.random().toString(36).substring(2);
                const redirectUrl = `/redirect?url=${encodeURIComponent(url)}&token=${token}`;
                
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = `
                    <p>生成的重定向链接：</p>
                    <p><a href="${redirectUrl}" target="_blank">${window.location.origin}${redirectUrl}</a></p>
                `;
            }
        </script>
    </body>
    </html>
    """


@router.get("/redirect")
async def redirect(url: str, token: str):
    cookie_settings = (
        f"token={token}; "
        "SameSite=Lax; "  # 允许在同源 iframe 中访问
        "Path=/"  # 设置 cookie 路径
    )
    return RedirectResponse(
        url=f"http://{url}",  # 使用 http 而不是 https
        headers={"Set-Cookie": cookie_settings}
    )


key_value_db = {}


@router.post("/token")
async def token(request: Request):
    data = await request.json()
    key_value_db[data["id"]] = data["value"]
    return {"id": data["id"], "value": data["value"]}
