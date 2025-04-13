import os
from typing import Optional
import logging

# 数据库配置
DEFAULT_DATABASE_URL = "sqlite:///:memory:"
SQL_URI: str = os.getenv("SQL_URI", DEFAULT_DATABASE_URL)

# 数据库连接参数


def get_db_connect_args() -> dict:
    if SQL_URI.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


# 日志配置
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'app.log'

# 日志处理器配置
LOG_HANDLERS = [
    logging.StreamHandler(),  # 输出到控制台
    logging.FileHandler(LOG_FILE)  # 输出到文件
]


# HOST
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", 8000)
