from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.models import Server

from app.routes import school
from app.routes import client
from app.routes import echo
from app.routes import baidu
from app.models.init_db import init_db
from app.logs import setup_logging, get_logger
from asyncio import TimeoutError
from . import settings
# 配置日志
setup_logging()
logger = get_logger(__name__)
logger.debug("应用启动")

app = FastAPI(
    title="RPC服务",
    description="RPC服务",
    version="0.1.0",
    servers=[
        {
            "url": f"http://{settings.HOST}:{settings.PORT}",
            "description": "RPC服务"
        },
        {
            "url": f"http://localhost:{settings.PORT}",
            "description": "RPC服务"
        }
    ]
)

# 初始化数据库
init_db()

app.include_router(school.router)
app.include_router(client.router)
app.include_router(echo.router)
app.include_router(baidu.router)


@app.exception_handler(TimeoutError)
async def timeout_exception_handler(request: Request, exc: TimeoutError):
    return JSONResponse(
        status_code=408,
        content={"detail": "Request timeout: No response received from client"}
    )
