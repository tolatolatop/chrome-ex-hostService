from fastapi import FastAPI
from app.routes import school
from app.models.init_db import init_db
from app.logs import setup_logging, get_logger

# 配置日志
setup_logging()
logger = get_logger(__name__)
logger.debug("应用启动")

app = FastAPI()

# 初始化数据库
init_db()

app.include_router(school.router)
