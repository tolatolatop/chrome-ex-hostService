from fastapi import FastAPI
from app.routes import chat, token
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
app.include_router(chat.router)
app.include_router(token.router)
