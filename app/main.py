from fastapi import FastAPI
from app.routes import chat, token, school
from app.models.init_db import init_db
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler('app.log')  # 输出到文件
    ]
)

# 创建logger
logger = logging.getLogger(__name__)
logger.debug("应用启动")

app = FastAPI()

# 初始化数据库
init_db()

app.include_router(chat.router)
app.include_router(token.router)
app.include_router(school.router)
