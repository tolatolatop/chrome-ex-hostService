import re

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Header
from sqlalchemy.orm import Session
from typing import List
from app.channel import channel

router = APIRouter(
    prefix="/baidu",
    tags=["baidu"],
    responses={404: {"description": "Not found"}},
)


@router.get("/get_username")
async def get_username(
    x_user_id: str = Header(..., description="用户ID")
):
    message = {
        "type": "fetch",
        "name": "visitBaidu",
    }
    try:
        response = await channel.single_request(x_user_id, message, timeout=10)
        username = re.search(r'username:"([^"]+)"', response.data['text'])
        if username:
            return {"username": username.group(1)}
        else:
            return {"error": "未找到用户名"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
