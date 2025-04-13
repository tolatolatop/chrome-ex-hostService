from fastapi import APIRouter, Depends, HTTPException, Query, Path, Header
from sqlalchemy.orm import Session
from typing import List
from app.channel import channel

router = APIRouter(
    prefix="/echo",
    tags=["echo"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def echo(
    message: str = Query(..., description="要回显的消息"),
    x_user_id: str = Header(..., description="用户ID")
):
    try:
        response = await channel.single_request(x_user_id, {"message": message}, timeout=10)
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
